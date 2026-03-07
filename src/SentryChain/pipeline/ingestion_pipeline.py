import os, sys
from pathlib import Path
from src.SentryChain.constants.project_constants import PDF_PATHS, PROCESSED_PDF
from langchain_community.document_loaders import TextLoader
from src.SentryChain.constants.graph_queries import SUPPLIER_CONTRACT, PENALTY_NODES, CONTRACT_CHUNK_LINK
from src.SentryChain.components.transformation import DataTransformation
from src.SentryChain.logging.logger import logging
from src.SentryChain.exception.exception import CustomException
import os, sys
from pathlib import Path
from src.SentryChain.constants.project_constants import PDF_PATHS, PROCESSED_PDF
from langchain_community.document_loaders import TextLoader
from src.SentryChain.constants.graph_queries import SUPPLIER_CONTRACT, PENALTY_NODES, CONTRACT_CHUNK_LINK
from src.SentryChain.components.transformation import DataTransformation
from src.SentryChain.logging.logger import logging
from src.SentryChain.exception.exception import CustomException

class DataIngestion:
    def __init__(self):
        self.transformer = DataTransformation()

    def data_ingestion(self, 
                            sla_data, 
                            contract_id, 
                            embedding_manager, 
                            dense_index, 
                            graph, 
                            processed_pdf_path: Path = PROCESSED_PDF): 
        
        try:
            supplier_name = sla_data.supplier_info.service_provider_name if sla_data.supplier_info else "Unknown"

            text_file = processed_pdf_path / f"{contract_id}_parsed.txt"
            loader = TextLoader(file_path=str(text_file), encoding="utf-8")
            docs = loader.load()

            contract_chunks = self.transformer.split_docs(documents=docs)

            logging.info("Generating batch embeddings...")
            texts = [chunk.page_content for chunk in contract_chunks]
            batch_embeddings = embedding_manager.generate_embeddings(texts)

            graph.query(SUPPLIER_CONTRACT, params={
                "s_name": supplier_name,
                "c_id": contract_id
            })

            if sla_data.penalty_clauses:
                for idx, p in enumerate(sla_data.penalty_clauses):
                    graph.query(PENALTY_NODES, params={
                        "c_id": contract_id,
                        "p_uid": f"rule_{contract_id}_{idx}",
                        "type": p.penalty_type,
                        "trigger": p.trigger_condition,
                        "amount": p.penalty_amount,
                        "ref": p.clause_id
                    })

            for i, (chunk, emb) in enumerate(zip(contract_chunks, batch_embeddings)):
                chunk_id = f"{contract_id}#chunk{i}"

                graph.query(CONTRACT_CHUNK_LINK, params={
                    "c_id": contract_id,
                    "v_id": chunk_id,
                    "text": chunk.page_content[:200]
                })

                dense_index.upsert(vectors=[{
                    "id": chunk_id,
                    "values": emb,
                    "metadata": {
                        **chunk.metadata,
                        "text": chunk.page_content,
                        "supplier_name": supplier_name,
                    }
                }])
            
            logging.info(f"Ingestion successful for {contract_id}")

        except Exception as e:
            raise CustomException(e, sys)