# MultimodalDoc

MultimodalDoc is a high-performance Document Intake & Extraction Pipeline that converts unstructured PDFs into structured, verifiable, and traceable data.

Built with FastAPI, Celery, Redis, and Supabase, the system supports:

- Native PDF text extraction
- OCR fallback for scanned documents
- Bounding box preservation for source traceability
- Async background processing

This project is designed as a foundation for multimodal Retrieval-Augmented Generation (RAG) systems.

---

## Features

- PDF upload with metadata registry
- Asynchronous document parsing (non-blocking API)
- Text extraction using PyMuPDF
- OCR fallback using EasyOCR
- Bounding box preservation for source highlighting
- Supabase Storage + Postgres integration
- Redis + Celery background job processing

---

## Architecture

```
Upload PDF
    ↓
Supabase Storage
    ↓
Postgres Metadata Registry
    ↓
Celery Worker (Async Ingestion)
    ↓
Text Extraction (PyMuPDF)
    ↓
OCR Fallback (EasyOCR)
    ↓
Structured text_blocks with Bounding Boxes
```

---

## Tech Stack

- FastAPI
- Celery
- Redis
- Supabase (Postgres + Storage)
- PyMuPDF
- EasyOCR
- Python 3.10+

---

## Project Structure

```
api/
│
├── main.py
├── ingestion.py
├── ocr_service.py
├── celery_app.py
├── tasks.py
├── supabase_client.py
│
├── models/
│   └── easyocr/
│
└── requirements.txt
```

---

## Database Schema

### documents

| Column       | Type        |
| ------------ | ----------- |
| id           | uuid        |
| filename     | text        |
| mime_type    | text        |
| size         | bigint      |
| storage_path | text        |
| status       | text        |
| created_at   | timestamptz |

### text_blocks

| Column      | Type        |
| ----------- | ----------- |
| id          | uuid        |
| document_id | uuid        |
| page_number | int         |
| text        | text        |
| bbox        | jsonb       |
| source_type | text        |
| created_at  | timestamptz |

---

## Setup (WSL Recommended)

### 1. Install Redis

```bash
sudo apt update
sudo apt install redis-server -y
sudo service redis-server start
```

Verify:

```bash
redis-cli ping
```

Expected output:

```
PONG
```

---

### 2. Create Virtual Environment

```bash
cd api
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install easyocr celery redis python-dotenv
```

---

### 3. Configure Supabase

Create a `.env` file inside `api/`:

```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_service_role_key
```

Use the service role key (not the anon key).

---

### 4. Download OCR Models (One-Time Setup)

Create a temporary script:

```python
from ocr_service import get_ocr_reader
get_ocr_reader()
```

Run:

```bash
python download_models.py
```

Models will be stored inside:

```
models/easyocr/
```

Delete the script afterward.

---

### 5. Start Services

Terminal 1 — FastAPI

```bash
source env/bin/activate
uvicorn main:app --reload
```

Terminal 2 — Celery Worker

```bash
source env/bin/activate
celery -A celery_app.celery worker --loglevel=info
```

---

## API Endpoints

### Upload Document

```
POST /documents/upload
```

Response:

```json
{
  "document_id": "uuid",
  "message": "Upload successful"
}
```

---

### Parse Document (Async)

```
POST /documents/{document_id}/parse
```

Starts background ingestion via Celery.

---

### Get Document Metadata

```
GET /documents/{document_id}
```

---

## Design Principles

- Non-blocking ingestion architecture
- Layout-aware extraction
- Structured evidence modeling
- OCR fallback for scanned PDFs
- Clear separation between API and worker
- Built as a foundation for multimodal RAG systems

---

## Future Improvements

- Table extraction engine
- Vector embeddings (pgvector)
- Hybrid semantic + keyword retrieval
- Interactive PDF highlight viewer
- Structured field extraction (Pydantic schemas)
- Docker & Kubernetes deployment

---

## License

MIT
