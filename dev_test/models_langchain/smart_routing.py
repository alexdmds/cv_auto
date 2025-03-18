"""
Exemple de routage : dirige la requête vers le traitement approprié
selon une analyse du contenu.
"""

from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from dev_test.models_langchain.llm_config_dev import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class Route(BaseModel):
    """Structure pour la décision de routage"""
    destination: Literal["story", "joke", "poem"] = Field(
        description="Où router la requête"
    )
    reason: str = Field(description="Justification du routage")

class State(TypedDict):
    input: str
    output: str
    route: str

def router(state: State) -> dict:
    """Analyse la requête et décide où la router"""
    llm = get_llm().with_structured_output(Route)
    
    response = llm.invoke([
        SystemMessage(content="Analyse la requête et décide si l'utilisateur veut une histoire, une blague ou un poème."),
        HumanMessage(content=state["input"])
    ])
    
    return {"route": response.destination}

def generate_story(state: State) -> dict:
    """Génère une histoire"""
    llm = get_llm()
    response = llm.invoke(f"Écris une histoire sur : {state['input']}")
    return {"output": response.content}

def generate_joke(state: State) -> dict:
    """Génère une blague"""
    llm = get_llm()
    response = llm.invoke(f"Écris une blague sur : {state['input']}")
    return {"output": response.content}

def generate_poem(state: State) -> dict:
    """Génère un poème"""
    llm = get_llm()
    response = llm.invoke(f"Écris un poème sur : {state['input']}")
    return {"output": response.content}

def route_to_generator(state: State) -> str:
    """Fonction de routage conditionnelle"""
    return state["route"]

# Construction du graphe
graph = StateGraph(State)

# Ajout des nœuds
graph.add_node("router", router)
graph.add_node("story", generate_story)
graph.add_node("joke", generate_joke)
graph.add_node("poem", generate_poem)

# Configuration du routage
graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    route_to_generator,
    {
        "story": "story",
        "joke": "joke",
        "poem": "poem"
    }
)

# Configuration des sorties
graph.add_edge("story", END)
graph.add_edge("joke", END)
graph.add_edge("poem", END)

# Compilation
chain = graph.compile()

if __name__ == "__main__":
    # Test
    result = chain.invoke({
        "input": "Raconte-moi une blague sur les programmeurs"
    })
    print(result["output"]) 