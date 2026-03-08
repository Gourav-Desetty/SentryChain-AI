import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from src.SentryChain.constants.project_constants import(
    PDF_PATHS, PROCESSED_PDF, CHUNK_SIZE, CHUNK_OVERLAP, 
    EMBEDDING_MODEL_NAME, PINECONE_INDEX_NAME
)

@dataclass
class IngestionConfig:
    pdf_paths: list = field(default_factory=lambda: PDF_PATHS)
    processed_pdf_dir: Path = PROCESSED_PDF

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