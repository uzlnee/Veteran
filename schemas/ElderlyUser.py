from langchain_core.pydantic_v1 import BaseModel
from typing import List

class ElderlyUser:
    name: str
    age: int
    location: str
    available_time: str
    license: List[str]
    preferred_field: List[str]
    health_condition: str
    career: str
    education: str