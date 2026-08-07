class FactEvaluator:
    """Evaluates fact density and computes source confidence scores."""
    
    @staticmethod
    def calculate_confidence(source_count: int, fact_length: int) -> float:
        if source_count >= 2 and fact_length > 100:
            return 0.95
        elif source_count >= 1 and fact_length > 30:
            return 0.80
        return 0.60