import os, sys
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from pinecone import Pinecone, ServerlessSpec
from src.SentryChain.entity.config_entity import PineconeConfig

class VectorStoreMangaer:
    def __init__(self, pinecone_config: PineconeConfig) -> None:
        self.pinecone_config = pinecone_config
        self.pc = Pinecone(api_key=pinecone_config.api_key)
        self.index = None
        self.initialize_index()

    def initialize_index(self):
        try:
            if not self.pc.has_index(self.pinecone_config.index_name):
                logging.info(f"Creating Pinecone index: {self.pinecone_config.index_name}")
                self.pc.create_index(
                    name=self.pinecone_config.index_name,
                    dimension=self.pinecone_config.index_dimension, 
                    metric=self.pinecone_config.metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"Manual index '{self.pinecone_config.index_name}' created.")

            self.index = self.pc.Index(self.pinecone_config.index_name)
            logging.info(f"Connected to pinecone index: {self.pinecone_config.index_name}")
        except Exception as e:
            logging.error("Error connecting to pinecone database")
            raise CustomException(e, sys)