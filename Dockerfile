FROM python:3.10.0-alpine

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt

RUN python -m pip install --upgrade pip
# RUN pip install umap-learn bechdelai==0.0.1a2

# RUN pip install /requirements.txt

RUN pip install Django
RUN pip install djangorestframework
RUN pip install flake8

RUN mkdir /app
WORKDIR /app 
COPY ./app /app
RUN adduser -D user
USER user

