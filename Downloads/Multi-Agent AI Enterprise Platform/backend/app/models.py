from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Agent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str                          # Support, Finance, Research, HR
    description: str
    status: str = "Idle"                # Idle, Working, Offline
    tools_allowed: str                  # e.g., "Email,CRM,Docs"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: Optional[int] = Field(default=None, foreign_key="agent.id")
    title: str
    prompt: str
    status: str = "Pending"              # Pending, In Progress, Completed, Escalated
    response_output: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)