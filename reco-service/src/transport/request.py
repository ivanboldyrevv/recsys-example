from typing import List
from pydantic import BaseModel, Field


class Item(BaseModel):
    iid: str
    description: str


class UserItemSequence(BaseModel):
    uid: str
    item_sequence: List[Item] = Field(default_factory=list)
