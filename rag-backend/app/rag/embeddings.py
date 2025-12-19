import google.generativeai as genai
from app.config import settings

# Configure the Gemini API key
genai.configure(api_key=settings.GOOGLE_API_KEY)

class GeminiEmbedding:
    """
    A class to generate embeddings using the Gemini API.
    """
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        """
        Initializes the GeminiEmbedding instance.

        Args:
            model_name: The name of the embedding model to use.
        """
        self.model_name = model_name

    def get_embedding(self, text: str):
        """
        Generates an embedding for the given text.

        Args:
            text: The text to generate an embedding for.

        Returns:
            The generated embedding.
        """
        try:
            return genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )["embedding"]
        except Exception as e:
            print(f"An error occurred while generating embedding: {e}")
            return None

    def get_embeddings(self, texts: list[str]):
        """
        Generates embeddings for a list of texts.

        Args:
            texts: The list of texts to generate embeddings for.

        Returns:
            A list of generated embeddings.
        """
        try:
            # The Gemini API can handle batching of texts.
            result = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"An error occurred while generating embeddings: {e}")
            return None

def get_embedding_client() -> GeminiEmbedding:
    """
    Returns a GeminiEmbedding instance.
    This function can be used for dependency injection in FastAPI.
    """
    return GeminiEmbedding()
