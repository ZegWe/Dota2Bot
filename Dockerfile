FROM python:3.7-alpine

LABEL author="ZegWe"
LABEL version="0.2.0"

RUN pip install requests
COPY . .
COPY config.example.json config.json
ENTRYPOINT ["python", "run.py", "-c", "./config.json"]