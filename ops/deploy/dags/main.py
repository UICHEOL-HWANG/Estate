from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.ml_pipeline import Preprocessor, Automation, EstatePredict, save_scaler_to_minio

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 2, 22),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="estate_prediction_pipeline",
    default_args=default_args,
    description="부동산 가격 예측 (PyCaret + XGBoost)",
    schedule_interval="@daily",
    catchup=False
) as dag:

    # 객체 초기화
    preprocessor = Preprocessor()
    automl = Automation(preprocessor)
    predictor = EstatePredict(preprocessor)

    # ✅ 데이터 가져오기
    fetch_data_task = PythonOperator(
        task_id="fetch_data",
        python_callable=preprocessor.fetch_data_from_db
    )

    # ✅ 데이터 전처리 및 스케일링 (타겟 변수는 preprocess_and_scale()에서 np.log1p 적용)
    preprocess_task = PythonOperator(
        task_id="preprocess_data",
        python_callable=lambda: preprocessor.preprocess_and_scale(preprocessor.fetch_data_from_db())
    )

    train_pycaret_task = PythonOperator(
        task_id="train_pycaret",
        python_callable=automl.train_pycaret
    )



    # ✅ XGBoost 학습
    train_xgboost_task = PythonOperator(
        task_id="train_xgboost",
        python_callable=predictor.fit,
        dag=dag
    )

    #
    # # ✅ XGBoost (Optuna 포함) 학습
    # train_xgboost_task = PythonOperator(
    #     task_id="train_xgboost",
    #     python_callable=predictor.fit
    # )




    # ✅ DAG 실행 순서 수정 (스케일링 후 모델 학습)
    fetch_data_task >> preprocess_task  >> [train_pycaret_task, train_xgboost_task]



    # # ✅ DAG 실행 순서 설정:
    # # fetch_data_task -> preprocess_task -> [train_pycaret_task, train_xgboost_task] -> (PyCaret 결과 저장)
    # fetch_data_task >> preprocess_task >> [train_pycaret_task, train_xgboost_task]
    # train_pycaret_task >> save_pycaret_results_task
