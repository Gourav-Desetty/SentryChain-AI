import os, sys
from pathlib import Path
from typing import Optional
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from src.SentryChain.entity.config_entity import IngestionConfig

class TextExtraction:
    def __init__(self, ingestion_config: IngestionConfig) -> None:
        self.ingestion_config = ingestion_config
        logging.info("TextExtraction initialised with paths.")

    async def llama_parse(self, pdf_path: Optional[Path] = None):
        try:
            from llama_parse import LlamaParse
            parser = LlamaParse(
                api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
                result_type="markdown",
                verbose=True,
                language="en"
            )
        except Exception as e:
            logging.error("Failed to initialize llama parse")
            raise CustomException(e, sys)

        paths_to_process = [pdf_path] if pdf_path else self.ingestion_config.pdf_paths

        for path in paths_to_process:
            try:
                logging.info(f"Starting text extraction for: {path.name}")
                
                documents = await parser.aload_data(str(path))
                full_text = "\n\n".join([doc.text for doc in documents])

                output_file = self.ingestion_config.processed_pdf_dir / f"{path.stem}_parsed.txt"
                output_file.write_text(full_text, encoding="utf-8")

                logging.info(f"Saved: {output_file}")

            except Exception as e:
                logging.error(f"Error during text extraction of {path.name}: {str(e)}")
                raise CustomException(e, sys)