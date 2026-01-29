from ..services import OllamaChatClient, ChromaStore, DocxSplitter
from ..utils import TextSplitter, Encoder
from ..schemas import DataPoint, Document



class RAGEngine:
    def __init__(self, ollama_model: str, embedding_model: str, chroma_collection_name: str):
        self.chat_client = OllamaChatClient(model=ollama_model)
        self.collection_name = chroma_collection_name
        self.vector_store = ChromaStore(collection_name=self.collection_name)
        self.text_splitter = TextSplitter()
        self.encoder = Encoder(model_name=embedding_model)

    def ingest_docx(self, docx_path: str):
        splitter = DocxSplitter(docx_path)
        documents = splitter.split_documents()
        embeddings = self.encoder.encode_documents(documents)
        data_points = [
            DataPoint(document=doc, embedding=emb)
            for doc, emb in zip(documents, embeddings)
        ]
        self.vector_store.add_points(self.collection_name, data_points)

    def retrieve(self, query: str, n_results: int = 5) -> list[Document]:
        query_embedding = self.encoder.encode_query(query)
        documents = self.vector_store.query(
            collection_name=self.collection_name,
            query_embedding=query_embedding,
            n_results=n_results
        )
        return documents