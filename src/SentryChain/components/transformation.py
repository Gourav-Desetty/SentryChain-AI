import os, sys
from typing import List
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from src.SentryChain.entity.config_entity import DataTransformationConfig
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class DataTransformation:
    def __init__(self, data_transformation_config: DataTransformationConfig) -> None:
        self.data_transformation_config = data_transformation_config
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "\nClause", "\nSection", " ", ""],
            chunk_overlap=data_transformation_config.chunk_overlap,
            chunk_size=data_transformation_config.chunks_size
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