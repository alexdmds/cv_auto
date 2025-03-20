"""
Exemple d'orchestrator-worker : un LLM central décompose la tâche
et délègue le travail à des workers spécialisés.
"""

from typing import TypedDict, List, Annotated
import operator
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from dev_test.models_langchain.llm_config_dev import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class Section(BaseModel):
    """Structure pour une section du rapport"""
    title: str = Field(description="Titre de la section")
    content_type: str = Field(description="Type de contenu (technique, business, etc)")
    key_points: List[str] = Field(description="Points clés à couvrir")

class Plan(BaseModel):
    """Structure pour le plan du rapport"""
    sections: List[Section] = Field(description="Liste des sections à générer")

class State(TypedDict):
    topic: str
    sections: List[Section]
    completed_sections: Annotated[List[dict], operator.add]
    final_report: str

def orchestrator(state: State) -> dict:
    """Planifie la structure du rapport"""
    llm = get_llm().with_structured_output(Plan)
    
    response = llm.invoke([
        SystemMessage(content="Crée un plan détaillé pour un rapport professionnel."),
        HumanMessage(content=f"Sujet du rapport : {state['topic']}")
    ])
    
    return {"sections": response.sections}

def write_section(state: State) -> dict:
    """Worker qui rédige une section spécifique"""
    section = state["section"]
    llm = get_llm()
    
    prompt = f"""Rédige une section de rapport avec ces caractéristiques :
    Titre : {section.title}
    Type : {section.content_type}
    Points clés à couvrir : {', '.join(section.key_points)}
    """
    
    response = llm.invoke(prompt)
    return {"completed_sections": [{
        "title": section.title,
        "content": response.content
    }]}

def synthesize_report(state: State) -> dict:
    """Assemble le rapport final"""
    # Trier les sections selon leur ordre dans le plan original
    section_order = {s.title: i for i, s in enumerate(state["sections"])}
    completed = sorted(
        state["completed_sections"],
        key=lambda x: section_order.get(x["title"], float("inf"))
    )
    
    # Assembler le rapport
    report = f"# Rapport : {state['topic']}\n\n"
    for section in completed:
        report += f"## {section['title']}\n\n"
        report += f"{section['content']}\n\n"
    
    return {"final_report": report}

# Construction du graphe
graph = StateGraph(State)

# Ajout des nœuds
graph.add_node("orchestrator", orchestrator)
graph.add_node("write_section", write_section)
graph.add_node("synthesize", synthesize_report)

# Configuration des transitions
graph.add_edge(START, "orchestrator")

def route_to_workers(state: State):
    """Route chaque section vers un worker"""
    return [
        Send("write_section", {"section": section})
        for section in state["sections"]
    ]

graph.add_conditional_edges(
    "orchestrator",
    route_to_workers,
    ["write_section"]
)

graph.add_edge("write_section", "synthesize")
graph.add_edge("synthesize", END)

# Compilation
chain = graph.compile()

if __name__ == "__main__":
    # Test
    result = chain.invoke({
        "topic": "Impact de l'IA sur le développement logiciel"
    })
    print(result["final_report"]) 