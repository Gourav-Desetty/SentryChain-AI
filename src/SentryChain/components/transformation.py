import os, sys
from typing import List
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from src.SentryChain.constants import ingestion_pipeline
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DataTransformation:
    def __init__(self, chunk_size:int = ingestion_pipeline.CHUNK_SIZE,
                chunk_overlap:int = ingestion_pipeline.CHUNK_OVERLAP) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "\nClause", "\nSection", " ", ""],
            chunk_overlap=chunk_overlap,
            chunk_size=chunk_size
        )

    def split_docs(self, documents: List[Document]):
        try:
            logging.info(f"Starting splitting of {len(documents)} documents")
            split_docs = self.text_splitter.split_documents(documents=documents)
            logging.info(f"Successfully split into {len(split_docs)} chunks")

            if split_docs:
                logging.info(f"Preview of first chunk {split_docs[0].page_content[:100]}...")

            return split_docs
        except Exception as e:
            logging.error("Error occured during document splitting")
            raise CustomException(e, sys)