from typing import List
from app.rag.loader import PDFDataLoader
from app.rag.embedder import embedder
from app.rag.chroma_client import chroma_manager
from app.logger import logger

class VectorRetriever:
    def __init__(self):
        self.chroma = chroma_manager
        self.loader = PDFDataLoader()
        self._index_documents_if_empty()

    def _index_documents_if_empty(self):
        try:
            count = self.chroma.collection.count()
            if count == 0:
                logger.info("Chroma DB empty. Auto-indexing PDF files...")
                docs = self.loader.load_and_split()
                if docs:
                    texts = [doc.page_content for doc in docs]
                    metadatas = [doc.metadata for doc in docs]
                    ids = [f"doc_{i}" for i in range(len(docs))]
                    embeddings = embedder.embed_documents(texts)
                    
                    self.chroma.collection.add(
                        documents=texts,
                        embeddings=embeddings,
                        metadatas=metadatas,
                        ids=ids
                    )
                    logger.info(f"Successfully stored {len(texts)} chunks in ChromaDB.")
        except Exception as e:
            logger.error(f"Document indexing failed: {str(e)}")

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        try:
            query_embedding = embedder.embed_query(query)
            results = self.chroma.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            documents = results.get("documents", [[]])[0]
            return documents
        except Exception as e:
            logger.error(f"RAG retrieval error: {str(e)}")
            return []

retriever = VectorRetriever()