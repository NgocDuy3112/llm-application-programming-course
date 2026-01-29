from ..services import  ChromaStore, DocxSplitter
from ..utils import TextSplitter, Encoder
from ..schemas import DataPoint, Document



class IngestAndRetrievalEngine:
    def __init__(
        self, 
        embedding_model: str, 
        persist_directory: str,
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ):
        self.per = persist_directory
        self.vector_store = ChromaStore(persist_directory=persist_directory)
        self.text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.encoder = Encoder(model_name=embedding_model)

    def ingest_docx(self, docx_path: str, collection_name: str) -> None:
        splitter = DocxSplitter(docx_path)
        documents = splitter.split_documents()
        embeddings = self.encoder.encode_documents(documents)
        data_points = [
            DataPoint(document=doc, embedding=emb)
            for doc, emb in zip(documents, embeddings)
        ]
        self.vector_store.add_points(collection_name, data_points)

    def retrieve(self, query: str, collection_name: str, n_results: int = 5) -> list[Document]:
        query_embedding = self.encoder.encode_query(query)
        documents = self.vector_store.query(
            collection_name=collection_name,
            query_embedding=query_embedding,
            n_results=n_results
        )
        return documents