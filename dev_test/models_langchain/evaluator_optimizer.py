"""
Exemple d'evaluator-optimizer : un LLM génère du contenu pendant qu'un autre
l'évalue et fournit du feedback pour l'améliorer itérativement.
"""

from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from dev_test.models_langchain.llm_config_dev import get_llm

class Evaluation(BaseModel):
    """Structure pour l'évaluation du contenu"""
    quality: Literal["good", "needs_improvement"] = Field(
        description="Qualité du contenu (good ou needs_improvement)"
    )
    feedback: str = Field(
        description="Feedback détaillé pour amélioration"
    )

class State(TypedDict):
    topic: str
    current_text: str
    feedback: str
    quality: str
    iterations: int
    final_text: str

def generate_content(state: State) -> dict:
    """Génère ou améliore le contenu"""
    llm = get_llm()
    
    if state.get("feedback"):
        prompt = f"""Réécris ce texte en tenant compte du feedback :
        Texte actuel : {state['current_text']}
        Feedback : {state['feedback']}
        """
    else:
        prompt = f"Écris un texte professionnel sur : {state['topic']}"
    
    response = llm.invoke(prompt)
    print("Contenu généré/amélioré.")
    return {"current_text": response.content}

def evaluate_content(state: State) -> dict:
    """Évalue la qualité du contenu"""
    llm = get_llm().with_structured_output(Evaluation, method="function_calling")
    
    response = llm.invoke(f"""Évalue ce texte selon ces critères :
    - Clarté et structure
    - Pertinence du contenu
    - Style professionnel
    
    Texte à évaluer :
    {state['current_text']}
    """)
    
    print(f"Évaluation : {response.quality}")
    return {
        "quality": response.quality,
        "feedback": response.feedback,
        "iterations": state.get("iterations", 0) + 1
    }

def should_continue(state: State) -> str:
    """Décide si on continue l'optimisation"""
    if state["iterations"] >= 3 or state["quality"] == "good":
        return "finalize"
    return "improve"

def finalize(state: State) -> dict:
    """Finalise le texte"""
    print("Texte finalisé.")
    return {"final_text": state["current_text"]}

# Construction du graphe
graph = StateGraph(State)

# Ajout des nœuds
graph.add_node("generate", generate_content)
graph.add_node("evaluate", evaluate_content)
graph.add_node("finalize", finalize)

# Configuration des transitions
graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")

graph.add_conditional_edges(
    "evaluate",
    should_continue,
    {
        "improve": "generate",
        "finalize": "finalize"
    }
)

graph.add_edge("finalize", END)

# Compilation
chain = graph.compile()

if __name__ == "__main__":
    # Test
    result = chain.invoke({
        "topic": "L'importance de la documentation dans le développement logiciel"
    })
    print("\nTexte final :")
    print(result["final_text"])
    print("\nNombre d'itérations :", result["iterations"]) 