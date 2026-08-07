import uuid
from datetime import datetime, timedelta
from app.schemas import QuotationOutput, PricingBreakdown
from app.services.pricing import PricingEngine
from app.services.recommendation import RecommendationService
from app.logger import logger

class QuoteGenerator:
    @staticmethod
    def generate_quote(
        company_name: str,
        plan_name: str,
        user_count: int,
        billing_cycle: str = "annual",
        custom_discount_pct: float = 0.0
    ) -> QuotationOutput:
        quote_id = f"QT-{uuid.uuid4().hex[:8].upper()}"
        pricing: PricingBreakdown = PricingEngine.calculate_price(
            plan_name=plan_name,
            user_count=user_count,
            billing_cycle=billing_cycle,
            custom_discount_pct=custom_discount_pct
        )
        
        rec_data = RecommendationService.recommend_tier(employee_count=user_count, budget=0, intent="")
        features = rec_data.get("features", ["Enterprise SLA Support"])

        valid_until = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

        quote = QuotationOutput(
            quote_id=quote_id,
            company_name=company_name,
            selected_plan=plan_name.title(),
            features=features,
            pricing=pricing,
            valid_until=valid_until
        )
        logger.info(f"Generated proposal {quote_id} for {company_name}")
        return quote
    