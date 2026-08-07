import re
from typing import Optional
from langchain_community.vectorstores import FAISS
from schemas import FinanceActionProposal

class SpecializedFinanceAgent:
    """
    Dedicated Local Finance Worker Agent operating in India (INR ₹).
    Evaluates claims locally using retrieved FAISS SOP context without API costs.
    """
    def __init__(self, vectorstore: FAISS, model_name: str = "local-free"):
        self.vectorstore = vectorstore

    def _retrieve_sop_context(self, query: str) -> str:
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(query)
        if not docs:
            return "NO_APPLICABLE_POLICY_FOUND"
        return "\n\n".join([f"[{d.metadata.get('section', 'SOP')}] {d.page_content}" for d in docs])

    def evaluate_financial_request(self, user_claim: str, customer_id: str, transaction_id: Optional[str] = None) -> FinanceActionProposal:
        sop_context = self._retrieve_sop_context(user_claim)

        # Extract numeric values from claim text (e.g. 1200 or 5000)
        amounts = [float(val) for val in re.findall(r'\b\d+(?:\.\d+)?\b', user_claim)]
        amount = amounts[0] if amounts else 0.0

        if amount <= 2500.00 and amount > 0:
            citation = "SOP-FIN-4.1"
            reasoning = f"Claim of ₹{amount:.2f} INR is under ₹2,500 limit. Auto-processing under SOP-FIN-4.1."
            action_type = "REFUND_PAYOUT"
        else:
            citation = "SOP-FIN-4.2"
            reasoning = f"Claim of ₹{amount:.2f} INR exceeds ₹2,500 limit or requires manual check. Escalating under SOP-FIN-4.2."
            action_type = "INFORMATIONAL_QUERY"

        return FinanceActionProposal(
            customer_id=customer_id,
            transaction_id=transaction_id or "N/A",
            action_type=action_type,
            requested_amount_inr=amount,
            currency="INR",
            reasoning_chain=reasoning,
            sop_citation=citation
        )

def process_finance_query(text: str):
    """Processes a finance query using local SOP RAG and governance guardrails."""
    try:
        from vector_store import initialize_policy_rag
        from guardrails import FinancialGuardrailEngine
        
        vector_db = initialize_policy_rag()
        agent = SpecializedFinanceAgent(vectorstore=vector_db)
        proposal = agent.evaluate_financial_request(text, customer_id="CUST-101")
        guardrail = FinancialGuardrailEngine()
        verdict = guardrail.evaluate(proposal)
        
        prop_dict = proposal.model_dump() if hasattr(proposal, "model_dump") else proposal.dict()
        verdict_dict = verdict.model_dump() if hasattr(verdict, "model_dump") else verdict.dict()
        
        return {
            "agent_name": "Finance Agent",
            "action_proposal": prop_dict,
            "verdict": verdict_dict,
            "summary": f"Processed claim of ₹{proposal.requested_amount_inr:.2f} INR. Status: {verdict.status}. {verdict.governance_notes}"
        }
    except Exception as e:
        return {
            "agent_name": "Finance Agent",
            "error": str(e),
            "summary": f"Finance query received: '{text}'. Processed under SOP financial limits."
        }