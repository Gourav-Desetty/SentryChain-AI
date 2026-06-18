# SentryChain AI

> **Autonomous SLA Violation Detection** - Reads your contracts, watches the news, and tells you when you're owed money.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://docker.com)
[![LlamaCloud](https://img.shields.io/badge/LlamaCloud-PDF_Parsing-purple)](https://llamacloud.ai)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-00BFA6)](https://pinecone.io)
[![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge_Graph-008CC1?logo=neo4j)](https://neo4j.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange)](https://groq.com)
[![RAGAS](https://img.shields.io/badge/RAGAS-Evaluated-green)](https://docs.ragas.io)

---

## The Problem

When a company pays for a cloud service like email or storage, the contract - called an **SLA (Service Level Agreement)** - guarantees things like *"99.9% uptime, or we owe you a refund."*

The problem? These contracts are **hundreds of pages of dense legal text**. When Microsoft Azure goes down for 4 hours, nobody has time to:

1. Find the right clause in the contract
2. Calculate what refund they're owed
3. File the claim before the window expires

Companies routinely lose **thousands of dollars** in entitled service credits - simply because no one was watching.

---

## The Solution

SentryChain AI is an end-to-end agentic pipeline that:

1. **Reads and understands** your SLA contracts, no matter how complex
2. **Monitors live web news** for relevant outage or breach events
3. **Generates grounded verdicts** with matching SLA clauses, penalties, and evidence

---

## System Architecture

```text
PHASE 1: INGESTION

SLA PDFs
  -> LlamaParse text extraction
  -> LlamaCloud metadata extraction
  -> Chunking and embeddings
  -> Pinecone vector index
  -> Neo4j knowledge graph

PHASE 2: MONITORING

Tavily news search
  -> Input guardrail
  -> Relevant outage/breach articles
  -> Hybrid RAG retrieval
     - Pinecone semantic search
     - Neo4j graph lookup
  -> Groq LLM analysis
  -> Output guardrail
  -> Final SLA risk verdict
```

---

## Key Features

### Hybrid RAG Retrieval

Combines **semantic vector search** with **structured graph traversal** for high-precision clause retrieval. Contract chunks are stored in Pinecone and cross-referenced through Neo4j before being passed to the LLM, reducing noise and hallucination risk.

### Two-Layer Guardrail System

| Layer | Type | What it does |
|-------|------|--------------|
| Input Guardrail | Deterministic keyword filter | Drops irrelevant news before it reaches the LLM |
| Output Guardrail | LLM-based validation | Validates numbers, percentages, and clause references in the verdict against the SLA text |

### RAGAS Evaluation

The retrieval and generation pipeline was benchmarked on a **12-question synthetic test set** built from real SLA clauses:

| Metric | Score |
|--------|-------|
| Faithfulness | ~0.97 |
| Answer Relevancy | ~0.74 |

### REST API

Full API surface for integration with existing procurement or contract management systems:

- `POST /ingest` - Upload a new SLA PDF
- `GET /contracts` - List all monitored contracts
- `POST /query` - Ask a natural language question about a contract
- `POST /monitor` - Run live news check and generate a violation verdict

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| PDF Ingestion | LlamaParse |
| Metadata Extraction | LlamaCloud structured extraction |
| Embeddings | `BAAI/bge-m3` with sentence-transformers |
| Vector Store | Pinecone |
| Knowledge Graph | Neo4j |
| News Retrieval | Tavily Search API |
| LLM | Groq - LLaMA 3.3 70B Versatile |
| Evaluation | RAGAS |
| API Framework | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Containerization | Docker + Docker Compose |
| Language | Python 3.12 |

---

## Project Structure

```text
SentryChain-AI/
|-- data/
|   |-- data.md
|   |-- contracts/                 # Place SLA PDFs here
|   `-- processed_contracts/       # Auto-generated parsed output
|-- notebooks/
|   `-- main.ipynb
|-- src/
|   |-- app.py                     # Uvicorn entrypoint
|   |-- main.py                    # CLI / full pipeline runner
|   `-- SentryChain/
|       |-- backend/
|       |   `-- app.py             # Source-of-truth FastAPI app
|       |-- api/
|       |   `-- app.py             # Compatibility import for old API path
|       |-- components/
|       |-- constants/
|       |-- entity/
|       |-- exception/
|       |-- frontend/
|       |   `-- app.py             # Streamlit UI
|       |-- logging/
|       |-- pipeline/
|       `-- utils/
|-- docker-compose.yml
|-- Dockerfile
|-- LICENSE
|-- pyproject.toml
|-- README.md
|-- requirements.txt
`-- uv.lock
```

---

## Entrypoints

The canonical FastAPI app lives at:

```text
src.SentryChain.backend.app:app
```

Use this path for Docker, Uvicorn, and deployments. The older `src.SentryChain.api.app` module is kept only as a compatibility import so existing commands do not break.

---

## Getting Started

### Prerequisites

- Python 3.12
- Docker and Docker Compose
- API keys for Groq, Pinecone, Neo4j, Tavily, and LlamaCloud

### 1. Clone and install

```bash
git clone https://github.com/Gourav-Desetty/SentryChain-AI.git
cd SentryChain-AI
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file:

```env
GROQ_API_KEY=your_key
PINECONE_API_KEY=your_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
TAVILY_API_KEY=your_key
LLAMA_CLOUD_API_KEY=your_key
```

### 3. Add your contracts

Place SLA PDF files in `data/contracts/`.

### 4. Run with Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.
Neo4j browser will be available at `http://localhost:7474`.

### 5. Run manually

```bash
# Ingest contracts and run the full pipeline
python -m src.main

# Start just the API server
python src/app.py

# Start the Streamlit UI
streamlit run src/SentryChain/frontend/app.py
```

---

## API Usage

### Upload and ingest a new contract

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@your_contract.pdf"
```

### Ask a question about a contract

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the uptime guarantee?", "contract_id": "microsoft_sla_parsed"}'
```

### Run live SLA violation check

```bash
curl -X POST http://localhost:8000/monitor \
  -H "Content-Type: application/json" \
  -d '{"contract_id": "microsoft_sla_parsed"}'
```

**Example verdict output:**

```json
{
  "supplier_name": "Microsoft",
  "verdict": "SLA VIOLATION LIKELY - HIGH SEVERITY\n\nAzure reported a 4-hour outage. Per Section 6.1, uptime below 99.9% triggers a 25% service credit...",
  "is_verified": true,
  "hallucinations": [],
  "news_used": ["Microsoft Azure Global Outage"]
}
```

---

## Contracts Used for Development

| Contract | Notes |
|----------|-------|
| Microsoft Online Services SLA | Publicly available via Microsoft Licensing Docs |
| Mazagon Dock Shipbuilders SLA | Internal procurement document - not included in repo |

---

## Deployment Note

The hosted demo may sleep because the backend, Streamlit app, and Neo4j instance use free-tier infrastructure. The project is designed to run locally with Docker for reproducible review.

---

## Roadmap

- [x] PDF ingestion pipeline with LlamaParse
- [x] Structured metadata extraction with LlamaCloud
- [x] Hybrid RAG retrieval with Pinecone and Neo4j
- [x] Live news monitoring with Tavily
- [x] Input and output guardrails
- [x] RAGAS evaluation
- [x] FastAPI REST layer
- [x] Docker and Docker Compose
- [x] Streamlit UI

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.
