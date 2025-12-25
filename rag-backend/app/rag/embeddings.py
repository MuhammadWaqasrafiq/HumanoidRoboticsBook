import httpx
from app.config import settings

class GeminiEmbedding:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        # Model name bina 'models/' prefix ke rakhein
        self.model_name = "text-embedding-004" 
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def embed_documents(self, texts: list[str]):
        url = f"{self.base_url}/models/{self.model_name}:batchEmbedContents?key={self.api_key}"
        
        requests = []
        for text in texts:
            requests.append({
                "model": f"models/{self.model_name}",
                "content": {"parts": [{"text": text}]},
                "task_type": "RETRIEVAL_DOCUMENT"
            })
        
        payload = {"requests": requests}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            if response.status_code != 200:
                print(f"Embedding Error: {response.text}")
                response.raise_for_status()
            
            data = response.json()
            return [item["values"] for item in data["embeddings"]]

    async def embed_query(self, text: str):
        url = f"{self.base_url}/models/{self.model_name}:embedContent?key={self.api_key}"
        
        payload = {
            "model": f"models/{self.model_name}",
            "content": {"parts": [{"text": text}]},
            "task_type": "RETRIEVAL_QUERY"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]["values"]