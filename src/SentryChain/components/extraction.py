import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from llama_cloud import ExtractConfig, ExtractMode, ExtractTarget
from llama_cloud.client import AsyncLlamaCloud

from src.SentryChain.entity.config_entity import IngestionConfig
from src.SentryChain.entity.schema import SLADocument
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging


class SlaMetadataExtraction:
    def __init__(self, ingestion_config: IngestionConfig) -> None:
        self.ingestion_config = ingestion_config
        self.schema = SLADocument.model_json_schema()
        logging.info("SlaMetadataExtraction initialized with schema and paths.")

    async def run_extraction(self, pdf_path: Optional[Path] = None) -> None:
        try:
            logging.info("Starting LlamaCloud extraction client...")
            client = AsyncLlamaCloud(
                token=os.getenv("LLAMA_CLOUD_API_KEY"), timeout=600
            )
        except Exception as e:
            logging.error("Failed to initialize LlamaCloud client.")
            raise CustomException(e, sys)

        # If a specific path is provided, use it; otherwise, use all paths from config
        paths_to_process = [pdf_path] if pdf_path else self.ingestion_config.pdf_paths

        for pdf in paths_to_process:
            try:
                logging.info(f"Starting metadata extraction for: {pdf.name}")

                # upload file
                with open(pdf, "rb") as f:
                    file_obj = await client.files.upload_file(upload_file=f)

                # start extraction job
                job = await client.llama_extract.extract_stateless(
                    file_id=file_obj.id,
                    data_schema=self.schema,
                    config=ExtractConfig(
                        extraction_target=ExtractTarget.PER_DOC,
                        extraction_mode=ExtractMode.PREMIUM,
                    ),
                )

                # poll until done
                while job.status == "PENDING":
                    await asyncio.sleep(2)
                    job = await client.llama_extract.get_job(job.id)

                TERMINAL_STATES = {"SUCCESS", "FAILED", "CANCELLED", "ERROR"}
                while job.status not in TERMINAL_STATES:
                    await asyncio.sleep(5)
                    job = await client.llama_extract.get_job(job.id)

                result_set = await client.llama_extract.get_job_result(job.id)
                logging.info(f"Raw result: {result_set.data}")

                if isinstance(result_set.data, dict):
                    sla = SLADocument(**result_set.data)
                elif isinstance(result_set.data, list) and len(result_set.data) > 0:
                    sla = SLADocument(**result_set.data[0])
                else:
                    logging.warning(f"Unexpected result format: {type(result_set.data)}")
                    sla = SLADocument()

                output_path = self.ingestion_config.processed_pdf_dir / f"{pdf.stem}.json"
                output_path.write_text(
                    sla.model_dump_json(indent=2, exclude_none=True), encoding="utf-8"
                )
                logging.info(f"Saved extracted metadata to {output_path}")

                if sla.supplier_info:
                    logging.info(
                        f"Detected Provider: {sla.supplier_info.service_provider_name}"
                    )
                if sla.uptime_commitments:
                    logging.info(
                        f"Detected Uptime: {sla.uptime_commitments.guaranteed_uptime_percent}%"
                    )
                else:
                    logging.warning(f"uptime_commitments not found in {pdf.name}")

            except Exception as e:
                logging.error(f"Error during extraction of {pdf.name}: {str(e)}")
                raise CustomException(e, sys)
