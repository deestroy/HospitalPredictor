FROM python:3.7

COPY . /app
WORKDIR /app

RUN pip3 install flask python-dotenv firebase_admin

ENTRYPOINT ["python3"]
CMD ["app.py"]
