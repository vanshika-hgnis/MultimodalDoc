📘 MultimodalDoc — RAG Architecture Documentation
1️⃣ System Overview

MultimodalDoc is a Retrieval-Augmented Generation (RAG) system that:

Ingests PDFs

Extracts:

Text blocks

Table blocks

Bounding boxes

Stores structured blocks in PostgreSQL (Supabase)

Generates embeddings (768-dim vectors)

Performs hybrid retrieval:

Vector similarity (pgvector HNSW)

Full-text search (tsvector + GIN)

Uses LLM (Ollama Cloud) for grounded answer generation

2️⃣ Database Schema
documents

Stores uploaded files metadata.

Column	Type
id	uuid (PK)
filename	text
mime_type	text
size	bigint
storage_path	text
status	text
created_at	timestamptz
text_blocks

Extracted raw text segments.

Column	Type
id	uuid
document_id	uuid
page_number	int
text	text
bbox	jsonb
embedding	vector(768)
fts	tsvector
source_type	text

Indexes:

HNSW vector index

GIN full-text index

table_blocks

Extracted tables stored as markdown + json.

Column	Type
id	uuid
document_id	uuid
page_number	int
table_markdown	text
table_json	jsonb
bbox	jsonb
embedding	vector(768)

Index:

HNSW vector index

3️⃣ Embedding Strategy

Dimension: 768
Distance metric: L2

Similarity normalization:

(1.0 / (1.0 + (embedding <-> query_embedding)))

This converts distance → similarity score between (0,1].

4️⃣ Hybrid Retrieval Strategy

Pipeline:

Compute query embedding

Run vector similarity on:

text_blocks

table_blocks

Run keyword FTS match on text_blocks

Merge results

Apply boost:
score += rank * 0.6

Deduplicate

Sort by score descending

Return top K

This creates:

Vector + Semantic + Keyword hybrid retrieval.

5️⃣ RAG Answer Flow
User Query
    ↓
retrieve_evidence()
    ↓
Top-K context blocks
    ↓
LLM prompt injection
    ↓
Ollama Cloud chat
    ↓
Answer + sources

Safety guard:
If no evidence → return fallback.

6️⃣ API Endpoints
Upload (existing)

POST /documents

Embed

POST /documents/{id}/embed

Triggers Celery async embedding.

Retrieve

POST /rag/retrieve

Returns:

block_type

page_number

content

bbox

score

Answer

POST /rag/answer

Returns:

answer

sources (retrieved blocks)

7️⃣ Performance Characteristics

Vector Search:
O(log n) approximate search using HNSW

FTS Search:
GIN indexed

Hybrid merging:
O(n) small K

LLM latency:
Dependent on Ollama Cloud model

8️⃣ Known Limitations (Current Phase)

• Images not yet embedded
• Table semantic weighting same as text
• No reranking model
• No cross-encoder re-scoring
• No query rewriting
• No caching
• No chunk overlap

These are Phase 2 improvements.

9️⃣ Architecture Diagram (Conceptual)
Frontend UI
    ↓
FastAPI
    ↓
rag_service.py
    ↓
Supabase (pgvector + FTS)
    ↓
Ollama Cloud
🔟 What You Have Built (Objectively)

This is no longer beginner RAG.

You now have:

• Hybrid retrieval
• Table-aware search
• HNSW indexing
• Production-grade schema
• Cloud LLM integration
• Async processing pipeline

That is real architecture.