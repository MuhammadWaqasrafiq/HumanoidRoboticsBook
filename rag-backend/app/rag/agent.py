import google.generativeai as genai
from app.config import settings
from app.rag.retriever import QdrantRetriever
from app.rag.embeddings import GeminiEmbedding

# Configure the Gemini API key
genai.configure(api_key=settings.GOOGLE_API_KEY)

class RAGAgent:
    """
    A RAG agent that uses a retriever and a generator to answer questions.
    """
    def __init__(self, retriever: QdrantRetriever, model_name: str = settings.CHAT_MODEL):
        """
        Initializes the RAGAgent instance.

        Args:
            retriever: The retriever for finding relevant documents.
            model_name: The name of the chat model to use.
        """
        self.retriever = retriever
        self.model = genai.GenerativeModel(model_name)

    def generate_answer(self, query: str) -> str:
        """
        Generates an answer to a query using the RAG pipeline.

        Args:
            query: The user's query.

        Returns:
            The generated answer.
        """
        # 1. Retrieve relevant context
        retrieved_chunks = self.retriever.search(query, top_k=3)

        # 2. Build the prompt
        if not retrieved_chunks:
            return "Not found in the book."

        context = "\n---\n".join(retrieved_chunks)
        
        prompt_template = """
        You are a helpful assistant for the book. Your name is 'BookBot'.
        You must answer questions based ONLY on the provided context.
        If the information to answer the question is not in the context, you MUST respond with 'Not found in the book.'.
        Do not add any other information or pleasantries.

        CONTEXT:
        ---
        {context}
        ---

        QUESTION: {query}

        ANSWER:
        """
        
        prompt = prompt_template.format(context=context, query=query)

        # 3. Generate the answer
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"An error occurred during response generation: {e}")
            return "Sorry, I encountered an error while generating a response."

def get_rag_agent() -> RAGAgent:
    """
    Returns a RAGAgent instance.
    This function can be used for dependency injection in FastAPI.
    """
    embedding_client = GeminiEmbedding()
    retriever = QdrantRetriever(embedding_client=embedding_client)
    return RAGAgent(retriever=retriever)
