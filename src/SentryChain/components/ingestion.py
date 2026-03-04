import os, sys
from pathlib import Path
from llama_cloud import AsyncLlamaCloud
from src.SentryChain.constants import ingestion_pipeline
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging

# Extract text from pdf
class TextExtraction:
    def __init__(self, pdf_paths: list = ingestion_pipeline.PDF_PATHS, 
                processed_pdf_path: Path = ingestion_pipeline.PROCESSED_PDF) -> None:
        self.pdf_paths = pdf_paths
        self.processed_pdf_path = processed_pdf_path
        logging.info("TextExtraction initialsed with paths.")

    async def llama_parse(self):
        try:
            if not self.pdf_paths:
                logging.error("No PDF files found.")
                raise ValueError("No PDF files found.")
            
            client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
        except Exception as e:
            logging.error("Failed to initialize llama cloud client")
            raise CustomException(e, sys)

        for pdf_path in self.pdf_paths:
            try:
                logging.info(f"Starting text extraction for: {pdf_path.name}")

                with open(pdf_path, "rb") as f:
                    file_obj = await client.files.create(file=f, purpose="parse")

                result = await client.parsing.parse(
                    file_id=file_obj.id,
                    tier="agentic_plus",
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

                logging.info(f"Result type: {type(result)}")
                logging.info(f"Markdown: {result.markdown}")
                logging.info(f"Result keys: {result.__dict__.keys()}")

                if result.markdown is None or result.markdown.pages is None:
                    logging.warning(f"Warning: No markdown returned for {pdf_path.name}, trying text fallback...")
                    
                    markdown_result = await client.parsing.get_job_markdown(job_id=result.id)
                    full_text = markdown_result if isinstance(markdown_result, str) else str(markdown_result)
                else:
                    full_text = "\n\n".join(page.markdown for page in result.markdown.pages)

                output_file = self.processed_pdf_path / f"{pdf_path.stem}_parsed.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(full_text)

                logging.info(f"Saved: {output_file}")
            except Exception as e:
                logging.info(f"Error during text extraction of {pdf_path.name} : {str(e)}")
                raise CustomException(e, sys)