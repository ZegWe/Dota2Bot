FROM python:3.7-alpine

LABEL author="ZegWe"

RUN pip install requests
WORKDIR /opt/dota2bot/
COPY . .
COPY config.example.json config.json
ENTRYPOINT ["python", "run.py", "-c", "./config.json"]