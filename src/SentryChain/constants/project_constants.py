import os
from pathlib import Path

PATH = Path("../data/contracts")
PDF_PATHS = list(PATH.glob("*.pdf"))
PROCESSED_PDF = Path("../data/processed_contracts")

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

PROCESSED_JSON_CONTRACT = Path("../data/processed_contracts")
PROCESSED_JSON_CONTRACT_PATHS = list(PROCESSED_JSON_CONTRACT.glob("*.json"))
