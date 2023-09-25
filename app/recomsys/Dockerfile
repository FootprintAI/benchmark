FROM python:3.9

RUN apt-get update

COPY . .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r modelinf/requirements.txt

ENTRYPOINT ["python"]
