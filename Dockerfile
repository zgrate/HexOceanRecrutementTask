FROM python:3.9

ENV PYTHONBUFFERED 1


RUN apt-get update

RUN apt-get install -y python3-psycopg2

WORKDIR /django_backend

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

COPY start_server.sh ./
