import os
import pickle
import tempfile
import mlflow
import pandas as pd
import boto3
from botocore.client import Config

# 모델 학습 시 사용한 feature 순서 (Preprocessor와 동일)
FEATURES = ["층", "법정동코드", "건축년도", "건물면적_㎡"]

os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://mlflow-artifact-store:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "mastermino"
os.environ["AWS_SECRET_ACCESS_KEY"] = "master1234!"
os.environ["MLFLOW_TRACKING_URI"] = "http://mlflow-server:5000"

def load_scaler_from_minio(bucket_name: str, object_name: str):
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4"),
        region_name="us-east-1"
    )
    # 임시 파일 경로 생성
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, "temp_scaler.pkl")

    # S3에서 임시 파일로 다운로드
    s3.download_file(bucket_name, object_name, tmp_path)

    # 파일 열어서 pickle 로드
    with open(tmp_path, "rb") as f:
        scaler = pickle.load(f)

    # 필요에 따라 임시 파일 삭제 (자동 삭제되지 않으므로)
    os.remove(tmp_path)

    return scaler


def load_func(data):
    """
    data: 예측에 사용할 데이터. 예를 들어, 리스트의 리스트 또는 dict 형식.
    예: [[3, 110101, 2005, 85.0]]

    저장된 scaler를 통해 입력 데이터를 스케일링한 후 MLflow에 저장된 모델로 예측합니다.
    """
    # MLflow 모델 URI (실제 모델 URI에 맞게 수정)
    logged_model = 'runs:/e4e30f12c37345c3ae85c32aee811462/xgboost_model'
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # 입력 데이터를 DataFrame으로 변환 (컬럼명은 FEATURES 순서와 일치해야 함)
    df = pd.DataFrame(data, columns=FEATURES)

    # MinIO에서 저장된 scaler 객체 로드 (예: bucket "mlflow", 객체 "scaler.pkl")
    scaler = load_scaler_from_minio(bucket_name="mlflow", object_name="scaler.pkl")

    # scaler를 사용하여 입력 데이터 스케일링
    df_scaled = pd.DataFrame(scaler.transform(df), columns=FEATURES)

    # 스케일링된 데이터로 예측 수행
    predictions = loaded_model.predict(df_scaled)

    return predictions
