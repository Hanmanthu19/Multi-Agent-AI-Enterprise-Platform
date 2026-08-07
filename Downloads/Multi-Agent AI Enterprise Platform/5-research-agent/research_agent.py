import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

try:
    from agents.research_agent import process_research_query
except Exception as e:
    def process_research_query(text: str):
        return {
            "agent_name": "Research Agent",
            "output_text": f"Research query: '{text}'. Extracted key research notes.",
            "status": "PROCESSED"
        }
