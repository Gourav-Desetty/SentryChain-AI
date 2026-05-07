import os, sys
from typing import List
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from src.SentryChain.entity.config_entity import EmbeddingConfig
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    def __init__(self, embedding_config: EmbeddingConfig):
        self.embedding_config = embedding_config
        self.model_name = embedding_config.model_name
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            logging.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logging.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logging.error("Error loading embedding model")
            raise CustomException(e, sys)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            logging.info(f"Starting embedding model: {self.model_name}")
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            # Ensure return is always List[List[float]]
            result = embeddings.astype(float).tolist()
            if result and isinstance(result[0], float):
                result = [result]
            logging.info(f"Embeddings completed for {len(texts)} texts")
            return result
        except Exception as e:
            logging.error("Error generating embeddings")
            raise CustomException(e, sys)