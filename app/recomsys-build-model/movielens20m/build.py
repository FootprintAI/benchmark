# reference
# [1] https://www.kaggle.com/code/anmol4210/recommendation-system-content-based
# [2] https://www.kaggle.com/code/sankha1998/collaborative-movie-recommendation-system
import os
import numpy as np
import pandas as pd
import time

def collaborative_filtering(folder_path):
    # load 20M rating file
    rating_df = load_rating_df(folder_path)
    #print(rating_df.shape)
    ## (20000263, 3)

    # filtering by per user rating, rating counts for each user should be greater
    # than 30
    rating_df = filtering_rating_by_item_rated_count(rating_df, 30)

    # filtering by per item rated, rated counts for each item should be greater
    # than 30
    rating_df = filtering_rating_by_user_rated_count(rating_df, 30)

    #print("---purged rating df---")
    #print(rating_df.shape)
    # (19287084, 3)

    # load all movies info
    movies_df = load_movie_df(folder_path)
    #print("--movies_df--")
    #print(movies_df.shape)
    # (27278, 3)

    movie_details= grouping_rating_movie_by_movieid(rating_df, movies_df)
    #print("---movie_details.shape")
    #print(movie_details.shape)
    # (19287084, 5)

    # this requires N by M matrix
    movie_pivot=movie_details.pivot_table(columns='userId',index='title',values='rating')
    movie_pivot.fillna(0,inplace=True)
    #print("--pivot table--")
    #print(movie_pivot.shape)
    # (12011, 112467)

    from scipy.sparse import csr_matrix
    movie_sparse=csr_matrix(movie_pivot)

    from sklearn.neighbors import NearestNeighbors
    model=NearestNeighbors( n_neighbors=7,algorithm='brute',metric='cosine')
    model.fit(movie_sparse)

    (samples, dims) = movie_pivot.shape
    print("dim:{}, samples:{}".format(dims, samples))
    # dim:112467, samples:12011

    # save model for later usage
    save_model({"dims": dims, "model": model}, "movielens20m.model.pkl")

    # reload it back for testing
    reloaded = load_model("movielens20m.model.pkl")

    movie_id = 540
    ramdon_feature = random_item_feature(dims)

    start = time.time()
    distances,suggestions=reloaded["model"].kneighbors(movie_pivot.iloc[movie_id,:].values.reshape(1,-1))
    print(distances)
    # [[0.         0.48257652 0.50935053 0.53108546 0.58302479 0.61280573                           │      es.reshape(1,-1))$
    # 0.77887124]]
    print(suggestions)
    # [[ 540  541  536  534  539  535 2114]]

    distances,suggestions=reloaded["model"].kneighbors(ramdon_feature.reshape(1,-1))

    print(distances)
    # [[0.40316643 0.40556802 0.41760994 0.41926286 0.43499672 0.45725176
    # 0.46246327]]
    print(suggestions)
    # [[ 8590  3954  9640  9530  5809 10058  1601]]
    print("cost: {}".format(time.time() - start))
    # cost: 1.2365801334381104

def random_item_feature(dims: int):
    import random
    features = []
    for i in range (dims):
        features.append(random.randint(0,5))
    return np.array(features)


#def content_based_filtering(folder_path):
#    rating_df = load_rating_df(folder_path)
#    movies_df = load_movie_df(folder_path)
#    moviesWithGenres_df, genreTable = convert_movie_df_to_genre_matrix(movies_df)
#
#    inputMovies = load_user_rating_inputs()
#    userProfile = load_user_profile_from_user_inputs(inputMovies, moviesWithGenres_df)
#    recommendationTable_df = ((genreTable*userProfile).sum(axis=1))/(userProfile.sum())
#    movies_df.loc[movies_df['movieId'].isin(recommendationTable_df.head(20).keys())]

#def load_user_profile_from_user_inputs(inputMovies, moviesWithGenres_df):
#    userMovies = moviesWithGenres_df[moviesWithGenres_df['movieId'].isin(inputMovies['movieId'].tolist())]
#    userMovies = userMovies.reset_index(drop=True)
#    #Dropping unnecessary issues due to save memory and to avoid issues
#    userGenreTable = userMovies.drop('movieId', axis=1).drop('title', axis=1).drop('genres', axis=1).drop('year', axis=1)
#
#    userProfile = userGenreTable.transpose().dot(inputMovies['rating'])
#
#    return userProfile
#
#
#def load_user_rating_inputs():
#    userInput = [
#            {'movieId': 1, 'title':'Breakfast Club, The', 'rating':5},
#            {'movieId': 2, 'title':'Toy Story', 'rating':3.5},
#            {'movieId': 296, 'title':'Jumanji', 'rating':2},
#            {'movieId': 1274, 'title':"Pulp Fiction", 'rating':5},
#            {'movieId': 1968, 'title':'Akira', 'rating':4.5}
#         ]
#    inputMovies = pd.DataFrame(userInput)
#    return inputMovies

def load_rating_df(folder_path: str):
    rating_path = os.path.join(folder_path, "rating.csv")
    ratings_df = pd.read_csv(rating_path)

    #Drop removes a specified row or column from a dataframe
    ratings_df = ratings_df.drop('timestamp', axis=1)

    return ratings_df

def filtering_rating_by_user_rated_count(rating_df, rated_count_per_user):
    number_rating = rating_df.groupby('userId')['rating'].count().reset_index()
    number_rating.rename(columns={'rating':'number of rating'},inplace=True)

    df=rating_df.merge(number_rating,on='userId')
    df=df[df['number of rating']>= rated_count_per_user] #selecting valuable books by ratings
    df.drop(columns=['number of rating'],inplace=True)
    df['rating']=df['rating'].astype(int)
    #print('user rated')
    #print(df.shape)
    # (19287084, 3)
    return df


def filtering_rating_by_item_rated_count(rating_df, rated_count_per_item):
    number_rating = rating_df.groupby('movieId')['rating'].count().reset_index()
    number_rating.rename(columns={'rating':'number of rating'},inplace=True)

    df=rating_df.merge(number_rating,on='movieId')
    df=df[df['number of rating']>= rated_count_per_item] #selecting valuable books by ratings
    df.drop(columns=['number of rating'],inplace=True)
    df['rating']=df['rating'].astype(int)
    return df


def load_movie_df(folder_path: str):
    movie_path = os.path.join(folder_path, "movie.csv")
    movies_df = pd.read_csv(movie_path)

    return movies_df

def grouping_rating_movie_by_movieid(rating_df, movies_df):
    copy_rating_df = rating_df.copy()
    copy_rating_df.set_index("movieId")

    copy_movies_df = movies_df.copy()
    copy_movies_df.set_index("movieId")
    movie_details=copy_movies_df.merge(copy_rating_df,on='movieId')
    #print(movie_details.head())

    return movie_details

def save_model(model, model_path):
    import pickle

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

def load_model(model_path):
    import pickle
    return pickle.load(open(model_path, "rb"))

#def convert_movie_df_to_genre_matrix(movies_df):
#    movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand=False)
#    #Removing the parentheses
#    movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand=False)
#    #Removing the years from the 'title' column
#    movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))', '')
#    #Applying the strip function to get rid of any ending whitespace characters that may have appeared
#    movies_df['title'] = movies_df['title'].apply(lambda x: x.strip())
#    #movies_df.head()
#
#    movies_df['genres'] = movies_df.genres.str.split('|')
#
#    # convert with one-hot matrix for generes
#    moviesWithGenres_df = movies_df.copy()
#
#    #For every row in the dataframe, iterate through the list of genres and place a 1 into the corresponding column
#    for index, row in movies_df.iterrows():
#        for genre in row['genres']:
#            moviesWithGenres_df.at[index, genre] = 1
#    #Filling in the NaN values with 0 to show that a movie doesn't have that column's genre
#    moviesWithGenres_df = moviesWithGenres_df.fillna(0)
#    moviesWithGenres_df.head()
#
#
#    #Now let's get the genres of every movie in our original dataframe
#    genreTable = moviesWithGenres_df.set_index(moviesWithGenres_df['movieId'])
#    #And drop the unnecessary information
#    genreTable = genreTable.drop('movieId', axis=1).drop('title', axis=1).drop('genres', axis=1).drop('year', axis=1)
#    #genreTable.head()
#
#
#    return moviesWithGenres_df, genreTable


def main():
    import os

    folder_path = os.environ.get("KAGGLE_RECOMMENDATION_MOVIELEN20M")
    print("loading data from path:{}".format(folder_path))
    collaborative_filtering(folder_path)

if __name__ == "__main__":
    main()


