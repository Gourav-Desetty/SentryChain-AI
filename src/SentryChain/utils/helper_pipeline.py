import json, sys, asyncio
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from src.SentryChain.components.ingestion import TextExtraction
from src.SentryChain.entity.config_entity import IngestionConfig
from src.SentryChain.entity.schema import SLADocument
from src.SentryChain.logging.logger import logging
from src.SentryChain.exception.exception import CustomException

async def start_ingestion(ingestion_config: IngestionConfig):
    try:
        logging.info("Starting LlamaParse text extraction...")
        text_extraction = TextExtraction(ingestion_config=ingestion_config)
        await text_extraction.llama_parse()
        logging.info("Text Extraction phase complete.")
    except Exception as e:
        raise CustomException(e, sys)

def load_documents(ingestion_config: IngestionConfig, contract_id: str):
    try:
        text_file = ingestion_config.processed_pdf_dir / f"{contract_id}_parsed.txt"
        loader = TextLoader(file_path=str(text_file), encoding="utf-8")
        docs = loader.load()
        logging.info(f"Loaded {len(docs)} documents for contract {contract_id}")
        return docs
    except Exception as e:
        raise CustomException(e, sys)

def load_contracts(ingestion_config: IngestionConfig):
    """yields (contract_id, SLADocument) for every pdf in pdf_paths"""
    try:
        for pdf_path in ingestion_config.pdf_paths:
            contract_id = pdf_path.stem
            json_path = ingestion_config.processed_json_contract / f"{contract_id}.json"

            with open(json_path, 'r', encoding="utf-8") as f:
                sla_dict = json.load(f)

            sla = SLADocument(**sla_dict)
            logging.info(f"Loaded contract: {contract_id}")
            yield contract_id, sla
    except Exception as e:
        raise CustomException(e, sys)