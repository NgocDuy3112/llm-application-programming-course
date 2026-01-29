import torch
from typing import TypedDict
from .document import Document


class DataPoint(TypedDict):
    document: Document
    embedding: torch.Tensor