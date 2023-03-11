FROM python:3.10-slim as base
COPY requirements.txt ./requirements.txt
# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True
# RUN apk --no-cache add gcc n && pip install --no-cache-dir -r requirements.txt && apk del gcc
RUN pip install --no-cache-dir -r requirements.txt 
COPY . ./
CMD gunicorn --workers 1 --threads 1 --workers 3 app:app -b :8080
