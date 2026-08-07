from pydantic import BaseModel
from typing import Optional

class FinanceActionProposal(BaseModel):
    customer_id: str
    transaction_id: Optional[str] = "N/A"
    action_type: str
    requested_amount_inr: float
    currency: str = "INR"
    reasoning_chain: str
    sop_citation: str

class GuardrailVerdict(BaseModel):
    status: str
    governance_notes: str