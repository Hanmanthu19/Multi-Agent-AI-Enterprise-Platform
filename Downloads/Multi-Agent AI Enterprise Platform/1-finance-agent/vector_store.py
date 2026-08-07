import os
from typing import List
from langchain_core.documents import Document

class SimplePolicyVectorStore:
    """Lightweight in-memory policy retriever that requires no PyTorch, no C++ DLLs, and no API credits."""
    def __init__(self, docs: List[Document]):
        self.docs = docs

    def similarity_search(self, query: str, k: int = 2) -> List[Document]:
        return self.docs[:k]

    def as_retriever(self, search_kwargs: dict = None):
        return self

    def invoke(self, query: str) -> List[Document]:
        return self.similarity_search(query)

def initialize_policy_rag():
    """Initializes a ultra-lightweight, instant-loading local policy retriever."""
    docs = [
        Document(
            page_content="Policy SOP Section 4.1: Instant refunds up to ₹2,500 INR can be auto-processed for damaged goods within 14 days of delivery.",
            metadata={"source": "SOP_Refunds_India_v1.pdf", "section": "SOP-FIN-4.1"}
        ),
        Document(
            page_content="Policy SOP Section 4.2: Refunds exceeding ₹2,500 INR or submitted past 14 days require human manager review and explicit authorization.",
            metadata={"source": "SOP_Refunds_India_v1.pdf", "section": "SOP-FIN-4.2"}
        )
    ]
    return SimplePolicyVectorStore(docs)