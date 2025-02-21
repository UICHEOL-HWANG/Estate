import os
import pandas as pd
import psycopg2
import numpy as np
import xgboost as xgb

from functools import partial
import optuna

from sklearn.metrics import mean_squared_error
import pickle

import boto3
from botocore.client import Config

import mlflow
from pycaret.regression import *
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split

os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://mlflow-artifact-store:9000")
os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")


def save_scaler_to_minio(scaler, bucket_name, object_name):
    """
    학습된 scaler 객체를 pickle로 저장하고, MinIO에 업로드하는 함수.
    bucket_name: 업로드할 버킷 이름 (예: "mlflow")
    object_name: 저장할 파일명 (예: "scaler.pkl")
    """
    # scaler 객체를 파일로 저장
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    # boto3 클라이언트 생성 (MinIO)
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("MLFLOW_S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4"),
        region_name="us-east-1"
    )

    # 파일 업로드
    s3.upload_file("scaler.pkl", bucket_name, object_name)
    print(f"Scaler 저장 완료: {bucket_name}/{object_name}")


class Preprocessor:
    """데이터 전처리 클래스"""

    def __init__(self):
        self.X_features = ["층", "법정동코드", "건축년도", "건물면적_㎡"]
        self.y_target = "물건금액_만원"
        self.scaler = RobustScaler()

    def fetch_data_from_db(self):
        """DB에서 데이터 불러오기"""
        print("📊 데이터베이스에서 데이터 불러오는 중...")

        query = "SELECT * FROM estate_details;"

        with psycopg2.connect(
                user=os.getenv("TRAIN_USER"),
                password=os.getenv("TRAIN_PASSWORD"),
                host=os.getenv("TRAIN_HOST"),
                database=os.getenv("TRAIN_DB"),
                port=5432
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                records = cursor.fetchall()

                # ✅ DataFrame 변환
                df = pd.DataFrame(records, columns=[desc[0] for desc in cursor.description])

        if df.empty:
            raise ValueError("🚨 데이터베이스에서 불러온 데이터가 없습니다!")

        print(f"✅ 데이터 로드 완료! {df.shape[0]}개의 데이터")
        return df

    def preprocess_and_scale(self, df):
        """
        데이터 전처리 및 스케일링:
          - 불필요한 컬럼 제거
          - 필요한 컬럼 선택
          - 결측치 처리
          - 타겟 변수 로그 변환 (np.log1p)
          - 독립 변수에 RobustScaler 적용
          - 스케일링된 독립 변수와 로그 변환된 타겟을 하나의 DataFrame으로 반환 (타겟 컬럼명: 'target')
        """
        print("🔄 데이터 전처리 및 스케일링 중...")
        # 불필요한 컬럼 제거 및 필요한 컬럼 선택
        df = df.drop(columns=["id", "estate_id"], errors="ignore")
        df = df[self.X_features + [self.y_target]]

        # 결측치 처리
        df.fillna(df.median(), inplace=True)

        # 타겟 변수 로그 변환 (np.log1p)
        df[self.y_target] = np.log1p(df[self.y_target])

        # 독립 변수 스케일링 (RobustScaler)
        X_scaled = self.scaler.fit_transform(df[self.X_features])
        df_scaled = pd.DataFrame(X_scaled, columns=self.X_features)
        save_scaler_to_minio(self.scaler, bucket_name="mlflow", object_name="scaler.pkl")

        # 로그 변환된 타겟 변수 추가 (컬럼명: 'target')
        df_scaled["target"] = df[self.y_target].values
        print("✅ 데이터 전처리 및 스케일링 완료!")
        return df_scaled


class Automation:
    """PyCaret AutoML 및 DB 저장 클래스"""

    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.results_df = None
        # DB 연결 설정 (필요한 경우 여기서 미리 연결하거나, 저장 시점에 생성)
        self.conn = psycopg2.connect(
            user=os.getenv("TRAIN_USER"),
            password=os.getenv("TRAIN_PASSWORD"),
            host=os.getenv("TRAIN_HOST"),
            database=os.getenv("TRAIN_DB")
        )
        self.cursor = self.conn.cursor()

    def train_pycaret(self):
        """PyCaret AutoML 실행 및 결과 DB 저장"""
        df = self.preprocessor.fetch_data_from_db()
        df_scaled = self.preprocessor.preprocess_and_scale(df)

        mlflow.set_experiment("pycaret_automl")
        print("📊 PyCaret AutoML 모델 훈련 시작...")

        with mlflow.start_run():
            setup(data=df_scaled, target="target", log_experiment=True, experiment_name="pycaret_automl", verbose=False)
            best_model = compare_models()
            self.results_df = pull()

            unique_model_names = ", ".join(self.results_df["Model"].unique())
            mlflow.log_param("model_name", unique_model_names)

            for _, row in self.results_df.iterrows():
                mlflow.log_metric("mae", row["MAE"])
                mlflow.log_metric("r2", row["R2"])
                mlflow.log_metric("rmse", row["RMSE"])

        # 학습 결과 DB에 저장
        self.save_results_to_db()

        # DB 연결 종료 (원한다면 여기서 종료하거나, 별도로 관리)
        self.cursor.close()
        self.conn.close()

        return self.results_df

    def save_results_to_db(self):
        """PyCaret 평가 결과를 DB에 저장"""
        if self.results_df is None:
            raise ValueError("🚨 모델 학습이 완료되지 않았습니다!")
        for _, row in self.results_df.iterrows():
            self.cursor.execute(
                "INSERT INTO model_results (model_name, mae, r2, rmse) VALUES (%s, %s, %s, %s);",
                (row["Model"], row["MAE"], row["R2"], row["RMSE"])
            )
        self.conn.commit()
        print("✅ DB에 결과 저장 완료!")


class EstatePredict:
    """XGBoost 모델 (Optuna 생략한 예시)"""

    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.best_params = {
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 1.0,
            "colsample_bytree": 1.0
        }
        self.model = xgb.XGBRegressor(**self.best_params, random_state=42)

    def fit(self):
        """XGBoost 모델 학습 및 MLflow 로깅"""
        print("📊 XGBoost 모델 학습 시작...")
        print("훈련중...")  # 진행 메시지 출력

        # 데이터 로드 및 전처리 + 스케일링 (단일 DataFrame 반환)
        df = self.preprocessor.fetch_data_from_db()
        df_scaled = self.preprocessor.preprocess_and_scale(df)

        # train/test split (예: 80:20 비율)
        X = df_scaled[self.preprocessor.X_features]
        y = df_scaled["target"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # MLflow 실험 설정
        mlflow.set_experiment("xgboost_optuna")
        with mlflow.start_run():
            mlflow.log_params(self.best_params)

            # 모델 학습
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=True
            )

            # 모델 성능 평가
            y_pred = self.model.predict(X_test)
            mae = np.mean(np.abs(y_test - y_pred))
            rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
            r2 = 1 - (np.sum((y_test - y_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))

            mlflow.log_metric("mae", mae)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            mlflow.xgboost.log_model(self.model, artifact_path="xgboost_model")

            print(f"✅ MLflow에 모델 저장 완료! (MAE: {mae:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f})")





# class EstatePredict:
#     """XGBoost 모델 (Optuna 하이퍼파라미터 튜닝 포함)"""
#
#     def __init__(self, preprocessor):
#         self.preprocessor = preprocessor
#         self.best_params = None
#         self.model = None
#
#     def fit(self):
#         """Optuna를 통한 최적 하이퍼파라미터 탐색 후 모델 학습 및 MLflow 로깅"""
#         print("📊 XGBoost 모델 학습 시작...")
#         print("훈련중...")
#
#         # 데이터 로드 및 전처리 + 스케일링 (단일 DataFrame 반환)
#         df = self.preprocessor.fetch_data_from_db()
#         df_scaled = self.preprocessor.preprocess_and_scale(df)
#
#         # train/test split (예: 80:20 비율)
#         X = df_scaled[self.preprocessor.X_features]
#         y = df_scaled["target"]
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
#         # objective 함수 정의 (별도의 함수로 분리 가능)
#         def objective(trial, X_train, y_train, X_test, y_test):
#             params = {
#                 "n_estimators": trial.suggest_int("n_estimators", 50, 500),
#                 "max_depth": trial.suggest_int("max_depth", 3, 20),
#                 "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
#                 "subsample": trial.suggest_float("subsample", 0.5, 1.0),
#                 "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
#                 "random_state": 42,
#                 "n_jobs": -1
#             }
#             model = xgb.XGBRegressor(**params)
#             model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
#             y_pred = model.predict(X_test)
#             rmse = np.sqrt(mean_squared_error(y_test, y_pred))
#             return rmse
#
#         # partial을 사용하여 objective 함수에 데이터 전달
#
#         objective_func = partial(objective, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test)
#         study = optuna.create_study(direction="minimize")
#         study.optimize(objective_func, n_trials=50)
#         print("Optuna 최적 파라미터:", study.best_params)
#         self.best_params = study.best_params
#
#         # 최적 파라미터로 최종 모델 생성 및 학습
#         self.model = xgb.XGBRegressor(**self.best_params, random_state=42, n_jobs=-1)
#         mlflow.set_experiment("xgboost_optuna")
#         with mlflow.start_run():
#             mlflow.log_params(self.best_params)
#             self.model.fit(
#                 X_train, y_train,
#                 eval_set=[(X_test, y_test)],
#                 verbose=True,
#             )
#
#             y_pred = self.model.predict(X_test)
#             mae = np.mean(np.abs(y_test - y_pred))
#             rmse = np.sqrt(mean_squared_error(y_test, y_pred))
#             r2 = 1 - (np.sum((y_test - y_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))
#
#             mlflow.log_metric("mae", mae)
#             mlflow.log_metric("rmse", rmse)
#             mlflow.log_metric("r2", r2)
#             mlflow.xgboost.log_model(self.model, artifact_path="xgboost_model_optuna")
#
#             print(f"✅ MLflow에 모델 저장 완료! (MAE: {mae:.4f}, RMSE: {rmse:.4f}, R²: {r2:.4f})")