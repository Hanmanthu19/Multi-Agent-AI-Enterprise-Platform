# AI Agent Platform — Reorganized

Your zip had ~6 duplicate `main*.py` files (`main.py`, `maain.py`, `maaain.py`,
`maaaain.py`, `maaaaain.py`, `mainn2.py`) sitting loose in the project root,
which is why everything looked "merged." Comparing them, they were actually
**5 separate agents** at different stages of being wired together into one
FastAPI app. I split each agent into its own folder, and kept the one
"master" app (the supervisor) that ties Support + HR together in its own
folder too.

## Folder structure

```
AI-Agent-Platform/
├── 1-finance-agent/         Expense/claim governance agent (INR), RAG + guardrail engine
├── 2-support-agent/         Customer support/refund RAG engine + tools (used by the supervisor)
├── 3-hr-agent/              HR leave/PTO RAG engine + tools (used by the supervisor)
├── 4-sales-agent/           Full sales agent service (leads, pricing, quotation, recommendations)
├── 5-research-agent/        Research agent with web search + evaluator
└── supervisor-orchestrator/ Combines 2-support-agent + 3-hr-agent behind an LLM router
```

## What went where, and why

| Original file(s) | Went to | Notes |
|---|---|---|
| `main.py`, `agents/finance_agent.py`, `guardrails.py`, `vector_store.py`, `schemas.py`, `static/index.html` | `1-finance-agent/` | Self-contained "Enterprise AI Workforce Governance Engine" — RAG + deterministic guardrail + human-in-the-loop approval queue. |
| `rag_engine.py`, `agent_tools.py` | `2-support-agent/` | Refund/support RAG engine + the `AGENT_TOOLS` function-calling schema + `execute_stripe_refund`. |
| `hr_rag_engine.py`, `hr_tools.py` | `3-hr-agent/` | HR policy RAG engine + `HR_TOOLS` + `execute_hris_leave`. |
| `app/` (already a clean package) | `4-sales-agent/app/` | This one wasn't actually mixed up — it's a proper `app.main` FastAPI package (agents, services, rag, api, models). Copied as-is, run from inside `4-sales-agent/`. |
| `Research Agent/` (already clean) | `5-research-agent/` | Also already self-contained. Just removed the space in the folder name. |
| `maaaain.py` (the most complete of the 6 duplicates) → `main.py`, `supervisor_agent.py` | `supervisor-orchestrator/` | The LLM-based ticket router. It needs copies of the support & HR engines to run standalone, so those two are duplicated in here as well. |
| `maain.py`, `maaaaain.py`, `mainn2.py` | *(dropped)* | Earlier drafts of the same supervisor app — superseded by `maaaain.py`, kept nowhere since they're strictly older/less complete versions of what's now in `supervisor-orchestrator/`. Say the word if you'd rather I include them too. |
| `chroma_db/`, `chroma_db_hr/`, `data/chroma_db/`, `__pycache__/` | *(dropped)* | Generated vector-DB/bytecode artifacts, not source — they'll be rebuilt automatically the first time each agent runs. |

## Bug I fixed while separating things

`maaaain.py` imported `supervisor_triage` (which doesn't exist) and read
fields like `agent_target`/`extracted_amount`/`extracted_days` from the
triage result. The actual function in `supervisor_agent.py` is
`triage_ticket`, returning `intent`/`amount`/`duration`. I corrected the
import and field names in `supervisor-orchestrator/main.py` so it actually
runs. Everything else was left as you wrote it.

## ⚠️ Security note

Your original `.env` had an **unresolved git merge conflict** and contained
**two real Gemini API keys in plaintext**. I did not copy that file into any
of the new folders — each agent that needs one now has a `.env.example`
placeholder instead. Please rotate/revoke those two keys in Google AI
Studio since they were sitting in a zip you shared.

## Running each agent

Each folder has its own `requirements.txt`. From inside a given agent's
folder:

```bash
pip install -r requirements.txt
python main.py            # finance-agent, supervisor-orchestrator
# or
uvicorn app.main:app --reload   # 4-sales-agent (see HOW_TO_RUN.txt)
uvicorn main:app --reload       # 5-research-agent (see HOW_TO_RUN.txt)
```

`2-support-agent/` and `3-hr-agent/` are libraries (RAG engine + tools) —
they're consumed by `supervisor-orchestrator/`, not run standalone, unless
you want me to add a small standalone `main.py` for each.

## One thing not yet wired up

`supervisor_agent.py` can already classify a ticket as `"SALES"`, but no
route in `supervisor-orchestrator/main.py` handles that case yet — the
sales agent still lives as its own separate service in `4-sales-agent/`.
Let me know if you want me to wire the supervisor to call it too.
