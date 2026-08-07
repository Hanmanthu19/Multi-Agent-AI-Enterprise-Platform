import os
import re
from typing import List, Tuple
from pydantic import BaseModel, Field


# 1. Define the missing ResearchResult schema
class ResearchResult(BaseModel):
    query: str
    sources_consulted: List[str] = Field(default_factory=list)
    retrieved_facts: str
    confidence_score: float
    requires_human_verification: bool = False


# 2. Helper evaluator class to avoid NameError for FactEvaluator
class FactEvaluator:
    @staticmethod
    def calculate_confidence(num_sources: int, facts_length: int) -> float:
        if num_sources == 0 or facts_length == 0:
            return 0.0
        # Basic confidence calculation based on sources and content depth
        score = min(1.0, 0.5 + (num_sources * 0.15) + (min(facts_length, 500) / 1000.0))
        return round(score, 2)


# 3. Main Research Agent Class
class ResearchAgent:
    def __init__(self, upload_dir: str = None):
        self.upload_dir = upload_dir or os.path.join("data", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def search_company_datasets(self, query: str) -> Tuple[List[str], List[str]]:
        """Scans local dataset directory for facts matching query keywords."""
        sources = []
        facts_list = []
        keywords = [k.lower() for k in re.findall(r'\w+', query) if len(k) > 2]

        if os.path.exists(self.upload_dir):
            for file in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, file)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            # Match keywords against text
                            if any(kw in content.lower() for kw in keywords):
                                sources.append(file)
                                facts_list.append(f"📄 [{file}]:\n{content[:400].strip()}...")
                    except Exception as e:
                        print(f"Error reading file {file}: {e}")

        return sources, facts_list

    def perform_research(self, query: str) -> ResearchResult:
        sources, facts_list = self.search_company_datasets(query)

        if not facts_list:
            sources.append("System Guidance")
            formatted_facts = f"No ingested company dataset matched query: '{query}'."
        else:
            # Build explicit top header listing all identified source datasets
            unique_sources = ", ".join(sources)
            top_header = f"Data extracted from dataset(s): {unique_sources}\n" + ("=" * 60) + "\n\n"
            
            # Format the individual retrieved blocks cleanly
            formatted_facts = top_header + "\n\n".join(facts_list)

        confidence = FactEvaluator.calculate_confidence(len(sources), len(formatted_facts))

        return ResearchResult(
            query=query,
            sources_consulted=sources,
            retrieved_facts=formatted_facts,
            confidence_score=confidence,
            requires_human_verification=(confidence < 0.70)
        )


# Direct test block
if __name__ == "__main__":
    agent = ResearchAgent()
    res = agent.perform_research("company policy")
    print(res.model_dump_json(indent=2))

def process_research_query(text: str):
    """Processes a research query using local company datasets scanner."""
    try:
        agent = ResearchAgent()
        result = agent.perform_research(text)
        return {
            "agent_name": "Research Agent",
            "query": text,
            "output_text": result.retrieved_facts,
            "sources_consulted": result.sources_consulted,
            "confidence_score": result.confidence_score,
            "requires_human_approval": result.requires_human_verification,
            "status": "SUCCESS"
        }
    except Exception as e:
        return {
            "agent_name": "Research Agent",
            "query": text,
            "output_text": f"Research Agent processed query: '{text}'. Scanning knowledge repositories.",
            "error": str(e),
            "status": "PROCESSED"
        }