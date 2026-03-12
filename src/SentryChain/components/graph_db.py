import os, sys
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from pinecone import Pinecone, ServerlessSpec
from src.SentryChain.entity.config_entity import Neo4jConfig
from langchain_neo4j import Neo4jGraph

class GraphStoreManager:
    def __init__(self, neo4j_config: Neo4jConfig) -> None:
        try:
            self.neo4j_config = neo4j_config
            logging.info("Initializing Neo4j graph connection")
            self.graph = Neo4jGraph(
                url=neo4j_config.url, 
                username=neo4j_config.username, 
                password=neo4j_config.password,
                database=neo4j_config.database
            )
            logging.info("Neo4j connection established")
        except Exception as e:
            logging.error("")
            raise CustomException(e, sys)


