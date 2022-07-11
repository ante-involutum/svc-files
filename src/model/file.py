from typing import Any, List
from pydantic import BaseModel


class File(BaseModel):
    name: str


class Plan(BaseModel):
    plan_name: str
    attachment: List[Any]
