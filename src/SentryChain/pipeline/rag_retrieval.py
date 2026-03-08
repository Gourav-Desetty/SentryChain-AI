import os, sys
from pathlib import Path
from src.SentryChain.constants.graph_queries import GRAPH_SEARCH
from src.SentryChain.components.embedding import EmbeddingManager
from src.SentryChain.logging.logger import logging
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.entity.artifact_entity import RagRetrievalArtifact

class RagRetrieval:
    def __init__(self, embeddings: EmbeddingManager) -> None:
        self.embeddings = embeddings

    def rag_retrieval(self, query:str, supplier_name: str, index, graph) -> RagRetrievalArtifact:
        try:
            logging.info(f"Generating embeddings for the query: {query}")
            query_embedding = self.embeddings.generate_embeddings([query])

            logging.info(f"Searching Vector DB for supplier: {supplier_name}")
            # Vector search
            vector_db_result = index.query(
                vector=query_embedding,
                top_k=5,
                
                include_metadata=True,
                filter={"supplier_name": {"$eq": supplier_name}}
            )

            retrieved_vector_ids = [m['id'] for m in vector_db_result['matches']]
            logging.info(f"Vector search returned {len(retrieved_vector_ids)} candidate matches.")

            logging.info("Cross-referencing candidates with Neo4j Knowledge Graph...")
            # Graph search
            graph_context = graph.query(GRAPH_SEARCH , params={
                "supplier_name": supplier_name,  
                "vector_ids": retrieved_vector_ids 
            })

            confirmed_ids = {item['id'] for item in graph_context}

            verified_results = [m for m in vector_db_result['matches'] if m['id'] in confirmed_ids]

            # return graph_context, vector_db_result, verified_results
            rag_retrieval_artifact = RagRetrievalArtifact(
                graph_context=graph_context,
                vector_db_result=vector_db_result,
                verified_results=verified_results
            )
            logging.info("Retrieval artifact created successfully.")
            return rag_retrieval_artifact
        except Exception as e:
            logging.error(f"Failed retrieving the query: {str(e)}")
            raise CustomException(e, sys)