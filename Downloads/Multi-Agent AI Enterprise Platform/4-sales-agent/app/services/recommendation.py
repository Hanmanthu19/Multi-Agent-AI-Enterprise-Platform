from typing import Dict, Any
from app.logger import logger

class RecommendationService:
    @staticmethod
    def recommend_tier(employee_count: int, budget: float, intent: str) -> Dict[str, Any]:
        if employee_count >= 200 or budget >= 10000 or intent == "Enterprise Plan":
            tier = "Enterprise"
            features = [
                "Dedicated Account Manager",
                "24/7 SLA Support",
                "Custom LLM Fine-tuning & Guardrails",
                "Unlimited RAG Collections",
                "SSO & On-Premises Deployment Options"
            ]
        elif employee_count >= 20 or budget >= 2000:
            tier = "Pro"
            features = [
                "Standard API Integration",
                "Priority Email Support",
                "Up to 50,000 Chat Sessions/mo",
                "Multi-Document Vector Search"
            ]
        else:
            tier = "Starter"
            features = [
                "Single Document RAG",
                "Community Support",
                "Up to 5,000 Chat Sessions/mo"
            ]

        logger.info(f"Recommended tier {tier} for workforce of {employee_count}")
        return {
            "tier": tier,
            "features": features,
            "reasoning": f"Based on employee headcount of {employee_count} and sales profile."
        }