import os, sys
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from pinecone import Pinecone, ServerlessSpec
from src.SentryChain.constants.project_constants import PINECONE_INDEX_NAME

class VectorStoreMangaer:
    def __init__(self, index_name: str = PINECONE_INDEX_NAME) -> None:
        self.index_name = index_name
        self.pc = pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = None
        self.initialize_index()

    def initialize_index(self):
        try:
            if not self.pc.has_index(self.index_name):
                logging.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1024, 
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"Manual index '{self.index_name}' created.")

            self.index = self.pc.Index(self.index_name)
            logging.info(f"Connected to pinecone index: {self.index_name}")
        except Exception as e:
            logging.error("Error connecting to pinecone database")
            raise CustomException(e, sys)

