# 📄 SLA Dataset & Pipeline
 
## 📦 1. Raw Data Sources
 
| Contract | Version | Description |
|----------|---------|-------------|
| [Microsoft Online Services SLA](https://www.microsoft.com/licensing/docs/view/Service-Level-Agreements-SLA-for-Online-Services?lang=1) | Jan 2026 | Official uptime commitments for Microsoft Online Services |
| **Mazagon Dock Shipbuilders (MDL) SLA** | 2023–2025 | Rate contract for industrial subcontracting services |
 
---
 
## 🔵 Phase 1 — Building the Digital Brain
 
### 2. SLA Dataset Goals
 
#### 📥 Ingestion
- Extract all **text and tables** from SLA PDFs using `LlamaParse`
- Store retrieved content in separate `.txt` files per contract
 
#### ✂️ Chunking & Embedding
- Load `.txt` files and perform chunking using `RecursiveCharacterTextSplitter`
  - Chunk size: `1200` | Overlap: `200`
  - Separators: `["\nClause", "\nSection", " ", ""]`
- Generate dense embeddings using **`BAAI/bge-m3`** (1024 dimensions)
 
#### 🗄️ Storage
- Push chunks with unique IDs to:
  - **Neo4j** — graph database storing supplier → contract → chunk relationships
  - **Pinecone** — vector database storing embeddings + metadata + raw text
 
#### 🔍 Retrieval
```
User Query + Supplier Name
        ↓
Pinecone Vector Search (top-k chunks)
        ↓
Neo4j Cross-Reference (confirm supplier ownership)
        ↓
Combined Context (vector + graph)
        ↓
LLM Response
```
 
---
 
## 🔴 Phase 2 — The News Monitor
 
### 3. SLA Violation Detection Pipeline
 
```
Tavily Search (per supplier)
        ↓
News Snippets
        ↓
Embed Snippet → Pinecone Query → Matching SLA Chunks
        ↓
Graph Query (Neo4j) → Confirm Supplier Ownership
        ↓
LLM Prompt (news + clauses) → Violation Verdict
        ↓
Risk Report
```