"""
LLM Chain Module
Handles Groq LLM integration for answer generation
"""
import os
from typing import List, Dict
from groq import Groq


class GroqLLMChain:
    """Generate answers using Groq LLM with retrieved context"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=self.api_key)
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    def generate_answer(self, query: str, retrieved_chunks: List[Dict]) -> Dict:
        context = "\n\n".join([
            f"[Chunk {i+1}]\n{chunk['text']}"
            for i, chunk in enumerate(retrieved_chunks)
        ])

        system_message = (
            "You are a helpful assistant answering questions based on a "
            "Product Requirements Document (PRD). Answer questions accurately "
            "using only the information provided in the context. If the "
            "information is not available in the context, say 'This information "
            "is not available in the provided document.' Be concise and clear."
        )

        user_message = (
            f"Based on the following document context, please answer the question:\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{query}\n\n"
            f"ANSWER:"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=1024,
                temperature=0.7,
            )

            answer = response.choices[0].message.content

            return {
                "status": "success",
                "query": query,
                "answer": answer,
                "model": self.model,
                "context_chunks": len(retrieved_chunks),
                "token_usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "model": self.model,
            }
