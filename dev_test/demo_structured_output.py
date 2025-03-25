from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# Pydantic models plus complexes
class SkillDetail(BaseModel):
    """Détails d'une compétence technique."""
    
    name: str = Field(..., description="Nom de la compétence")
    level: int = Field(..., description="Niveau de maîtrise de 1 à 5")
    years_experience: float = Field(..., description="Années d'expérience avec cette compétence")
    last_used: Optional[str] = Field(description="Date de dernière utilisation (YYYY-MM)")


class ProjectReference(BaseModel):
    """Référence à un projet où la compétence a été utilisée."""
    
    name: str = Field(..., description="Nom du projet")
    role: str = Field(..., description="Rôle dans le projet")
    impact: str = Field(..., description="Impact de la compétence dans ce projet")

class JokeDetails(BaseModel):
    """Details of the joke."""
    
    setup: str = Field(..., description="The setup of the joke")
    punchline: str = Field(..., description="The punchline to the joke")
    length: Optional[int] = Field(description="Length of the joke in characters")
    difficulty: int = Field(description="Difficulté de compréhension de 1 à 5")
    cultural_context: Optional[str] = Field(description="Contexte culturel nécessaire pour comprendre")

class JokeMetadata(BaseModel):
    """Metadata about the joke."""
    
    source: Optional[str] = Field(description="Source of the joke")
    popularity: Optional[int] = Field(description="Popularity score of the joke from 1 to 100")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the joke")
    related_skills: List[SkillDetail] = Field(default_factory=list, description="Compétences liées à cette blague")
    projects: List[ProjectReference] = Field(default_factory=list, description="Projets où cette blague a été utilisée")

class Joke(BaseModel):
    """Joke to tell user with additional details."""

    details: JokeDetails = Field(..., description="Details of the joke")
    rating: Optional[int] = Field(description="How funny the joke is, from 1 to 10")
    categories: List[str] = Field(default_factory=list, description="Categories of the joke")
    author: Optional[str] = Field(description="Author of the joke")
    date_created: Optional[str] = Field(description="Date when the joke was created")
    metadata: Optional[JokeMetadata] = Field(description="Additional metadata about the joke")
    suitable_for: List[str] = Field(default_factory=list, description="Public cible pour cette blague (enfants, adultes, etc.)")

structured_llm = llm.with_structured_output(Joke)

# Requête plus complexe pour tester les capacités
prompt = """
Raconte-moi une blague technique sur l'intelligence artificielle qui:
1. Inclut une référence à Python et aux modèles de langage
2. Est adaptée à un public de développeurs
3. Contient un jeu de mots subtil
4. Pourrait être utilisée lors d'une conférence tech
5. A un niveau de difficulté de 4/5

Fournis tous les détails possibles sur cette blague, y compris des compétences techniques associées.
"""

structured_llm.invoke(prompt)