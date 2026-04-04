import os, sys, time
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from src.SentryChain.entity.schema import SLADocument
from src.SentryChain.entity.config_entity import IngestionConfig

class SlaMetadataExtraction:
    def __init__(self, ingestion_config: IngestionConfig) -> None:
        self.ingestion_config = ingestion_config
        self.schema = SLADocument.model_json_schema()
        logging.info("SlaMetadataExtraction initialized with schema and paths.")

    def run_extraction(self) -> None:
        try:
            logging.info("Starting LlamaCloud extraction client...")
            from llama_cloud import LlamaCloud
            client = LlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
        except Exception as e:
            logging.error("Failed to initialize LlamaCloud client.")
            raise CustomException(e, sys)

        for pdf in self.ingestion_config.pdf_paths:
            try:
                logging.info(f"Starting metadata extraction for: {pdf.name}")

                # upload file
                with open(pdf, "rb") as f:
                    file_obj = client.files.create(file=f, purpose="extract")

                # start extraction job
                job = client.extract.create(
                    file_input=file_obj.id,
                    configuration={
                        "data_schema": self.schema,
                        "extraction_target": "per_doc",
                        "tier": "agentic",
                    },
                )

                # poll until done
                while job.status not in ("COMPLETED", "FAILED", "CANCELLED"):
                    time.sleep(2)
                    job = client.extract.get(job.id)

                if job.status != "COMPLETED":
                    raise ValueError(f"Extraction job {job.status} for {pdf.name}")

                logging.info(f"Raw result: {job.extract_result}")

                sla = SLADocument(**job.extract_result)

                output_path = self.ingestion_config.processed_pdf_dir / f"{pdf.stem}.json"
                output_path.write_text(sla.model_dump_json(indent=2, exclude_none=True), encoding="utf-8")
                logging.info(f"Saved extracted metadata to {output_path}")

                if sla.supplier_info:
                    logging.info(f"Detected Provider: {sla.supplier_info.service_provider_name}")
                if sla.uptime_commitments:
                    logging.info(f"Detected Uptime: {sla.uptime_commitments.guaranteed_uptime_percent}%")
                else:
                    logging.warning(f"uptime_commitments not found in {pdf.name}")

            except Exception as e:
                logging.error(f"Error during extraction of {pdf.name}: {str(e)}")
                raise CustomException(e, sys)