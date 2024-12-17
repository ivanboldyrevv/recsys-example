from dataclasses import dataclass


@dataclass
class Prediction:
    iid: str
    score: float
