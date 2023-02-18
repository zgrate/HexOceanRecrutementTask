FROM python:3.9-alpine

ENV PYTHONBUFFERED 1

WORKDIR /django_backend

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

