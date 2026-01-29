import torch
import chromadb


from ..schemas import DataPoint, Document



class ChromaStore:
    def __init__(self, persist_directory: str | None = None):
        self.client = chromadb.PersistentClient(path=persist_directory) if persist_directory else chromadb.Client()

    def add_points(self, collection_name: str, data_points: list[DataPoint]) -> None:
        collection = self.client.get_or_create_collection(name=collection_name)

        ids = [str(i) for i in range(len(data_points))]
        embeddings = torch.stack([dp["embedding"] for dp in data_points]).cpu().numpy().tolist()
        metadatas = [dp["document"].metadata for dp in data_points]
        documents = [dp["document"].content for dp in data_points]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(
        self, 
        collection_name: str, 
        query_embedding: torch.Tensor, 
        n_results: int = 5, 
        **kwargs
    ) -> list[Document]:
        collection = self.client.get_collection(name=collection_name)

        query_embedding_np = query_embedding.cpu().numpy().tolist()
        results = collection.query(
            query_embeddings=[query_embedding_np],
            include=["documents", "metadatas"],
            n_results=n_results,
            **kwargs
        )

        documents = []
        for id, doc_content, metadata in zip(results['ids'][0], results['documents'][0], results['metadatas'][0]):
            documents.append(Document(id=id, content=doc_content, metadata=metadata))

        return documents