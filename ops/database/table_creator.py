import psycopg2
import os

class TableCreator:
    def __init__(self):
        """DB 연결 설정"""
        try:
            self.conn = psycopg2.connect(
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                database=os.getenv("POSTGRES_DB")
            )
            self.cursor = self.conn.cursor()
            print("🔗 DB 연결 성공!")
        except Exception as e:
            print(f"🚨 DB 연결 실패: {e}")
            raise

    def create_tables(self):
        """DB 테이블 생성 (중복 생성 방지)"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS estate (
                id SERIAL PRIMARY KEY,
                접수연도 INT NOT NULL,
                자치구코드 INT NOT NULL,
                자치구명 VARCHAR(255) NOT NULL,
                법정동코드 INT NOT NULL,
                법정동명 VARCHAR(255) NOT NULL,
                지번구분 FLOAT,
                지번구분명 VARCHAR(255),
                본번 FLOAT,
                부번 FLOAT,
                건물명 VARCHAR(255),
                계약일 INT NOT NULL,
                물건금액_만원 INT NOT NULL,
                건물면적_㎡ FLOAT,
                토지면적_㎡ FLOAT,
                층 FLOAT,
                권리구분 VARCHAR(255),
                건축년도 FLOAT,
                건물용도 VARCHAR(255),
                신고구분 VARCHAR(255)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS estate_details (
                id SERIAL PRIMARY KEY,
                estate_id INT NOT NULL,
                본번 FLOAT,
                층 FLOAT,
                물건금액_만원 INT NOT NULL,
                법정동코드 INT NOT NULL,
                건축년도 FLOAT,
                건물면적_㎡ FLOAT,
                FOREIGN KEY (estate_id) REFERENCES estate(id) ON DELETE CASCADE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS model_results (
                id SERIAL PRIMARY KEY,
                model_name TEXT,
                mae FLOAT,
                r2 FLOAT,
                rmse FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS saved_models (
                id SERIAL PRIMARY KEY,
                model_name TEXT,
                model BYTEA,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]

        try:
            for query in queries:
                self.cursor.execute(query)
            self.conn.commit()
            print("✅ 테이블 생성 완료!")
        except Exception as e:
            print(f"🚨 테이블 생성 실패: {e}")
            self.conn.rollback()

    def close_connection(self):
        """DB 연결 종료"""
        self.cursor.close()
        self.conn.close()
        print("🔌 DB 연결 종료!")

if __name__ == "__main__":
    db_manager = TableCreator()
    db_manager.create_tables()
    db_manager.close_connection()
