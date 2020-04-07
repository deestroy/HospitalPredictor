FROM python:3.8

COPY . /app
WORKDIR / app

RUN pip3 install -r requirements.txt

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app