FROM python:3.9-alpine

ENV PYTHONBUFFERED 1

RUN apt-get update && apt-get install

RUN apt-get install -y python-psycopg2

WORKDIR /django_backend

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

