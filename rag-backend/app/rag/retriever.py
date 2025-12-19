from qdrant_client import QdrantClient, models
from app.config import settings
from app.rag.embeddings import GeminiEmbedding

class QdrantRetriever:
    """
    A class to handle retrieval from a Qdrant vector database.
    """
    def __init__(
        self,
        embedding_client: GeminiEmbedding,
        collection_name: str = settings.COLLECTION_NAME,
        qdrant_host: str = settings.QDRANT_HOST,
        qdrant_port: int = settings.QDRANT_PORT
    ):
        """
        Initializes the QdrantRetriever instance.

        Args:
            embedding_client: The client for generating embeddings.
            collection_name: The name of the collection in Qdrant.
            qdrant_host: The host for the Qdrant vector database.
            qdrant_port: The port for the Qdrant vector database.
        """
        # Using :memory: for local, non-persistent storage.
        # For persistent storage, provide a path: self.client = QdrantClient(path="/path/to/db")
        # Or run a Qdrant instance and connect to it:
        # self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.client = QdrantClient(":memory:")
        self.embedding_client = embedding_client
        self.collection_name = collection_name
        self.vector_size = len(self.embedding_client.get_embedding("test"))

        # Create collection if it doesn't exist
        try:
            self.client.get_collection(collection_name=self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
            )

    def upsert_documents(self, documents: list[str]):
        """
        Upserts documents into the Qdrant collection.

        Args:
            documents: A list of documents to upsert.
        """
        embeddings = self.embedding_client.get_embeddings(documents)
        if embeddings:
            self.client.upsert(
                collection_name=self.collection_name,
                points=models.Batch(
                    ids=[i for i in range(len(documents))],  # Simple sequential IDs
                    payloads=[{"text": doc} for doc in documents],
                    vectors=embeddings,
                ),
                wait=True
            )

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """
        Searches for relevant documents for a given query.

        Args:
            query: The query to search for.
            top_k: The number of top results to return.

        Returns:
            A list of relevant document texts.
        """
        query_embedding = self.embedding_client.get_embedding(query)
        if query_embedding:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            return [hit.payload['text'] for hit in search_result]
        return []

def get_retriever_client() -> QdrantRetriever:
    """
    Returns a QdrantRetriever instance.
    This function can be used for dependency injection in FastAPI.
    """
    embedding_client = GeminiEmbedding()
    return QdrantRetriever(embedding_client=embedding_client)
