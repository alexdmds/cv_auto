"""Configuration commune du LLM pour tous les modèles"""

from langchain_openai import ChatOpenAI

def get_llm():
    """Retourne une instance configurée du LLM"""
    return ChatOpenAI(
        model="gpt-4o-mini",
    ) 