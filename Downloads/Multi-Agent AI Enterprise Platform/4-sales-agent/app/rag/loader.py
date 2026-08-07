import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.config import settings
from app.logger import logger

class PDFDataLoader:
    def __init__(self, data_dir: str = settings.DATA_DIR):
        self.data_dir = data_dir
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def load_and_split(self) -> List[Document]:
        documents = []
        if not os.path.exists(self.data_dir):
            logger.warning(f"PDF directory {self.data_dir} does not exist.")
            return documents

        files = [f for f in os.listdir(self.data_dir) if f.endswith(".pdf")]
        if not files:
            logger.warning(f"No PDFs found in {self.data_dir}")
            return documents

        for file_name in files:
            file_path = os.path.join(self.data_dir, file_name)
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source_file"] = file_name
                chunks = self.splitter.split_documents(docs)
                documents.extend(chunks)
                logger.info(f"Indexed {file_name}: {len(chunks)} chunks created.")
            except Exception as e:
                logger.error(f"Failed loading PDF {file_name}: {str(e)}")

        return documents