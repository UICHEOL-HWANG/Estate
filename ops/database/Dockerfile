FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/app

RUN pip install -U pip &&\
    pip install pandas psycopg2-binary

COPY table_creator.py .

ENTRYPOINT ["python", "table_creator.py"]

