import os, sys, json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
from src.SentryChain.components.transformation import DataTransformation
from src.SentryChain.components.embedding import EmbeddingManager
from src.SentryChain.components.vector_db import VectorStoreMangaer
from src.SentryChain.components.graph_db import GraphStoreManager
from src.SentryChain.pipeline.ingestion_pipeline import DataIngestion
from src.SentryChain.pipeline.news_monitor import NewsMonitor
from src.SentryChain.pipeline.rag_retrieval import RagRetrieval
from src.SentryChain.entity.config_entity import (
    IngestionConfig, DataTransformationConfig,
    EmbeddingConfig, PineconeConfig, Neo4jConfig,
)
from src.SentryChain.utils.helper_pipeline import load_documents
from src.SentryChain.entity.schema import SLADocument
from src.SentryChain.logging.logger import logging

from pydantic import BaseModel
from pydantic import SecretStr
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

#----------------------request models-----------------------------------------#

class QueryRequest(BaseModel):
    question: str
    contract_id: str

class MonitorRequest(BaseModel):
    contract_id: str

ingestion_config = IngestionConfig()
data_transformation = DataTransformation(DataTransformationConfig())
embedding_manager = EmbeddingManager(EmbeddingConfig())
vector_store = VectorStoreMangaer(PineconeConfig())
graph_store = GraphStoreManager(Neo4jConfig())
rag_retrieval = RagRetrieval(embeddings=embedding_manager)
news_monitor = NewsMonitor(retriever=rag_retrieval)
data_ingestion = DataIngestion(
    transformer=data_transformation,
    ingestion_config=ingestion_config,
)

services = {}
#---------------------initialising all the services----------------------------#

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up SentryChain services...")

    llm = ChatGroq(
        api_key=SecretStr(os.environ["GROQ_API_KEY"]),
        model="llama-3.3-70b-versatile",
        temperature=0.1,
    )

    services["dense_index"] = vector_store.index
    services["graph"] = graph_store.graph
    services["llm"] = llm

    logging.info("All services initialised.")

    yield  

    logging.info("Shutting down SentryChain services...")
    services.clear()
    logging.info("Shutdown complete.")




app = FastAPI(lifespan=lifespan)



#-------------------------Helper----------------------------------------------#

def get_supplier_name(contract_id: str):
    """Read supplier name from the processed json contracts"""
    json_file = ingestion_config.processed_pdf_dir / f"{contract_id.replace("_parsed", "")}.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    data = json.loads(json_file.read_text(encoding='utf-8'))
    return data.get("supplier_info", {}).get("service_provider_name", "Unknown")


#-----------------------------Routes------------------------------------------#

@app.get('/')
def root():
    return {
        "message" : "SentryChainAI is running" 
    }

@app.get("/contracts")
def list_contracts():
    """list all the contracts"""
    contracts = []
    for txt_file in ingestion_config.processed_pdf_dir.glob("*_parsed.txt"):
        contract_id = txt_file.stem
        supplier_name = get_supplier_name(contract_id)
        contracts.append({"Contract_id": contract_id, "supplier_name": supplier_name})
    return {"Contracts": contracts}

@app.get('/contracts/{contract_id}')
def get_contract(contract_id: str):
    """Get the structured SLA metadata"""
    json_file = ingestion_config.processed_pdf_dir / f"{contract_id.replace('_parsed', '')}.json"
    if not json_file.exists():
        raise HTTPException(status_code=404, detail=f"Contract {contract_id} not found")
    data = json.loads(json_file.read_text(encoding='utf-8'))
    return {
        "Contract": contract_id,
        "Metadata": data
    }

@app.post('/ingest')
async def ingest_contract(file: UploadFile = File(...)):
    """ingest contracts"""
    file_name = file.filename
    if not file_name or not file_name.lower().endswith('.pdf'):
        raise HTTPException(status_code=404, detail="Only PDF files are supported")

    save_path = ingestion_config.contracts_dir / file_name
    save_path.write_bytes(await file.read())

    contract_id = Path(file_name).stem

    try:
        from src.SentryChain.components.ingestion import TextExtraction
        from src.SentryChain.components.extraction import SlaMetadataExtraction
        # parse text
        text_extraction = TextExtraction(ingestion_config=ingestion_config)
        await text_extraction.llama_parse()

        # extract metadata
        sla_metadata = SlaMetadataExtraction(ingestion_config=ingestion_config)
        sla_metadata.run_extraction()

        # chunks, embedding and store
        json_path = ingestion_config.processed_pdf_dir / f"{contract_id}.json"
        sla = SLADocument(**json.loads(json_path.read_text(encoding='utf-8')))

        docs = load_documents(
            ingestion_config=ingestion_config,
            contract_id=contract_id
        ) 
        chunks = data_transformation.split_docs(documents=docs)
        embeddings = embedding_manager.generate_embeddings([c.page_content for c in chunks])

        data_ingestion.data_ingestion(
            sla_data=sla,
            contract_id=contract_id,
            contract_chunks=chunks,
            embeddings=embeddings,
            dense_index=services["dense_index"],
            graph=services["graph"]
        )

        return {
            "message": f"Contract {contract_id} successfully ingeseted."
        }
    except Exception as e:
        logging.error(f"Ingestion failes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def rag_query(request: QueryRequest):
    """Ask question about contract"""
    supplier_name = get_supplier_name(request.contract_id)

    artifact = rag_retrieval.rag_retrieval(
        query=request.question,
        supplier_name=supplier_name,
        contract_id=request.contract_id,
        index=services["dense_index"],
        graph=services["graph"]
    )

    vector_texts = [m['metadata']['text'] for m in artifact.verified_results]
    graph_texts = [item['preview'] for item in artifact.graph_context]
    combined_results = list(set(vector_texts + graph_texts))

    prompt = f"""You are a contract analyst. Answer using ONLY the context below.
            Context:
            {chr(10).join(combined_results)}

            Question: {request.question}
            Answer (cite clause numbers where possible):"""

    response = services["llm"].invoke(prompt)

    return {
        "contract_id": request.contract_id,
        "supplier_name": supplier_name,
        "answer": response.content,
        "sources": [m["id"] for m in artifact.verified_results[:3]]
    }


@app.post('/monitor')
def monitor_sla(request: MonitorRequest):
    """fetch latest news and check for sla breaches"""
    supplier_name = get_supplier_name(contract_id=request.contract_id)

    news_artifact = news_monitor.fetch_news(supplier_name=supplier_name)

    if not news_artifact:
        return {
            "contract_id": request.contract_id,
            "supplier_name": supplier_name,
            "message": "No news found"
        }
    
    compare = news_monitor.compare_sla(
        supplier_name=supplier_name,
        news_results=news_artifact.articles,
        contract_id=request.contract_id,
        index=services["dense_index"],
        graph=services["graph"]
    )

    return {
        "contract_id":    request.contract_id,
        "supplier_name":  supplier_name,
        "verdict":        compare.verdict,
        "is_verified":    compare.is_verified,
        "hallucinations": compare.hallucinations,
        "news_used":      compare.news_used
    }