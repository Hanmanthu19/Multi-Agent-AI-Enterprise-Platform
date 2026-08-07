from app.schemas import LeadScoreResult
from app.logger import logger

class LeadScoringService:
    @staticmethod
    def score_lead(
        employee_count: int,
        budget: float,
        urgency: str,
        intent: str,
        has_demo_req: bool
    ) -> LeadScoreResult:
        score = 0
        reasons = []

        if employee_count >= 500:
            score += 30
            reasons.append("Enterprise size tier (+30)")
        elif employee_count >= 50:
            score += 20
            reasons.append("Mid-Market size tier (+20)")
        else:
            score += 10
            reasons.append("Small business size tier (+10)")

        if intent in ["Purchase Intent", "Enterprise Plan"]:
            score += 25
            reasons.append("Strong purchase signal (+25)")
        elif intent in ["Pricing Inquiry", "Demo Request"]:
            score += 15
            reasons.append("Moderate inquiry signal (+15)")

        if urgency.lower() == "high":
            score += 20
            reasons.append("High urgency (+20)")
        elif urgency.lower() == "medium":
            score += 10
            reasons.append("Medium urgency (+10)")

        if budget >= 10000:
            score += 15
            reasons.append("High budget allocation (+15)")
        elif budget > 0:
            score += 5
            reasons.append("Defined budget (+5)")

        if has_demo_req:
            score += 10
            reasons.append("Demo request (+10)")

        score = min(score, 100)
        
        if score >= 70:
            priority = "Hot"
        elif score >= 40:
            priority = "Warm"
        else:
            priority = "Cold"

        logger.info(f"Calculated Lead Score: {score} ({priority})")
        return LeadScoreResult(score=score, priority=priority, reasoning=reasons)