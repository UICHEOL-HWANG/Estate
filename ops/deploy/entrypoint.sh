#!/bin/bash

echo "🚀 Airflow 환경 초기화 시작..."

# ✅ Airflow DB 초기화 (최초 실행 시 필요)
airflow db init

# ✅ Airflow 마스터 계정이 이미 존재하는지 확인 후 생성
if ! airflow users list | grep -q "admin"; then
    echo "🛠️ Admin 사용자 생성 중..."
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin
else
    echo "✅ Admin 사용자가 이미 존재합니다."
fi

# ✅ CeleryExecutor 실행 (Scheduler, Worker, Webserver)
if [[ "$AIRFLOW__CORE__EXECUTOR" == "CeleryExecutor" ]]; then
    echo "🚀 CeleryExecutor 감지됨 - Scheduler 및 Worker 실행"
    airflow scheduler & airflow celery worker &
fi

# ✅ Airflow 웹 서버 실행
echo "🌍 Airflow 웹 서버 실행 중..."
exec airflow webserver
