FROM python:3.7-alpine

LABEL author="ZegWe"

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
WORKDIR /opt/bot/

ENTRYPOINT ["python", "app.py", "-c", "./config.json"]