FROM python:3.10.13-alpine3.19

RUN apk update && apk add "imagemagick=7.1.1.32-r0"

WORKDIR /app

COPY . .

COPY requirements.txt .

RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED="true"

ENTRYPOINT ["flask", "--app", "main", "run", "-h", "0.0.0.0", "-p", "5000"]