"""
Exemple de prompt chaining : décompose une tâche en séquence d'étapes.
Chaque appel LLM traite la sortie du précédent.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from dev_test.models_langchain.llm_config_dev import get_llm

class State(TypedDict):
    topic: str
    initial_draft: str
    improved_draft: str
    final_draft: str

def generate_initial(state: State) -> dict:
    """Première étape : génération du brouillon initial"""
    llm = get_llm()
    response = llm.invoke(f"Écris un premier jet sur {state['topic']}")
    print("Étape 1 : Brouillon initial généré.")
    return {"initial_draft": response.content}

def improve_draft(state: State) -> dict:
    """Deuxième étape : amélioration du brouillon"""
    llm = get_llm()
    prompt = f"""Améliore ce texte en le rendant plus professionnel :
    {state['initial_draft']}
    """
    response = llm.invoke(prompt)
    print("Étape 2 : Brouillon amélioré.")
    return {"improved_draft": response.content}

def finalize_draft(state: State) -> dict:
    """Troisième étape : finalisation et polish"""
    llm = get_llm()
    prompt = f"""Finalise ce texte en ajoutant des détails pertinents :
    {state['improved_draft']}
    """
    response = llm.invoke(prompt)
    print("Étape 3 : Brouillon finalisé.")
    return {"final_draft": response.content}

# Construction du graphe
graph = StateGraph(State)

# Ajout des nœuds
graph.add_node("generate", generate_initial)
graph.add_node("improve", improve_draft)
graph.add_node("finalize", finalize_draft)

# Configuration des transitions - Toujours passer par improve
graph.add_edge(START, "generate")
graph.add_edge("generate", "improve")
graph.add_edge("improve", "finalize")
graph.add_edge("finalize", END)

# Compilation
chain = graph.compile()

if __name__ == "__main__":
    # Test
    result = chain.invoke({
        "topic": "L'importance de l'IA dans le développement moderne"
    })
    print("Résultat final :")
    print(result["final_draft"]) 