# SLA Dataset

## 1. Raw Data Sources
* **Microsoft Online Services SLA:** (Jan 2026) Official commitments for uptime. [https://www.microsoft.com/licensing/docs/view/Service-Level-Agreements-SLA-for-Online-Services?lang=1]
* **NABARD BIRD SLA:** (2024) Institutional agreement for digital solutions.

# Phase 1

## 2. SLA dataset goals
* Retrieve all the text and the tables from the SLA's
* Store all the retrieved text and tables in a separate txt files
* Retrieve the .txt files perform chunking (*RecursiveCharacterTextSplitter*)
* Make a metadata for each chunks and store in the respective document 
* Use *BAAI/bge-m3* as embedding manager
* Push the chunks with unique id to the graph database (*Neo4j*) and perform embedding on the chunks and push the embeddings + metadata + text to the *pinecone* database
* Search for the query (*user_input*) and the supplier_name (*user_input*) from the pinecone and graph db 
* Combine both contexts from graphdb and pinecone 
* Push the combined contexts to the llm 

# Phase 2

Tavily Search (per supplier)
        ↓
News Snippets
        ↓
Embed snippet → Pinecone Query → Matching SLA Chunks
        ↓
Graph Query (Neo4j) → Confirm supplier ownership
        ↓
LLM Prompt (news + clauses) → Violation verdict
        ↓
Risk Report / Neo4j NewsEvent node