FROM python:3.10-slim as base
COPY requirements.txt ./requirements.txt
# RUN apk --no-cache add gcc n && pip install --no-cache-dir -r requirements.txt && apk del gcc
RUN pip install --no-cache-dir -r requirements.txt 
COPY . ./
CMD gunicorn --forwarded-allow-ips='*' app:app -b :8000
