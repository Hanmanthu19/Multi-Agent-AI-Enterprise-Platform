from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Agent
from app.schemas import AgentCreate

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.post("/", response_model=Agent)
def create_agent(agent_data: AgentCreate, session: Session = Depends(get_session)):
    new_agent = Agent(**agent_data.model_dump())
    session.add(new_agent)
    session.commit()
    session.refresh(new_agent)
    return new_agent

@router.get("/", response_model=list[Agent])
def list_agents(session: Session = Depends(get_session)):
    agents = session.exec(select(Agent)).all()
    return agents