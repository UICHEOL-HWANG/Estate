from fastapi import APIRouter, HTTPException
from .query_schemas import QuerySchemas, Response
from .model_selection import load_func, FEATURES
import numpy as np

predict_router = APIRouter(
    prefix="/predict",
    tags=["predict"],
    responses={404: {"description": "Not found"}},
)


@predict_router.post("/", response_model=Response)
def predict(query: QuerySchemas):
    """
    예시 입력: "3,110101,2005,85.0"
    각 값은 모델 학습 시 사용된 피처 순서대로 입력됩니다.
    """
    try:
        # 입력 문자열을 쉼표 기준으로 분리하여 숫자로 변환
        values = [float(x.strip()) for x in query.query.split(",")]
    except Exception:
        raise HTTPException(status_code=400, detail="입력 형식 오류: 쉼표로 구분된 숫자값을 입력하세요.")

    if len(values) != len(FEATURES):
        raise HTTPException(status_code=400, detail=f"입력값 개수가 올바르지 않습니다. (예상: {len(FEATURES)}개)")

    # 데이터를 리스트 안에 리스트 형태로 전달 (예: [[...]])
    data = [values]

    try:
        predictions = load_func(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예측 오류: {e}")

    return Response(response=str(np.expm1(predictions[0])))
