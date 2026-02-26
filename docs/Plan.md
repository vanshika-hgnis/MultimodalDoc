Phase 0 — Repo + Product Skeleton (½–1 day)

Goal: usable web app skeleton with upload UI + API running.

Deliverables

web/ (TypeScript: Next.js or React + Vite)

api/ (FastAPI)

Basic local dev run instructions (README.md)

.env.example

Done when

You can open UI, choose a file, hit upload, and API receives it.

Phase 1 — Storage + Document Registry (1 day)

Goal: upload → store → track metadata.

Use Supabase

Supabase Storage bucket: documents

Supabase Postgres tables: documents, pages

Deliverables

Upload endpoint: POST /documents/upload

Stores file in Supabase bucket

Inserts row in documents:

id, filename, mime, size, storage_path, status, created_at

Done when

Upload returns {document_id}

Supabase bucket contains file

Postgres shows document row

Phase 2 — PDF Parsing (text-first, no OCR yet) (1–2 days)

Goal: extract real PDF text with page mapping.

Tools

pypdf or (better for layout) PyMuPDF (fitz) for page text + bbox

Deliverables

Worker task ingest_document(document_id)

Extract per-page text blocks:

page_number

text

(optional now) bbox if using PyMuPDF

Store to table text_blocks

Done when

Document status changes: uploaded -> parsed

You can query /documents/{id}/pages and see extracted text by page

Phase 3 — OCR for Scans (2–4 days)

Goal: scanned PDFs/images become searchable too.

OCR options

Tesseract OCR (free, offline)

pytesseract + OpenCV preprocessing

Later upgrade: docTR / PaddleOCR (better accuracy)

Deliverables

Detect pages with no extractable text → run OCR

Store OCR text blocks in the same schema as text blocks

Add source_type: pdf_text | ocr_text

Done when

Upload a scanned PDF and you still get searchable text output

Phase 4 — Table Extraction (2–4 days)

Goal: tables preserved as structured evidence.

Options

camelot (works well for lattice tables; requires Ghostscript)

tabula (Java dependency)

pdfplumber (more flexible)

If OCR tables: use OCR + table detection later

Deliverables

Extract tables per page

Store as:

table_markdown

table_csv

bbox

page_number

tables table in Postgres

Done when

UI can show extracted tables for a PDF page

Tables are not “lost into text”

Phase 5 — Layout + Source Highlighting (HIGH VALUE) (3–6 days)

Goal: “highlights sources” requirement — you need bbox and viewer integration.

Backend deliverables

Store bbox for each block:

text blocks

tables

images/figures (optional)

Endpoint:

GET /documents/{id}/evidence?page=3 returns blocks + bbox

Frontend deliverables

PDF viewer (react-pdf / pdfjs)

Draw highlight rectangles on top of PDF canvas using bbox coords

Done when

Clicking a text/table block highlights exact region on the PDF page

This is a huge “impress them” feature because it proves traceability.

Phase 6 — Multimodal Extraction Model (2–6 days)

Goal: structured fields extraction + better table understanding using a model.

What this means practically

From document you want:

key-value fields (dates, IDs, names)

consistent schema output

confidence score

references to evidence blocks used

Deliverables

Define Pydantic schemas:

InvoiceSchema, SurveySchema, etc. (start with ONE domain)

Extraction endpoint:

POST /documents/{id}/extract?schema=survey_v1

Output:

JSON object validated by Pydantic

Each extracted field includes:

value

confidence

evidence_block_id

Done when

You can extract a structured JSON from the PDF + show “field → source highlight”

Phase 7 — Search + Retrieval Ready (optional but future-proof) (2–4 days)

Even if your current goal is “intake pipeline”, you should prepare it for RAG.

Deliverables

Add embeddings for blocks (Ollama embeddings)

Store in pgvector (Supabase supports extensions if enabled)

Endpoint POST /search returning block IDs + bbox

Done when

“Search within PDFs” works even without LLM answering

Phase 8 — Production Hardening (1–3 days)

Goal: make it look like real engineering.

Deliverables

async jobs + status tracking

retry logic for OCR/table extraction

job logs table

rate limiting

basic auth (Supabase Auth or JWT)

Done when

ingestion is reliable and observable

What order should you build in (best demo velocity)

Upload + registry (Phase 1)

Text extraction (Phase 2)

OCR fallback (Phase 3)

Tables (Phase 4)

Highlighting (Phase 5) ✅ strongest demo

Structured extraction (Phase 6)
