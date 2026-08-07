import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

# --- DYNAMIC SYSTEM PATH WIRING ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "1-finance-agent"))
sys.path.append(str(BASE_DIR / "3-hr-agent"))
sys.path.append(str(BASE_DIR / "4-sales-agent"))
sys.path.append(str(BASE_DIR / "5-research-agent"))

# Import Super Agent Supervisor Router
# Guarded: a broken supervisor import must not take down the whole server.
try:
    from app.ai.supervisor import classify_and_route
except Exception as e:
    print(f"Warning: Failed to import classify_and_route: {e}")
    print("Falling back to a basic keyword router so the server can still start.")

    def classify_and_route(text: str) -> str:
        lower = text.lower()
        if any(t in lower for t in ["finance", "invoice", "refund", "claim", "budget", "expense", "payment", "inr"]):
            return "FINANCE"
        if any(t in lower for t in ["hr", "leave", "pto", "vacation", "policy", "hiring", "sick", "employee"]):
            return "HR"
        if any(t in lower for t in ["sales", "lead", "quote", "proposal", "pricing", "deal", "demo"]):
            return "SALES"
        return "RESEARCH"

# --- AGENT IMPORTS WITH TRY/EXCEPT FALLBACKS ---
try:
    from finance_agent import process_finance_query
except Exception as e:
    print(f"Warning: Failed to import process_finance_query: {e}")
    process_finance_query = None

try:
    from hr_rag_engine import process_hr_query
except Exception as e:
    print(f"Warning: Failed to import process_hr_query: {e}")
    process_hr_query = None

try:
    from sales_agent import process_sales_query
except Exception as e:
    try:
        from app.agents.sales_agent import process_sales_query
    except Exception as ex:
        print(f"Warning: Failed to import process_sales_query: {ex}")
        process_sales_query = None

try:
    from research_agent import process_research_query
except Exception as e:
    try:
        from agents.research_agent import process_research_query
    except Exception as ex:
        print(f"Warning: Failed to import process_research_query: {ex}")
        process_research_query = None


print("=" * 60)
print("AGENT STARTUP REPORT")
print(f"  FINANCE  agent : {'OK' if process_finance_query else 'MISSING (will DISCONNECT)'}")
print(f"  HR       agent : {'OK' if process_hr_query else 'MISSING (will DISCONNECT)'}")
print(f"  SALES    agent : {'OK' if process_sales_query else 'MISSING (will DISCONNECT)'}")
print(f"  RESEARCH agent : {'OK' if process_research_query else 'MISSING (will DISCONNECT)'}")
print("=" * 60)

app = FastAPI(title="AI Employee Factory Platform")

# Configure CORS explicitly for http://localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AI Employee Factory Unified Orchestrator",
        "endpoints": ["/api/orchestrate"]
    }


@app.post("/api/orchestrate")
async def orchestrate_workflow(
    file: Optional[UploadFile] = File(None),
    user_prompt: Optional[str] = Form(None)
):
    try:
        # 1. Read document text if a file was uploaded
        file_text = ""
        if file:
            content = await file.read()
            file_text = content.decode("utf-8", errors="ignore")

        # 2. Build combined prompt
        prompt_parts = []
        if user_prompt and user_prompt.strip():
            prompt_parts.append(user_prompt.strip())
        if file_text.strip():
            prompt_parts.append(f"[Uploaded File Content: {file.filename}]\n{file_text.strip()}")

        combined_text = "\n\n".join(prompt_parts).strip()
        if not combined_text:
            raise HTTPException(status_code=400, detail="Please provide a prompt or upload a file.")

        # 3. Super Agent classifies the prompt into department
        department = classify_and_route(combined_text)

        # 4. Route text to the corresponding sub-agent function
        result_data = None

        if department == "FINANCE":
            if process_finance_query:
                result_data = process_finance_query(combined_text)
            else:
                result_data = {"agent_name": "Finance Agent", "output": f"Finance claim received: '{combined_text[:100]}...'", "status": "DISCONNECTED"}
        elif department == "HR":
            if process_hr_query:
                result_data = process_hr_query(combined_text)
            else:
                result_data = {"agent_name": "HR Agent", "output": f"HR request received: '{combined_text[:100]}...'", "status": "DISCONNECTED"}
        elif department == "SALES":
            if process_sales_query:
                result_data = process_sales_query(combined_text)
            else:
                result_data = {"agent_name": "Sales Agent", "output": f"Sales lead received: '{combined_text[:100]}...'", "status": "DISCONNECTED"}
        elif department == "RESEARCH":
            if process_research_query:
                result_data = process_research_query(combined_text)
            else:
                result_data = {"agent_name": "Research Agent", "output": f"Research query received: '{combined_text[:100]}...'", "status": "DISCONNECTED"}
        else:
            result_data = {"agent_name": "General Agent", "output": f"Processed query: '{combined_text}'", "status": "PROCESSED"}

        # 5. Return clean JSON response
        return {
            "status": "success",
            "department": department,
            "data": result_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)