import os, sys
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from src.SentryChain.entity.config_entity import IngestionConfig

class TextExtraction:
    def __init__(self, ingestion_config: IngestionConfig) -> None:
        self.ingestion_config = ingestion_config
        logging.info("TextExtraction initialised with paths.")

    async def llama_parse(self):
        try:
            if not self.ingestion_config.pdf_paths:
                logging.error("No PDF files found.")
                raise ValueError("No PDF files found.")

            from llama_cloud import AsyncLlamaCloud
            client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
        except Exception as e:
            logging.error("Failed to initialize llama cloud client")
            raise CustomException(e, sys)

        for pdf_path in self.ingestion_config.pdf_paths:
            try:
                logging.info(f"Starting text extraction for: {pdf_path.name}")

                with open(pdf_path, "rb") as f:
                    file_obj = await client.files.create(file=f, purpose="parse")

                result = await client.parsing.parse(
                    file_id=file_obj.id,
                    tier="agentic",
                    version="latest",
                    output_options={
                        "markdown": {
                            "tables": {
                                "output_tables_as_markdown": True
                            }
                        }
                    },
                    expand=["markdown"],
                )

                if result.markdown is None or result.markdown.pages is None:
                    logging.warning(f"No markdown returned for {pdf_path.name}, trying text fallback...")
                    full_text = result.text if isinstance(result.text, str) else str(result)
                else:
                    full_text = "\n\n".join(page.markdown for page in result.markdown.pages)

                output_file = self.ingestion_config.processed_pdf_dir / f"{pdf_path.stem}_parsed.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(full_text)

                logging.info(f"Saved: {output_file}")

            except Exception as e:
                logging.error(f"Error during text extraction of {pdf_path.name}: {str(e)}")
                raise CustomException(e, sys)