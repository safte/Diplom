FROM python:rc-alpine

WORKDIR /application
COPY requirements.txt /application

RUN apk update && apk add curl && pip3 install -r requirements.txt

COPY app /application/app

ENTRYPOINT [ "python3", "app/app.py" ]
