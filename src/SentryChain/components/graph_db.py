import os, sys
from pathlib import Path
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.logging.logger import logging
from pinecone import Pinecone, ServerlessSpec
from src.SentryChain.constants.project_constants import PINECONE_INDEX_NAME
from langchain_community.graphs import Neo4jGraph

class GraphStoreManager:
    def __init__(self) -> None:
        try:
            logging.info("Initializing Neo4j graph connection")
            self.graph = Neo4jGraph(
                url=os.getenv("NEO4J_URI"), 
                username=os.getenv("NEO4J_USERNAME"), 
                password=os.getenv("NEO4J_PASSWORD"),
                database='neo4j'
            )
            logging.info("Neo4j connection established")
        except Exception as e:
            logging.error("")
            raise CustomException(e, sys)


