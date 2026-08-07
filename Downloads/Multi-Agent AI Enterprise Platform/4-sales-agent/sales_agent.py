import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from app.agents.sales_agent import process_sales_query
except Exception as e:
    def process_sales_query(text: str):
        return {
            "agent_name": "Sales AI Agent",
            "response": f"Sales Agent received query: '{text}'. Formulating proposal.",
            "status": "PROCESSED"
        }
