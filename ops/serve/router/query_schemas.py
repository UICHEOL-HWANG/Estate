from pydantic import BaseModel

class QuerySchemas(BaseModel):
    query : str

class Response(BaseModel):
    response : str  