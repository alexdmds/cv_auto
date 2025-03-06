"""
Exemple de parallélisation : exécution simultanée de plusieurs tâches LLM
et agrégation des résultats.
"""

from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from models_langchain.llm_config import get_llm

class State(TypedDict):
    topic: str
    story_text: str  # Renommé pour éviter le conflit
    joke_text: str   # Renommé pour éviter le conflit
    poem_text: str   # Renommé pour éviter le conflit
    combined_output: str

def generate_story(state: State) -> dict:
    """Génère une histoire sur le sujet"""
    llm = get_llm()
    response = llm.invoke(f"Écris une courte histoire sur {state['topic']}")
    print("Histoire générée.")
    return {"story_text": response.content}

def generate_joke(state: State) -> dict:
    """Génère une blague sur le sujet"""
    llm = get_llm()
    response = llm.invoke(f"Écris une blague sur {state['topic']}")
    print("Blague générée.")
    return {"joke_text": response.content}

def generate_poem(state: State) -> dict:
    """Génère un poème sur le sujet"""
    llm = get_llm()
    response = llm.invoke(f"Écris un court poème sur {state['topic']}")
    print("Poème généré.")
    return {"poem_text": response.content}

def combine_outputs(state: State) -> dict:
    """Combine tous les outputs en un seul texte"""
    combined = f"Sur le thème de {state['topic']} :\n\n"
    combined += f"HISTOIRE :\n{state['story_text']}\n\n"
    combined += f"BLAGUE :\n{state['joke_text']}\n\n"
    combined += f"POÈME :\n{state['poem_text']}"
    print("Contenus combinés.")
    return {"combined_output": combined}

# Construction du graphe
graph = StateGraph(State)

# Ajout des nœuds avec des noms différents des clés d'état
graph.add_node("generate_story", generate_story)
graph.add_node("generate_joke", generate_joke)
graph.add_node("generate_poem", generate_poem)
graph.add_node("combine", combine_outputs)

# Configuration des transitions parallèles
graph.add_edge(START, "generate_story")
graph.add_edge(START, "generate_joke")
graph.add_edge(START, "generate_poem")

# Configuration de la convergence
graph.add_edge("generate_story", "combine")
graph.add_edge("generate_joke", "combine")
graph.add_edge("generate_poem", "combine")
graph.add_edge("combine", END)

# Compilation
chain = graph.compile()

if __name__ == "__main__":
    # Test
    result = chain.invoke({
        "topic": "L'intelligence artificielle"
    })
    print("\nRésultat final :")
    print(result["combined_output"]) 