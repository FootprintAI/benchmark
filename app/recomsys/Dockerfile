FROM python:3.9

RUN apt-get update

WORKDIR /app/recomsys 

COPY app/recomsys /app/recomsys
COPY app/recomsys-build-model/movielens20m/movielens20m.model.pkl.tar.gz /app/recomsys/modelinf
RUN cd /app/recomsys/modelinf && tar xzvf movielens20m.model.pkl.tar.gz

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/recomsys/modelinf/requirements.txt
RUN pip install --no-cache-dir -r /app/recomsys/userresource/requirements.txt

ENTRYPOINT ["python"]
