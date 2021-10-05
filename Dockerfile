FROM python:rc-alpine

WORKDIR /application
COPY requirements.txt /application

RUN apk update && apk add curl
RUN pip3 install -r requirements.txt

COPY app /application/app

HEALTHCHECK --interval=900s --timeout=2s --start-period=30s \  
    CMD curl -I http://127.0.0.1:5000 || echo 1

ENTRYPOINT [ "python3", "app/app.py" ]
