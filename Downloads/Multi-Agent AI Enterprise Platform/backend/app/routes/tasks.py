from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Task, Agent
from app.schemas import TaskCreate
from app.ai.supervisor import route_task_to_agent

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.post("/", response_model=Task)
def assign_task(task_data: TaskCreate, session: Session = Depends(get_session)):
    # 1. Store task in DB
    new_task = Task(**task_data.model_dump())
    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    # 2. Update Agent Status to Working
    agent = None
    if new_task.agent_id:
        agent = session.get(Agent, new_task.agent_id)
        if agent:
            agent.status = "Working"
            session.add(agent)
            session.commit()

    try:
        # 3. Process task through AI Engine
        role = agent.role if agent else "General AI Employee"
        description = agent.description if agent else ""
        tools_allowed = agent.tools_allowed if agent else ""
        ai_output = route_task_to_agent(
            agent_role=role,
            prompt=new_task.prompt,
            description=description,
            tools_allowed=tools_allowed
        )

        # 4. Save Output & Set Status to Completed
        new_task.response_output = ai_output
        new_task.status = "Completed"
    except Exception as e:
        new_task.status = "Failed"
        new_task.response_output = f"Task Execution Error: {str(e)}"
    finally:
        # Guarantee Agent status returns to "Idle" regardless of outcome
        if agent:
            agent.status = "Idle"
            session.add(agent)

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

    return new_task

@router.get("/", response_model=list[Task])
def list_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks