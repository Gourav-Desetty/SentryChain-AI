import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

PATH = PROJECT_ROOT / "data" / "contracts"
PDF_PATHS = list(PATH.glob("*.pdf"))
PROCESSED_PDF = PROJECT_ROOT / "data" / "processed_contracts"

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

PROCESSED_JSON_CONTRACT = Path("../data/processed_contracts")
PROCESSED_JSON_CONTRACT_PATHS = list(PROCESSED_JSON_CONTRACT.glob("*.json"))

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"

PINECONE_INDEX_NAME = "sentry-chain-ai"

TARGET_CONTRACT_ID = "OnlineSvcsConsolidatedSLA(WW)(English)(January2026)CR (1)_parsed"

MODEL_NAME = "llama-3.3-70b-versatile"
CURRENT_YEAR = "2026"