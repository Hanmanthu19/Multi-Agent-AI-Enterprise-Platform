from pydantic import BaseModel
from typing import Optional

class AgentCreate(BaseModel):
    name: str
    role: str
    description: str
    tools_allowed: str

class TaskCreate(BaseModel):
    agent_id: Optional[int] = None
    title: str
    prompt: str