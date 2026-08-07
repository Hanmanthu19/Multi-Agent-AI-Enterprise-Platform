from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

class ChatRequest(BaseModel):
    user_query: str
    company_name: Optional[str] = "Unknown Enterprise"
    employee_count: Optional[int] = 10
    budget: Optional[float] = 0.0
    contact_email: Optional[EmailStr] = "prospect@example.com"
    contact_phone: Optional[str] = None
    urgency: Optional[str] = "medium"

class QuoteRequest(BaseModel):
    company_name: str
    plan_name: str
    user_count: int = Field(gt=0, default=10)
    billing_cycle: str = Field(default="annual")
    custom_discount_pct: Optional[float] = Field(default=0.0, ge=0.0, le=50.0)

class LeadCreateSchema(BaseModel):
    company_name: str
    industry: Optional[str] = "Technology"
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    employee_count: int = Field(gt=0, default=1)
    budget: float = Field(ge=0.0, default=0.0)
    urgency: str = Field(default="medium")

class PricingBreakdown(BaseModel):
    plan_name: str
    user_count: int
    base_unit_price: float
    billing_cycle: str
    subtotal: float
    discount_amount: float
    discount_percentage: float
    tax_amount: float
    final_total: float

class QuotationOutput(BaseModel):
    quote_id: str
    company_name: str
    selected_plan: str
    features: List[str]
    pricing: PricingBreakdown
    valid_until: str

class LeadScoreResult(BaseModel):
    score: int
    priority: str
    reasoning: List[str]

class ChatResponse(BaseModel):
    intent: str
    retrieved_context: List[str]
    agent_response: str
    recommended_plan: Optional[str] = None
    pricing_estimate: Optional[Dict[str, Any]] = None
    lead_score: Optional[LeadScoreResult] = None
    quotation: Optional[Dict[str, Any]] = None

class LeadResponseSchema(BaseModel):
    id: int
    company_name: str
    industry: Optional[str]
    contact_email: str
    contact_phone: Optional[str]
    employee_count: int
    lead_score: float
    lead_priority: str
    recommended_plan: Optional[str]
    created_at: Any

    class Config:
        from_attributes = True