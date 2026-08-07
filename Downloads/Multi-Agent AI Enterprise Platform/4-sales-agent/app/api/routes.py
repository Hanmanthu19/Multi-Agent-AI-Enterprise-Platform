from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import (
    ChatRequest, ChatResponse, QuoteRequest, QuotationOutput,
    LeadCreateSchema, LeadResponseSchema
)
from app.graph import sales_graph
from app.services.quotation import QuoteGenerator
from app.services.lead_scoring import LeadScoringService
from app.database import get_db
from app.models import LeadModel
from app.logger import logger

router = APIRouter(prefix="/sales", tags=["Enterprise Sales"])

@router.post("/chat", response_model=ChatResponse)
async def sales_chat_endpoint(payload: ChatRequest):
    try:
        initial_state = {
            "user_query": payload.user_query,
            "company_name": payload.company_name,
            "employee_count": payload.employee_count,
            "budget": payload.budget,
            "urgency": payload.urgency,
            "contact_email": payload.contact_email,
            "contact_phone": payload.contact_phone
        }
        
        final_state = sales_graph.invoke(initial_state)

        return ChatResponse(
            intent=final_state.get("intent", "General Sales Question"),
            retrieved_context=final_state.get("retrieved_chunks", []),
            agent_response=final_state.get("agent_response", ""),
            recommended_plan=final_state.get("recommended_plan"),
            pricing_estimate=final_state.get("pricing_estimate"),
            lead_score=final_state.get("lead_score"),
            quotation=final_state.get("quotation")
        )
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quote", response_model=QuotationOutput)
async def generate_quote_endpoint(payload: QuoteRequest):
    try:
        return QuoteGenerator.generate_quote(
            company_name=payload.company_name,
            plan_name=payload.plan_name,
            user_count=payload.user_count,
            billing_cycle=payload.billing_cycle,
            custom_discount_pct=payload.custom_discount_pct
        )
    except Exception as e:
        logger.error(f"Quote generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lead", response_model=LeadResponseSchema)
async def create_lead_endpoint(payload: LeadCreateSchema, db: Session = Depends(get_db)):
    try:
        score_res = LeadScoringService.score_lead(
            employee_count=payload.employee_count,
            budget=payload.budget,
            urgency=payload.urgency,
            intent="Purchase Intent",
            has_demo_req=False
        )

        lead = LeadModel(
            company_name=payload.company_name,
            industry=payload.industry,
            contact_email=payload.contact_email,
            contact_phone=payload.contact_phone,
            employee_count=payload.employee_count,
            lead_score=score_res.score,
            lead_priority=score_res.priority,
            recommended_plan="Enterprise" if payload.employee_count > 100 else "Pro"
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leads", response_model=List[LeadResponseSchema])
async def list_leads_endpoint(db: Session = Depends(get_db)):
    try:
        return db.query(LeadModel).order_by(LeadModel.created_at.desc()).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))