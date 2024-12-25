from typing import List
from dataclasses import dataclass, field


@dataclass
class Prediction:
    iid: str
    score: float


@dataclass
class Item:
    iid: str
    description: str


@dataclass
class UserItemSequence:
    uid: str
    item_sequence: List[Item] = field(default_factory=list)
