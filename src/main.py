import os, sys, asyncio
from src.SentryChain.components.extraction import SlaMetadataExtraction
from src.SentryChain.components.transformation import DataTransformation 
from src.SentryChain.components.embedding import EmbeddingManager
from src.SentryChain.components.vector_db import VectorStoreMangaer
from src.SentryChain.components.graph_db import GraphStoreManager
from src.SentryChain.pipeline.ingestion_pipeline import DataIngestion
from src.SentryChain.pipeline.news_monitor import NewsMonitor
from src.SentryChain.pipeline.rag_retrieval import RagRetrieval
from src.SentryChain.logging.logger import logging
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.entity.config_entity import (
    IngestionConfig, DataTransformationConfig, EmbeddingConfig, PineconeConfig,
    Neo4jConfig
)
from src.SentryChain.utils.helper_pipeline import start_ingestion, load_contracts, load_documents
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    try:
        ingestion_config = IngestionConfig()
        asyncio.run(start_ingestion(ingestion_config=ingestion_config))

        sla_metadata_extraction = SlaMetadataExtraction(ingestion_config=ingestion_config)
        sla_metadata_extraction.run_extraction()

        data_transformation_config = DataTransformationConfig()
        data_transformation = DataTransformation(data_transformation_config=data_transformation_config)

        embedding_config = EmbeddingConfig()
        embedding_manager = EmbeddingManager(embedding_config=embedding_config)

        pinecone_config = PineconeConfig()
        vector_store_manager = VectorStoreMangaer(pinecone_config=pinecone_config)
        dense_index = vector_store_manager.index

        neo4j_config = Neo4jConfig()
        graph_store_manager = GraphStoreManager(neo4j_config=neo4j_config)
        graph = graph_store_manager.graph

        data_ingestion = DataIngestion(transformer=data_transformation,
                                        ingestion_config=ingestion_config)

        for (contract_id, sla) in load_contracts(ingestion_config=ingestion_config):
            docs = load_documents(
                ingestion_config=ingestion_config,
                contract_id=contract_id
            )

            chunks = data_transformation.split_docs(documents=docs)
            logging.info(f"Contract {contract_id} split into {len(chunks)} chunks")

            texts = [chunk.page_content for chunk in chunks]
            embeddings = embedding_manager.generate_embeddings(texts=texts)
            logging.info(f"Generated {len(embeddings)} embeddings for {contract_id}")

            data_ingestion.data_ingestion(
                sla_data=sla,
                contract_id=contract_id,
                contract_chunks=chunks,
                embeddings=embeddings,
                dense_index=dense_index,
                graph=graph
            )

        rag_retrieval = RagRetrieval(embeddings=embedding_manager)
        news_monitor = NewsMonitor(retriever=rag_retrieval)

        for (contract_id, sla) in load_contracts(ingestion_config=ingestion_config):
            supplier_name = (
                sla.supplier_info.service_provider_name 
                if sla.supplier_info and sla.supplier_info.service_provider_name 
                else "Unknown"
            )

            news_artifact = news_monitor.fetch_news(
                supplier_name=supplier_name
            )

            if not news_artifact.articles:
                logging.info(f"No relevant news found for {supplier_name}, skipping.")
                continue

            compare_sla_artifact = news_monitor.compare_sla(
                supplier_name=supplier_name,
                news_results=news_artifact.articles,
                contract_id=contract_id,
                index = dense_index,
                graph=graph
            )

            logging.info(f"\n{'='*50}")
            logging.info(f"Supplier: {supplier_name}")
            logging.info(f"Verdict: {compare_sla_artifact.verdict}")
            logging.info(f"{'='*50}\n")

            print("\n" + "="*60)
            print(f"  SUPPLIER     : {supplier_name}")
            print(f"  CONTRACT ID  : {contract_id}")
            print(f"  NEWS SOURCES : {len(compare_sla_artifact.news_used)}")
            print(f"  SLA CLAUSES  : {len(compare_sla_artifact.sla_clauses_matched)}")
            print("-"*60)
            print(f"  VERDICT:\n\n{compare_sla_artifact.verdict}")
            print("="*60 + "\n")
    except Exception as e:
        raise CustomException(e, sys)
