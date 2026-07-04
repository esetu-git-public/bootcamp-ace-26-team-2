"""
Large Language Model (LLM) interaction service.

Wraps the Google Gemini API (via LangChain) for generating
answers grounded in retrieved document context.
"""


class LLMService:
    """
    Manages communication with the Gemini LLM.
    Future: Initialize LangChain Gemini model, implement generate().
    """

    def __init__(self):
        pass

    async def generate(self, prompt: str, context: str) -> str:
        """
        Send a prompt with retrieved context to the LLM and return the response.
        Future: Build the full prompt, call Gemini, parse the answer.
        """
        pass