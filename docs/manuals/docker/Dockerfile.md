```
FROM python:3.9 as taipy

# Web port of the application
EXPOSE 5000

# Install your application
WORKDIR /opt/airflow
COPY . .
RUN pip install -r requirements.txt
RUN pip install pip install 'apache-airflow==2.2.3' \
 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.3/constraints-3.9.txt"

RUN mkdir -p /app/data && chmod -R 777 /app/data

RUN useradd -ms /bin/bash airflow
USER airflow

CMD python demo_cli.py



FROM apache/airflow:latest-python3.9 as airflow

USER root
RUN apt update -y
RUN apt install -y git

USER airflow

COPY . .
RUN pip install -r requirements.txt
RUN pip install --upgrade numpy

ENV PYTHONPATH=/opt/airflow
```
