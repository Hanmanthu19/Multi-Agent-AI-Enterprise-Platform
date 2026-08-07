from pydantic import BaseModel
from typing import List, Optional

class ResearchRequest(BaseModel):
    query: str

class ResearchResult(BaseModel):
    query: str
    sources_consulted: List[str]
    retrieved_facts: str
    confidence_score: float
    requires_human_verification: bool = False