from app.schemas import PricingBreakdown
from app.logger import logger

PLAN_BASE_PRICES = {
    "starter": 29.0,
    "pro": 79.0,
    "enterprise": 199.0
}

class PricingEngine:
    @staticmethod
    def calculate_price(
        plan_name: str,
        user_count: int,
        billing_cycle: str = "annual",
        custom_discount_pct: float = 0.0
    ) -> PricingBreakdown:
        normalized_plan = plan_name.lower().strip()
        base_unit = PLAN_BASE_PRICES.get(normalized_plan, PLAN_BASE_PRICES["pro"])
        
        months = 12 if billing_cycle.lower() == "annual" else 1
        subtotal = base_unit * user_count * months
        
        standard_discount = 0.20 if billing_cycle.lower() == "annual" else 0.0
        
        if user_count >= 100:
            standard_discount += 0.15
        elif user_count >= 50:
            standard_discount += 0.10

        total_discount_pct = min(standard_discount + (custom_discount_pct / 100.0), 0.50)
        discount_amount = subtotal * total_discount_pct
        
        taxable = subtotal - discount_amount
        tax_amount = taxable * 0.10
        final_total = taxable + tax_amount

        result = PricingBreakdown(
            plan_name=plan_name.title(),
            user_count=user_count,
            base_unit_price=base_unit,
            billing_cycle=billing_cycle.lower(),
            subtotal=round(subtotal, 2),
            discount_amount=round(discount_amount, 2),
            discount_percentage=round(total_discount_pct * 100, 1),
            tax_amount=round(tax_amount, 2),
            final_total=round(final_total, 2)
        )
        logger.info(f"Calculated pricing for {plan_name}: ${final_total}")
        return result