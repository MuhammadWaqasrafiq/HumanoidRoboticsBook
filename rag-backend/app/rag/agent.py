import os
import google.genai as genai
from app.config import settings
from app.rag.retriever import QdrantRetriever, get_retriever_client
from app.rag.persona import prompt_template

class RAGAgent:
    def __init__(self, retriever: QdrantRetriever, model_name: str = settings.CHAT_MODEL):
        """
        Initializes the RAGAgent.
        Sets the Google API key as an environment variable and initializes the model.
        """
        os.environ['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
        
        self.retriever = retriever
        self.model = genai.GenerativeModel(model_name)

    async def generate_answer(self, query: str, context: str | None = None) -> str:
        """
        Generates an answer by retrieving context and calling the generative model.
        """
        if context:
            query = f"Context: {context}\n\nQuestion: {query}"
            
        retrieved_chunks = await self.retriever.search(query, top_k=3)
        if not retrieved_chunks:
            return "I could not find any relevant information in the book to answer your question."

        context_str = "\n---\n".join(retrieved_chunks)
        prompt = prompt_template.format(context=context_str, query=query)

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error during content generation: {e}")
            return "I am sorry, but I encountered an error while trying to generate a response."

async def get_rag_agent():
    """
    FastAPI dependency to get a RAGAgent instance.
    This correctly handles the lifecycle of the QdrantRetriever.
    """
    retriever = await get_retriever_client()
    try:
        # Manually enter the context
        await retriever.__aenter__()
        yield RAGAgent(retriever=retriever)
    finally:
        # Manually exit the context to ensure cleanup
        await retriever.__aexit__(None, None, None)