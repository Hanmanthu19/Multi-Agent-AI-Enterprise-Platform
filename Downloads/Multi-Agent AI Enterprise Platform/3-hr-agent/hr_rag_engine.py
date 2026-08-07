import os
import chromadb
from pypdf import PdfReader

class FastEmbeddingFunction(chromadb.EmbeddingFunction):
    def name(self) -> str:
        return "fast_hr_embedding"

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        embeddings = []
        for text in input:
            vec = [0.0] * 384
            for i, char in enumerate(str(text)[:384]):
                vec[i] = ord(char) / 255.0
            embeddings.append(vec)
        return embeddings

class HRRAGEngine:
    def __init__(self, chroma_path="./chroma_db_hr"):
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="hr_policies",
            embedding_function=FastEmbeddingFunction()
        )

    def ingest_policy(self, pdf_path: str = "hr_policy.pdf"):
        """Ingests default HR SOPs into ChromaDB."""
        default_hr_sop = """
        COMPANY HR & LEAVE POLICY:
        1. Employees receive 18 days of Paid Time Off (PTO) per calendar year.
        2. HR AI Employees can auto-approve casual/sick leave requests up to 3 consecutive days.
        3. Leave requests exceeding 3 consecutive days require mandatory Human HR Manager approval.
        4. Parental leave, bereavement, or medical leave exceeding 5 days must be routed to HR Operations.
        5. Unused PTO up to 5 days can be carried over to the next year.
        """

        if not os.path.exists(pdf_path):
            self.collection.upsert(
                documents=[default_hr_sop],
                ids=["hr_default_sop"]
            )
            return "Ingested default HR policy."

        reader = PdfReader(pdf_path)
        chunks = [page.extract_text() for page in reader.pages if page.extract_text()]
        if not chunks:
            chunks = [default_hr_sop]

        ids = [f"hr_doc_page_{i+1}" for i in range(len(chunks))]
        self.collection.upsert(documents=chunks, ids=ids)
        return f"Successfully ingested {len(chunks)} HR policy pages."

    def search_hr_policy(self, query: str) -> str:
        results = self.collection.query(query_texts=[query], n_results=1)
        if results and results["documents"] and results["documents"][0]:
            return results["documents"][0][0]
        return "Standard HR Policy: Auto-approval limit for leave is up to 3 consecutive days."

def process_hr_query(text: str):
    """Processes an HR query using ChromaDB RAG storage."""
    try:
        engine = HRRAGEngine()
        engine.ingest_policy()
        policy_info = engine.search_hr_policy(text)
        return {
            "agent_name": "HR AI Agent",
            "query": text,
            "policy_retrieved": policy_info,
            "status": "SUCCESS",
            "summary": f"HR Query Evaluated. Policy Match: {policy_info[:150]}..."
        }
    except Exception as e:
        return {
            "agent_name": "HR AI Agent",
            "query": text,
            "policy_retrieved": "Standard HR Policy: 18 days PTO/yr. Up to 3 consecutive days sick/casual leave auto-approved.",
            "error": str(e),
            "summary": f"HR Query evaluated under standard company leave policies for query: '{text}'."
        }