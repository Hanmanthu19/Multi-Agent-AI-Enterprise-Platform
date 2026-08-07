import chromadb
import logging
from app.ai.gemini_client import client

# Initialize ChromaDB persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="company_knowledge")

def add_document(doc_id: str, text: str):
    """Add or update company knowledge documents in ChromaDB using upsert"""
    try:
        collection.upsert(
            documents=[text],
            ids=[doc_id]
        )
        return {"status": "success", "message": f"Document '{doc_id}' indexed successfully."}
    except Exception as e:
        logging.error(f"ChromaDB upsert error for document '{doc_id}': {e}")
        raise RuntimeError(f"Failed to index document '{doc_id}': {str(e)}")

def get_relevant_context(user_prompt: str) -> str:
    """Queries ChromaDB for context without directly calling Gemini API"""
    try:
        results = collection.query(
            query_texts=[user_prompt],
            n_results=2
        )
        if results and results.get('documents') and len(results['documents']) > 0:
            return " ".join(results['documents'][0])
    except Exception as e:
        logging.warning(f"ChromaDB retrieval warning: {e}")
    return ""

def query_knowledge_base(user_prompt: str) -> str:
    """Queries ChromaDB context and answers using Gemini API with exception handling"""
    context = get_relevant_context(user_prompt)
    augmented_prompt = f"Company Knowledge Base Context:\n{context}\n\nUser Task Request:\n{user_prompt}"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=augmented_prompt
        )
        return response.text
    except Exception as e:
        logging.error(f"Gemini API generation error: {e}")
        raise RuntimeError(f"Gemini API processing failed: {str(e)}")
