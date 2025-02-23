#!/bin/bash

set -e

echo "Creating multiple PostgreSQL databases: $POSTGRES_MULTIPLE_DATABASES"

# 쉼표(,)로 구분된 데이터베이스 목록을 하나씩 처리
for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
    echo "Creating database: $db"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
        CREATE DATABASE $db;
        GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
done
