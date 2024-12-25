from typing import List
from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    iid: str
    description: str


class UserItemRecommendation(BaseModel):
    uid: str
    recommendations: List[Recommendation] = Field(default_factory=list)
