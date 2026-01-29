import torch
from sentence_transformers import SentenceTransformer

from ..schemas.document import Document



class Encoder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", **kwargs):
        self.model = SentenceTransformer(model_name, **kwargs)

    def encode_query(self, query: str, **kwargs) -> torch.Tensor:
        return self.model.encode_query(query, convert_to_tensor=True, **kwargs)

    def encode_documents(self, documents: list[str] | list[Document], **kwargs) -> torch.Tensor:
        texts = [doc.content if isinstance(doc, Document) else doc for doc in documents]
        return self.model.encode_document(texts, convert_to_tensor=True, **kwargs)