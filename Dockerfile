FROM python:3.7-slim

COPY . /app
WORKDIR /app/src

RUN pip3 install -r requirements.txt 

EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
