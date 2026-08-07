from schemas import FinanceActionProposal, GuardrailVerdict

class FinancialGuardrailEngine:
    """
    Deterministic governance engine enforcing financial cap policies in INR.
    """
    def __init__(self, max_auto_approve_cap_inr: float = 2500.00):
        self.max_auto_approve_cap_inr = max_auto_approve_cap_inr

    def evaluate(self, proposal: FinanceActionProposal) -> GuardrailVerdict:
        # Check 1: Exceeds threshold -> Escalate to human
        if proposal.requested_amount_inr > self.max_auto_approve_cap_inr:
            return GuardrailVerdict(
                status="ESCALATED_HUMAN_IN_THE_LOOP",
                governance_notes=f"Amount ₹{proposal.requested_amount_inr:.2f} INR exceeds auto-approval threshold of ₹{self.max_auto_approve_cap_inr:.2f} INR. Escalated for human review."
            )

        # Check 2: Within threshold -> Auto-approve
        if proposal.requested_amount_inr > 0:
            return GuardrailVerdict(
                status="AUTO_APPROVED",
                governance_notes=f"Auto-approved refund of ₹{proposal.requested_amount_inr:.2f} INR under threshold of ₹{self.max_auto_approve_cap_inr:.2f} INR."
            )

        # Fallback for 0.0 INR
        return GuardrailVerdict(
            status="AUTO_APPROVED",
            governance_notes="Informational query with zero financial commitment."
        )