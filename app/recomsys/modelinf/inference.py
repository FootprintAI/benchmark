from sklearn.neighbors import NearestNeighbors
"""
Find similar movies using KNN
"""
def find_similar_movies(query_feature, model, metric='cosine', show_distance=False):
    distances,suggestions=model.kneighbors(query_feature.reshape(1,-1))
    return suggestions
