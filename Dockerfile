FROM python:3.9-alpine

LABEL author="ZegWe"

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
WORKDIR /opt/bot/
COPY . .
ENTRYPOINT ["python", "app.py", "-c", "./config.json"]