FROM python:slim
MAINTAINER jensoft <jen.soft.maser@gmail.ru>

RUN apt-get update
RUN apt-get install -y gcc libpq5 git
RUN apt-get install -y libpq-dev
RUN pip install --upgrade pip

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt
