import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Guard the google-genai import: if the package is missing or conflicts
# with google-generativeai, this must NOT crash the whole backend on startup.
# We fall back to rule-based classification instead (see below).
try:
    from google import genai
except Exception as e:
    print(f"[SUPERVISOR] Warning: google-genai not available ({e}). "
          f"Falling back to rule-based classification only.")
    genai = None

def get_genai_client():
    if genai is None:
        return None
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your-key-here":
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            print(f"[SUPERVISOR] Warning: could not create genai client: {e}")
    return None

def classify_and_route(text: str) -> str:
    """Super Agent: Prompts gemini-2.5-flash to classify input strictly into FINANCE, HR, SALES, or RESEARCH."""
    prompt = f"""
You are the Super Agent Supervisor of an enterprise AI workforce.
Analyze the following text and determine which specialized AI Employee department should handle it.

Choose EXACTLY ONE department name:
- FINANCE (invoices, budgets, claims, payments, financial policy, refunds, expenses)
- HR (leave requests, employee policies, hiring, PTO, benefits, onboarding)
- SALES (leads, proposals, quotes, enterprise plan inquiries, pricing estimates)
- RESEARCH (deep analysis, dataset searches, market research, summaries, general queries)

Respond with ONLY the department name in capital letters (FINANCE, HR, SALES, or RESEARCH) and nothing else.

Content to classify:
{text[:2000]}
"""

    client = get_genai_client()
    if client:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            category = response.text.strip().upper()
            
            for valid in ["FINANCE", "HR", "SALES", "RESEARCH"]:
                if valid in category:
                    return valid
        except Exception as e:
            print(f"[SUPERVISOR] Gemini API error: {e}")

    # Rule-based fallback mechanism
    lower = text.lower()
    if any(term in lower for term in ["finance", "invoice", "refund", "claim", "budget", "expense", "payment", "rupee", "inr", "payout"]):
        return "FINANCE"
    if any(term in lower for term in ["hr", "leave", "pto", "vacation", "policy", "hiring", "sick", "onboard", "employee"]):
        return "HR"
    if any(term in lower for term in ["sales", "lead", "quote", "proposal", "pricing", "deal", "tier", "subscription", "demo"]):
        return "SALES"
    return "RESEARCH"