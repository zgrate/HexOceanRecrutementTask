FROM python:3.9-alpine

ENV PYTHONBUFFERED 1

COPY . .

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]