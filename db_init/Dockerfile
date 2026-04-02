FROM python:3.10.13-alpine3.19

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python", "db_init.py"]