import os, sys
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from pinecone import Pinecone, ServerlessSpec
from src.SentryChain.entity.config_entity import Neo4jConfig
from langchain_neo4j import Neo4jGraph

class GraphStoreManager:
    def __init__(self, neo4j_config: Neo4jConfig) -> None:
        self.neo4j_config = neo4j_config
        self.graph = None
        self.connect()

    def connect(self):
        try:
            logging.info("Initializing Neo4j graph connection")
            self.graph = Neo4jGraph(
                url=self.neo4j_config.url, 
                username=self.neo4j_config.username, 
                password=self.neo4j_config.password,
                database=self.neo4j_config.database,
                refresh_schema=False
            )
            logging.info("Neo4j connection established")
            print("Neo4j connection established successfully!")  ## debugging
        except Exception as e:
            logging.warning(f"Neo4j unavailable at startup: {e}. Graph features disabled.")
            print(f"Neo4j connection failed: {e}") ## debugging
            self.graph = None