from pydantic import BaseModel
from uuid import uuid4



class Document(BaseModel):
    id: str = str(uuid4())
    content: str
    metadata: dict | None = None