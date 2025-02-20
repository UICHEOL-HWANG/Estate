import os
import pandas as pd
import psycopg2
import numpy as np
import xgboost as xgb
import mlflow
from pycaret.regression import *
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split

os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL", "http://mlflow-artifact-store:9000")
os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000")
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")

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

        # 로그 변환된 타겟 변수 추가 (컬럼명: 'target')
        df_scaled["target"] = df[self.y_target].values
        print("✅ 데이터 전처리 및 스케일링 완료!")
        return df_scaled


class Automation:
    """PyCaret AutoML 클래스"""

    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.results_df = None

    def train_pycaret(self):
        """PyCaret AutoML 실행"""
        df = self.preprocessor.fetch_data_from_db()
        # preprocess_and_scale() 내에서 전처리와 스케일링을 모두 처리하고 'target'으로 컬럼명을 변경
        df_scaled = self.preprocessor.preprocess_and_scale(df)

        mlflow.set_experiment("pycaret_automl")
        print("📊 PyCaret AutoML 모델 훈련 시작...")

        with mlflow.start_run():
            setup(data=df_scaled, target="target", log_experiment=True, experiment_name="pycaret_automl", verbose=False)
            best_model = compare_models()
            self.results_df = pull()

            for _, row in self.results_df.iterrows():
                mlflow.log_param("model_name", row["Model"])
                mlflow.log_metric("mae", row["MAE"])
                mlflow.log_metric("r2", row["R2"])
                mlflow.log_metric("rmse", row["RMSE"])

    def get_results(self):
        """PyCaret 결과 반환"""
        if self.results_df is None:
            raise ValueError("🚨 모델 학습이 완료되지 않았습니다!")
        return self.results_df



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

class MetricSave:
    """모델 평가 결과 DB 저장"""

    def __init__(self):
        self.conn = psycopg2.connect(
            user=os.getenv("TRAIN_USER"),
            password=os.getenv("TRAIN_PASSWORD"),
            host=os.getenv("TRAIN_HOST"),
            database=os.getenv("TRAIN_DB")
        )
        self.cursor = self.conn.cursor()

    def save_results(self, results_df):
        """PyCaret 평가 결과 DB 저장"""
        for _, row in results_df.iterrows():
            self.cursor.execute(
                "INSERT INTO model_results (model_name, mae, r2, rmse) VALUES (%s, %s, %s, %s);",
                (row["Model"], row["MAE"], row["R2"], row["RMSE"])
            )
        self.conn.commit()

    def close_connection(self):
        """DB 연결 종료"""
        self.cursor.close()
        self.conn.close()
