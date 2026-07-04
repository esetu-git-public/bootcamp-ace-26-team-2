"""
RAG (Retrieval-Augmented Generation) orchestration service.

Coordinates the end-to-end RAG pipeline:
1. Retrieve relevant document chunks from the vector store.
2. Build a prompt with the retrieved context.
3. Invoke the LLM to generate a grounded answer.
"""


class RAGService:
    """
    Orchestrates the retrieval-augmented generation flow.
    Future: Implement retrieve -> augment -> generate pipeline.
    """

    def __init__(self):
        pass

    async def answer_question(self, question: str, document_id: str) -> str:
        """
        Given a user question and document context, return a generated answer.
        Future: Call retrieval_service, build prompt, call llm_service.
        """
        pass