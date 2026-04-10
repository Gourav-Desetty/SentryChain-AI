# SentryChain AI 🔗⚖️

> **Autonomous SLA Violation Detection** — Reads your contracts, watches the news, and tells you when you're owed money.

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

When a company pays for a cloud service like email or storage, the contract — called an **SLA (Service Level Agreement)** — guarantees things like *"99.9% uptime, or we owe you a refund."*

The problem? These contracts are **hundreds of pages of dense legal text**. When Microsoft Azure goes down for 4 hours, nobody has time to:
1. Find the right clause in the contract
2. Calculate what refund they're owed
3. File the claim before the window expires

Companies routinely lose **thousands of dollars** in entitled service credits — simply because no one was watching.

---

## The Solution

SentryChain AI is an end-to-end agentic pipeline that:

1. **Reads and understands** your SLA contracts (no matter how complex)
2. **Monitors the internet** 24/7 for relevant outage or breach news
3. **Automatically generates verdicts** — citing exact clauses, penalties, and evidence

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PHASE 1: INGESTION                       │
│                                                                 │
│  SLA PDFs ──► LlamaParse ──► Text + Metadata ──► Chunking       │
│                                    │                            │
│                          ┌─────────┴──────────┐                 │
│                          ▼                    ▼                 │
│                    Pinecone (Vector DB)   Neo4j (Graph DB)      │
│                    "The Library"          "The Map"             │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                     PHASE 2: MONITORING                         │
│                                                                 │
│  Tavily News Search ──► Input Guardrail ──► Relevant Articles   │
│                                                  │              │
│                                    Hybrid RAG Retrieval         │
│                               (Vector Search + Graph Lookup)    │
│                                          │                      │
│                                   Groq LLM Analysis             │
│                                          │                      │
│                              Output Guardrail (Hallucination    │
│                              Check) ──► Final Verdict           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 🧠 Hybrid RAG Retrieval
Combines **semantic vector search** (Pinecone) with **structured graph traversal** (Neo4j) for high-precision clause retrieval. Only chunks that appear in *both* the vector index and the knowledge graph are passed to the LLM — reducing noise and hallucination risk.

### 🛡️ Two-Layer Guardrail System
| Layer | Type | What it does |
|-------|------|--------------|
| Input Guardrail | Deterministic (keyword filter) | Drops irrelevant news before it reaches the LLM |
| Output Guardrail | LLM-based | Validates every number, percentage, and clause reference in the verdict against the actual SLA text |

### 📊 RAGAS Evaluation
The retrieval and generation pipeline was benchmarked on a **12-question synthetic test set** built from real SLA clauses:

| Metric | Score |
|--------|-------|
| Faithfulness | ~0.98 |
| Answer Relevancy | ~0.97 |

### 🔌 REST API (FastAPI)
Full API surface for integration with existing procurement or contract management systems:
- `POST /ingest` — Upload a new SLA PDF
- `GET /contracts` — List all monitored contracts
- `POST /query` — Ask a natural language question about a contract
- `POST /monitor` — Run live news check and generate a violation verdict

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| PDF Ingestion | LlamaParse (agentic tier) |
| Metadata Extraction | LlamaCloud structured extraction |
| Embeddings | `BAAI/bge-m3` (1024-dim, sentence-transformers) |
| Vector Store | Pinecone (serverless, cosine similarity) |
| Knowledge Graph | Neo4j |
| News Retrieval | Tavily Search API |
| LLM | Groq — LLaMA 3.3 70B Versatile |
| Evaluation | RAGAS |
| API Framework | FastAPI + Uvicorn |
| Containerization | Docker + Docker Compose |
| Language | Python 3.12 |

---

## Project Structure

```
sentrychain-ai/
├── src/
│   ├── app.py                          # Uvicorn entrypoint
│   └── SentryChain/
│       ├── api/
│       │   └── app.py                  # FastAPI routes
│       ├── pipeline/
│       │   ├── ingestion_pipeline.py   # Vector + graph ingestion
│       │   ├── rag_retrieval.py        # Hybrid RAG
│       │   └── news_monitor.py         # Tavily fetch + SLA compare
│       ├── components/
│       │   ├── ingestion.py            # LlamaParse PDF extraction
│       │   ├── extraction.py           # LlamaCloud metadata extraction
│       │   ├── transformation.py       # Text chunking
│       │   ├── embedding.py            # BAAI/bge-m3 embeddings
│       │   ├── vector_db.py            # Pinecone manager
│       │   ├── graph_db.py             # Neo4j manager
│       │   └── guardrails.py           # Input + output guardrails
│       ├── entity/
│       │   ├── schema.py               # Pydantic SLA schema
│       │   ├── config_entity.py        # Configuration dataclasses
│       │   └── artifact_entity.py      # Pipeline artifact dataclasses
│       └── constants/
│           ├── project_constants.py    # Paths, model names
│           ├── prompts.py              # LLM prompt templates
│           └── graph_queries.py        # Cypher queries
├── data/
│   ├── contracts/                      # Place SLA PDFs here
│   └── processed_contracts/            # Auto-generated parsed output
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

---

## Getting Started

### Prerequisites

- Python 3.12
- Docker & Docker Compose
- API keys for: Groq, Pinecone, Neo4j (AuraDB or self-hosted), Tavily, LlamaCloud

### 1. Clone and install

```bash
git clone https://github.com/Gourav-Desetty/SentryChain-AI.git
cd sentrychain-ai
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
Neo4j browser at `http://localhost:7474`.

### 5. Run manually (without Docker)

```bash
# Ingest contracts and run the full pipeline
python -m src.main

# Or start just the API server
python src/app.py
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
  "verdict": "SLA VIOLATION LIKELY — HIGH SEVERITY\n\nAzure reported a 4-hour outage on Jan 15 2026. Per Section 6.1, uptime below 99.9% triggers a 25% service credit...",
  "is_verified": true,
  "hallucinations": [],
  "news_used": ["Microsoft Azure Global Outage — Jan 15 2026"]
}
```

---

## Contracts Used for Development

| Contract | Notes |
|----------|-------|
| Microsoft Online Services SLA (Jan 2026) | Publicly available via Microsoft Licensing Docs |
| Mazagon Dock Shipbuilders SLA | Internal procurement document — not included in repo |

---

## Roadmap

- [x] PDF ingestion pipeline (LlamaParse)
- [x] Structured metadata extraction (LlamaCloud)
- [x] Hybrid RAG retrieval (Pinecone + Neo4j)
- [x] Live news monitoring (Tavily)
- [x] Input + output guardrails
- [x] RAGAS evaluation (Faithfulness ~0.98, Relevancy ~0.97)
- [x] FastAPI REST layer
- [x] Docker + Docker Compose
- [ ] Streamlit UI
- [ ] Evidently drift monitoring
- [ ] MLflow experiment tracking

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.