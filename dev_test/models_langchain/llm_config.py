"""Configuration commune du LLM pour tous les modèles"""

from langchain_openai import ChatOpenAI

def get_llm(model: str = "gpt-4o-mini", temperature: float = 0.2):
    """Retourne une instance configurée du LLM"""
    return ChatOpenAI(
        model=model,
        temperature=temperature
    )