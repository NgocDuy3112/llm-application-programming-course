import torch
from pydantic import BaseModel
from .document import Document


class DataPoint(BaseModel):
    document: Document
    embedding: torch.Tensor