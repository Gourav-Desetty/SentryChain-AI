from dataclasses import dataclass
from typing import List, Any, Dict

@dataclass
class RagRetrievalArtifact:
    graph_context: List[Dict[str, Any]]
    vector_db_result: Dict[str, Any]
    verified_results: List[Dict[str, Any]]

@dataclass
class NewsArticle:
    title: str
    content: str
    url: str
    score: float

@dataclass
class NewsFetchArtifact:
    supplier_name: str
    articles: List[NewsArticle]

@dataclass
class CompareSLAArtifact:
    supplier_id: str
    verdict: str 
    news_used: List[str]
    sla_clauses_matched: List[str]
    is_verified: bool | None
    hallucinations: list

@dataclass
class InputGuardrailArtifact:
        filtered_articles: list[NewsArticle]

@dataclass
class OutputGuardrailArtifact:
    is_verified: bool | None
    hallucinations: list