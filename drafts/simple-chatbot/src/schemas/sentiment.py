from pydantic import BaseModel
from typing import Literal


class SentimentAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    reason: str