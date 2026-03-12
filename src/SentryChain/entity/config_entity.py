import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from src.SentryChain.constants.project_constants import(
    PDF_PATHS, PROCESSED_PDF, CHUNK_SIZE, CHUNK_OVERLAP, 
    EMBEDDING_MODEL_NAME, PINECONE_INDEX_NAME, PROCESSED_JSON_CONTRACT,
    PROCESSED_JSON_CONTRACT_PATHS
)

BASE_DIR = Path(__file__).resolve().parents[3]  

class IngestionConfig:
    def __init__(self):
        self.contracts_dir = BASE_DIR / "data" / "contracts"
        self.processed_pdf_dir = BASE_DIR / "data" / "processed_contracts"
        self.processed_json_contract = BASE_DIR / "data" / "processed_contracts"
        self.pdf_paths = list(self.contracts_dir.glob("*.pdf"))


@dataclass
class DataTransformationConfig:
    chunks_size: int = CHUNK_SIZE
    chunk_overlap: int = CHUNK_OVERLAP

@dataclass
class EmbeddingConfig:
    model_name:str = EMBEDDING_MODEL_NAME

@dataclass
class PineconeConfig:
    index_name: str = PINECONE_INDEX_NAME
    index_dimension: int = 1024
    metric: str = "cosine"
    api_key:Optional[str] = field(default_factory=lambda: os.getenv('PINECONE_API_KEY'))

@dataclass
class Neo4jConfig:
    url: Optional[str] = field(default_factory=lambda: os.getenv("NEO4J_URI"))
    username: Optional[str] = field(default_factory=lambda: os.getenv("NEO4J_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD"))
    database: str = "neo4j"