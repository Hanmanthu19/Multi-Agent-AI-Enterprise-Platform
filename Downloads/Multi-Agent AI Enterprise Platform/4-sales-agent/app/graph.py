from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from app.agents.sales_agent import sales_agent_llm
from app.rag.retriever import retriever
from app.services.recommendation import RecommendationService
from app.services.pricing import PricingEngine
from app.services.lead_scoring import LeadScoringService
from app.services.quotation import QuoteGenerator
from app.database import SessionLocal
from app.models import LeadModel
from app.logger import logger

class SalesWorkflowState(TypedDict):
    user_query: str
    company_name: str
    employee_count: int
    budget: float
    urgency: str
    contact_email: str
    contact_phone: Optional[str]
    intent: Optional[str]
    retrieved_chunks: Optional[List[str]]
    agent_response: Optional[str]
    recommended_plan: Optional[str]
    pricing_estimate: Optional[Dict[str, Any]]
    lead_score: Optional[Dict[str, Any]]
    quotation: Optional[Dict[str, Any]]

# --- Pipeline Node Callables ---

def intent_detection_node(state: SalesWorkflowState) -> Dict[str, Any]:
    intent = sales_agent_llm.detect_intent(state["user_query"])
    return {"intent": intent}

def rag_retrieval_node(state: SalesWorkflowState) -> Dict[str, Any]:
    chunks = retriever.retrieve(state["user_query"], top_k=3)
    return {"retrieved_chunks": chunks}

def gemini_response_node(state: SalesWorkflowState) -> Dict[str, Any]:
    response = sales_agent_llm.generate_sales_response(
        state["user_query"], 
        state.get("retrieved_chunks", [])
    )
    return {"agent_response": response}

def recommendation_node(state: SalesWorkflowState) -> Dict[str, Any]:
    rec = RecommendationService.recommend_tier(
        state.get("employee_count", 10),
        state.get("budget", 0.0),
        state.get("intent", "")
    )
    return {"recommended_plan": rec["tier"]}

def pricing_node(state: SalesWorkflowState) -> Dict[str, Any]:
    pricing = PricingEngine.calculate_price(
        plan_name=state.get("recommended_plan", "Pro"),
        user_count=state.get("employee_count", 10)
    )
    return {"pricing_estimate": pricing.model_dump()}

def lead_scoring_node(state: SalesWorkflowState) -> Dict[str, Any]:
    intent = state.get("intent", "")
    score_res = LeadScoringService.score_lead(
        employee_count=state.get("employee_count", 10),
        budget=state.get("budget", 0.0),
        urgency=state.get("urgency", "medium"),
        intent=intent,
        has_demo_req=(intent == "Demo Request")
    )
    return {"lead_score": score_res.model_dump()}

def quote_node(state: SalesWorkflowState) -> Dict[str, Any]:
    if state.get("intent") in ["Pricing Inquiry", "Purchase Intent", "Enterprise Plan"]:
        quote = QuoteGenerator.generate_quote(
            company_name=state.get("company_name", "Enterprise Client"),
            plan_name=state.get("recommended_plan", "Pro"),
            user_count=state.get("employee_count", 10)
        )
        return {"quotation": quote.model_dump()}
    return {"quotation": None}

def database_save_node(state: SalesWorkflowState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        score_data = state.get("lead_score", {})
        lead = LeadModel(
            company_name=state.get("company_name", "Unknown"),
            contact_email=state.get("contact_email", "client@example.com"),
            contact_phone=state.get("contact_phone"),
            employee_count=state.get("employee_count", 1),
            lead_score=score_data.get("score", 0.0),
            lead_priority=score_data.get("priority", "Cold"),
            recommended_plan=state.get("recommended_plan")
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
    except Exception as e:
        db.rollback()
        logger.error(f"Error persisting lead: {str(e)}")
    finally:
        db.close()
    return {}

# --- Assemble LangGraph Pipeline ---

builder = StateGraph(SalesWorkflowState)

builder.add_node("intent_detection", intent_detection_node)
builder.add_node("rag_retrieval", rag_retrieval_node)
builder.add_node("gemini_response", gemini_response_node)
builder.add_node("recommendation", recommendation_node)
builder.add_node("pricing", pricing_node)
builder.add_node("lead_scoring", lead_scoring_node)
builder.add_node("quote", quote_node)
builder.add_node("database_save", database_save_node)

builder.set_entry_point("intent_detection")
builder.add_edge("intent_detection", "rag_retrieval")
builder.add_edge("rag_retrieval", "gemini_response")
builder.add_edge("gemini_response", "recommendation")
builder.add_edge("recommendation", "pricing")
builder.add_edge("pricing", "lead_scoring")
builder.add_edge("lead_scoring", "quote")
builder.add_edge("quote", "database_save")
builder.add_edge("database_save", END)

sales_graph = builder.compile()