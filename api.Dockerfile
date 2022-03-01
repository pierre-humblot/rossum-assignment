FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

# for building psycopg2
RUN apt-get update
RUN apt-get -y install libpq-dev gcc

COPY requirements.txt /api/requirements.txt
WORKDIR /api
COPY ./pdf_rendering_service /api
RUN pip3 install -r requirements.txt

EXPOSE 8000

