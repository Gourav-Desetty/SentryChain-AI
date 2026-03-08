import os, sys
from pathlib import Path
from llama_cloud import LlamaCloud
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from src.SentryChain.entity.schema import SLADocument
from src.SentryChain.entity.config_entity import IngestionConfig

class SlaMetadataExtraction:
    def __init__(self, ingestion_config : IngestionConfig) -> None:
        self.ingestion_config = ingestion_config
        self.schema = SLADocument.model_json_schema()
        logging.info("SlaMetadataExtraction initialized with schema and paths.")

    def run_extraction(self) -> None:
        try:
            logging.info("Starting Llamacloud extraction client..")
            client = LlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
        except Exception as e:
            logging.error("Failed to initialize LlamaCloud client.")
            raise CustomException(e, sys)


        for pdf in self.ingestion_config.pdf_paths:
            try:
                logging.info(f"Starting metadata extraction for: {pdf.name}")
                with open(pdf, "rb") as f:
                    file_obj = client.files.create(file=(pdf.name, f, "application/pdf"), purpose="extract")

                result = client.extraction.extract(
                    file_id=file_obj.id,
                    data_schema=self.schema,
                    config={},
                )

                # Debug: see what actually came back
                print("Raw result:", result.data)

                sla = SLADocument(**result.data)

                output_path = self.ingestion_config.processed_pdf / f"{pdf.stem}.json"
                output_path.write_text(sla.model_dump_json(indent=2, exclude_none=True), encoding="utf-8")
                logging.info(f"Successfully saved extracted metadata to {output_path}")

                # Safe access
                if sla.supplier_info:
                    logging.info(f"Detected Provider: {sla.supplier_info.service_provider_name}")
                if sla.uptime_commitments:
                    logging.info(f"Detected Uptime   : {sla.uptime_commitments.guaranteed_uptime_percent}%")
                else:
                    logging.warning(f"uptime_commitments not found in document {pdf.name}")
            except Exception as e:
                logging.error(f"Error during extraction of {pdf.name}: {str(e)}")
                raise CustomException(e, sys)