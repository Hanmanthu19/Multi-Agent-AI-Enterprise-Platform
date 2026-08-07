import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_IMPL"] = "chromadb.telemetry.product.posthog.Posthog"

import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from vector_store import initialize_policy_rag
from guardrails import FinancialGuardrailEngine
from finance_agent import SpecializedFinanceAgent

load_dotenv()

app = FastAPI(title="Enterprise AI Workforce Governance Engine (INR)")

vector_db = initialize_policy_rag()
finance_agent = SpecializedFinanceAgent(vectorstore=vector_db)
cap_limit = float(os.getenv("AUTO_APPROVAL_CAP_INR", 2500.00))
guardrail_engine = FinancialGuardrailEngine(max_auto_approve_cap_inr=cap_limit)

# In-memory queue for claims waiting for human approval
pending_approvals = {}

class ApprovalRequest(BaseModel):
    claim_id: str
    approved: bool

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

@app.post("/api/v1/manager/approve")
async def approve_claim(req: ApprovalRequest):
    if req.claim_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Claim ID not found or already processed")
    
    claim_data = pending_approvals.pop(req.claim_id)
    if req.approved:
        return {
            "status": "APPROVED",
            "message": f"Human Manager APPROVED payment of ₹{claim_data['amount']:.2f} INR for Customer {claim_data['customer_id']}."
        }
    else:
        return {
            "status": "REJECTED",
            "message": f"Human Manager REJECTED claim of ₹{claim_data['amount']:.2f} INR for Customer {claim_data['customer_id']}."
        }

async def sse_event_stream(claim: str, customer_id: str, transaction_id: str):
    # Event 1: Supervisor Routing
    yield f"data: {json.dumps({'event': 'SUPERVISOR_ROUTING', 'message': 'Routing request to SpecializedFinanceAgent...'})}\n\n"
    await asyncio.sleep(0.4)

    # Event 2: RAG Context Retrieval
    yield f"data: {json.dumps({'event': 'RAG_RETRIEVAL', 'message': 'Fetching policy constraints from vector store...'})}\n\n"
    await asyncio.sleep(0.4)

    # Event 3: Agent Reasoning Execution
    proposal = finance_agent.evaluate_financial_request(claim, customer_id, transaction_id)
    yield f"data: {json.dumps({'event': 'AGENT_REASONING', 'proposed_amount_inr': proposal.requested_amount_inr, 'citation': proposal.sop_citation, 'reasoning': proposal.reasoning_chain})}\n\n"
    await asyncio.sleep(0.4)

    # Event 4: Deterministic Guardrail Check
    verdict = guardrail_engine.evaluate(proposal)
    yield f"data: {json.dumps({'event': 'GUARDRAIL_EVALUATION', 'status': verdict.status, 'notes': verdict.governance_notes})}\n\n"
    await asyncio.sleep(0.4)

    # Event 5: Final Execution Dispatch or Escalation
    if verdict.status == "AUTO_APPROVED":
        yield f"data: {json.dumps({'event': 'EXECUTION_DISPATCH', 'status': 'SUCCESS', 'message': f'API Payment auto-dispatched for ₹{proposal.requested_amount_inr:.2f} INR.'})}\n\n"
    else:
        claim_id = f"CLM-{int(asyncio.get_event_loop().time() * 1000)}"
        pending_approvals[claim_id] = {
            "customer_id": customer_id,
            "amount": proposal.requested_amount_inr,
            "reasoning": proposal.reasoning_chain
        }
        yield f"data: {json.dumps({'event': 'HITL_ESCALATION_QUEUED', 'claim_id': claim_id, 'status': 'QUEUED_FOR_MANAGER', 'message': f'Claim of ₹{proposal.requested_amount_inr:.2f} INR exceeds ₹{cap_limit:.2f} limit. Waiting for human approval.'})}\n\n"

@app.get("/api/v1/process-claim")
async def process_claim(claim: str, customer_id: str, transaction_id: str = "N/A"):
    return StreamingResponse(
        sse_event_stream(claim, customer_id, transaction_id),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)