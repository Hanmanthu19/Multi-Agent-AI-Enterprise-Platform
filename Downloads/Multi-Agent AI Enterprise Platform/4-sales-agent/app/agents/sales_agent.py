import google.generativeai as genai
from app.config import settings
from app.prompts import SYSTEM_SALES_PROMPT, INTENT_DETECTION_PROMPT
from app.logger import logger

class GeminiSalesAgent:
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.warning("GEMINI_API_KEY is missing from environment config.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.MODEL_NAME)

    def detect_intent(self, query: str) -> str:
        try:
            prompt = INTENT_DETECTION_PROMPT.format(query=query)
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Failed to detect intent via Gemini: {str(e)}")
            return "General Sales Question"

    def generate_sales_response(self, query: str, context_chunks: list[str]) -> str:
        try:
            formatted_context = "\n---\n".join(context_chunks) if context_chunks else "No context available."
            prompt = SYSTEM_SALES_PROMPT.format(
                context=formatted_context,
                query=query
            )
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error invoking Gemini API: {str(e)}")
            return "I encountered an error processing your query against our sales system."

sales_agent_llm = GeminiSalesAgent()

def process_sales_query(text: str):
    """Processes a sales inquiry using Gemini Sales Agent."""
    try:
        intent = sales_agent_llm.detect_intent(text)
        resp = sales_agent_llm.generate_sales_response(text, context_chunks=[])
        return {
            "agent_name": "Sales AI Agent",
            "detected_intent": intent,
            "response": resp,
            "status": "SUCCESS"
        }
    except Exception as e:
        return {
            "agent_name": "Sales AI Agent",
            "detected_intent": "General Inquiry",
            "response": f"Sales Inquiry recorded for prompt: '{text}'. Thank you for your interest in our enterprise platform.",
            "error": str(e)
        }