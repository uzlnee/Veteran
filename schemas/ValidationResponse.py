from langchain_core.pydantic_v1 import BaseModel, Field


class ValidationResponse(BaseModel):
    is_valid: bool = Field(description="응답이 유효한지 여부")
    message: str = Field(description="유효하지 않은 경우 부족한 정보 설명")