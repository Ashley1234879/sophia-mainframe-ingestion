FROM python:3.7.0-slim

ENV http_proxy=http://proxy.int.sharedsvc.a-sharedinfra.net:8080/
ENV https_proxy=http://proxy.int.sharedsvc.a-sharedinfra.net:8080/

# Install software
RUN apt-get update && apt-get install -y git
RUN apt-get install -y vim
RUN apt-get install -y gcc

WORKDIR /projects/app

COPY ./etl_scripts /projects/app/etl_scripts
COPY ./airflow_src /projects/app/airflow_src

WORKDIR /projects/app/airflow_src

ENV PYTHONPATH="/projects"

RUN pip install -r requirements.txt