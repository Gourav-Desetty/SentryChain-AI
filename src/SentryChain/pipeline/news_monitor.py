import os, sys
from src.SentryChain.constants.project_constants import CURRENT_YEAR, MODEL_NAME
from src.SentryChain.constants.prompts import RISK_ANALYSIS_PROMPT, SUPPLIER_RISK_SEARCH_QUERY
from src.SentryChain.entity.artifact_entity import NewsFetchArtifact, CompareSLAArtifact, NewsArticle
from src.SentryChain.logging.logger import logging
from src.SentryChain.exception.exception import CustomException
from src.SentryChain.pipeline.rag_retrieval import RagRetrieval
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

class NewsMonitor:
    def __init__(self) -> None:
        try:
            self.groq_llm = ChatGroq(api_key=os.environ["GROQ_API_KEY"],
                                    model=MODEL_NAME,
                                    temperature=0.1)
            self.retriever = RagRetrieval()
            logging.info("NewsMonitor initialized successfully.")
        except Exception as e:
            raise CustomException(e, sys)
        


    def fetch_news(self, supplier_name, score_threshold:float = 0.5, current_year = CURRENT_YEAR) -> NewsFetchArtifact:
        try:
            logging.info(f"Fetching news for: {supplier_name}")
            tavily = TavilySearch(api_key=os.getenv('TAVILY_API_KEY'),
                                search_depth="advanced",
                                max_results=5)

            query = SUPPLIER_RISK_SEARCH_QUERY.format(supplier_name=supplier_name,
                                                        current_year=current_year)

            results = tavily.invoke(query)

            articles = [
                NewsArticle(
                    title=r.get('title', 'No Title'),
                    content=r.get('content', ''),
                    url=r.get('url', ''),
                    score=r.get('score', 0.0)
                )
                for r in results.get('results', []) if r.get('score', 0) >= score_threshold
            ]
            logging.info(f"Retrieved {len(articles)} high-confidence news articles.")
            news_fetch_artifact = NewsFetchArtifact(
                supplier_name=supplier_name,
                articles=articles
            )
            return news_fetch_artifact
        except Exception as e:
            raise CustomException(e, sys)

    def compare_sla(self, supplier_name : str, news_results : list, index, graph) -> CompareSLAArtifact:
        try:
            logging.info(f"Starting SLA risk analysis for {supplier_name}")
            news_content = "".join([f"Source:{article['title']}\n{article['content']}" for article in news_results])

            query = "service outage uptime penalty SLA breach downtime"
            artifact = self.retriever.rag_retrieval(
                query=query, 
                supplier_name=supplier_name, 
                index=index, 
                graph=graph)
            vector_texts = [match['metadata']['text'] for match in artifact.verified_results]
            graph_texts = [item['preview'] for item in artifact.graph_context]

            combined_contexts = list(set(vector_texts+graph_texts))

            final_prompt = RISK_ANALYSIS_PROMPT.format(
                news_content=news_content,
                combined_contexts="\n---\n".join(combined_contexts)
            )

            response = self.groq_llm.invoke(final_prompt)
            logging.info(f"Risk analysis complete for {supplier_name}.")
            compare_sla_artifact = CompareSLAArtifact(
                supplier_id=supplier_name,
                verdict=str(response.content),
                news_used = [a['title'] for a in news_results],
                sla_clauses_matched = combined_contexts
            )
            return compare_sla_artifact
        except Exception as e:
            logging.error(f"SLA comparison failed for {supplier_name}")
            raise CustomException(e, sys)