import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv


def get_env():
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)

def get_data():
    data = pd.read_csv("C:/Users/user/Desktop/Estate/hub/workdir/data/cleaned_data.csv")

    # cleansing Data
    cleansing_data = data.drop("Unnamed: 0", axis=1)

    return cleansing_data


def insert_estate_data(connect, data):
    """
    estate 테이블에 데이터를 삽입하고 생성된 estate_id를 반환하는 함수
    """
    insert_query = """
    INSERT INTO estate (
        접수연도, 자치구코드, 자치구명, 법정동코드, 법정동명, 
        지번구분, 지번구분명, 본번, 부번, 건물명, 
        계약일, 물건금액_만원, 건물면적_㎡, 토지면적_㎡, 층, 
        권리구분, 건축년도, 건물용도, 신고구분
    ) VALUES (
        %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, 
        %s, %s, %s, %s
    ) RETURNING id;
    """

    estate_ids = []

    try:
        with connect.cursor() as cur:
            for row in data:
                cur.execute(insert_query, row)  # 개별 INSERT 실행
                estate_id = cur.fetchone()  # `RETURNING id` 값 가져오기
                if estate_id:
                    estate_ids.append(estate_id[0])  # 리스트에 추가

            connect.commit()
        print(f"✅ estate 테이블 데이터 삽입 완료 (총 {len(estate_ids)}개)")

        return estate_ids  # 삽입된 estate_id 리스트 반환

    except Exception as e:
        connect.rollback()
        print(f"❌ 에러 발생: {e}")
        return []


def insert_train_data(connect, estate_ids, data):
    """
    estate_details 테이블에 데이터를 삽입하는 함수
    """

    insert_query = """
    INSERT INTO estate_details (
        estate_id, 본번, 층, 법정동코드, 건축년도, 건물면적_㎡, 물건금액_만원
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s
    );
    """

    if not estate_ids:
        print("⚠️ estate_id가 없습니다. estate_details 삽입을 건너뜁니다.")
        return

    # estate_id와 매칭하여 데이터 리스트 생성
    detailed_data = [(estate_id, *row) for estate_id, row in zip(estate_ids, data)]

    try:
        with connect.cursor() as cur:
            cur.executemany(insert_query, detailed_data)  # 배치 삽입
            connect.commit()
        print("✅ estate_details 테이블 데이터 삽입 완료")

    except Exception as e:
        connect.rollback()
        print(f"❌ 에러 발생: {e}")


if __name__ == "__main__":
    get_env()

    # DB 연결
    db_connect = psycopg2.connect(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port=int(os.getenv("POSTGRES_PORT", 5433)),  # 기본값 5432
        database=os.getenv("POSTGRES_DB")
    )

    # 데이터 로드
    df = get_data()

    # estate 테이블에 삽입할 데이터 (19개 컬럼)
    estate_data = df.iloc[:, :19].values.tolist()

    if not estate_data:
        print("⚠️ estate_data가 비어 있습니다. 데이터 삽입을 건너뜁니다.")
    else:
        estate_ids = insert_estate_data(db_connect, estate_data)  # estate_id 목록 받아오기

        # estate_details 테이블에 삽입할 데이터 (5개 컬럼)
        if estate_ids:
            estate_details_data = df.loc[:, ["본번", "층", "법정동코드", "건축년도", "건물면적(㎡)", "물건금액(만원)"]].values.tolist()
            insert_train_data(db_connect, estate_ids, estate_details_data)
        else:
            print("⚠️ estate_ids가 없습니다. estate_details 삽입을 건너뜁니다.")

    # DB 연결 닫기
    db_connect.close()

