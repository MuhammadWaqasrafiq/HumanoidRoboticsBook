from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.config import settings

class QdrantRetriever:
    def __init__(self, embedding_client):
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.embeddings = embedding_client
        self.collection_name = settings.COLLECTION_NAME

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Qdrant client close karna zaroori hai
        await self.client.close()

    async def upsert_documents(self, chunks):
        print(f"Generating embeddings for {len(chunks)} chunks...")
        vectors = await self.embeddings.embed_documents(chunks)
        
        # Collection check/create
        collections = await self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            print(f"Creating collection: {self.collection_name}")
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
            )

        points = [
            models.PointStruct(
                id=i,
                vector=vectors[i],
                payload={"text": chunks[i]}
            ) for i in range(len(chunks))
        ]
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print("Successfully uploaded to Qdrant!")

    async def search(self, query: str, top_k: int = 3):
        query_vector = await self.embeddings.embed_query(query)
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return [hit.payload["text"] for hit in results]

async def get_retriever_client():
    from app.rag.embeddings import GeminiEmbedding
    return QdrantRetriever(embedding_client=GeminiEmbedding())