import os
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Import directly from agents/research_agent.py
from agents.research_agent import ResearchAgent

app = FastAPI(title="Research Agent System")
research_agent = ResearchAgent()

# 1. Mount the static directory (serves any CSS, JS, or static files if needed)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# 2. Serve index.html from inside the static folder
@app.get("/", response_class=HTMLResponse)
def get_search_ui():
    static_index_path = os.path.join("static", "index.html")
    if os.path.exists(static_index_path):
        with open(static_index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found inside static/ folder.</h1>"


# 3. Search API endpoint triggered by the search bar
@app.get("/api/chat")
def search_api(q: str = Query(..., description="User search query")):
    result = research_agent.perform_research(q)
    return {
        "agent_name": "Research Agent",
        "output_text": result.retrieved_facts,
        "requires_human_approval": result.requires_human_verification
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)