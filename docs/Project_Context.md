Sure! Below is a **detailed breakdown** of your **MultimodalDoc (Single PDF Chat)** project, including its code structure, database schema, API endpoints, current state, future features, and overall goals. This should give you a comprehensive view of the project and help you move forward with it efficiently.

---

## **Project Name:**

**MultimodalDoc (Single PDF Chat)**

### **Overview:**

MultimodalDoc is a document-based interactive system that allows users to upload, process, and query PDFs for relevant information. This system is based on a **Retrieval-Augmented Generation (RAG)** model, which allows answering questions based on the content of documents (primarily text and tables). The goal is to help users interact with the document's content dynamically and retrieve evidence-backed answers.

### **Project Goals:**

* **Efficient Document Interaction**: Upload PDFs, extract their content, and answer user queries with evidence-based responses.
* **Multimodal Retrieval**: The system can handle both text and table-based content, providing relevant data for more structured queries.
* **User-Friendly Interface**: Simple chat-based interaction for users to ask questions, select documents, and view results.

---

## **Code File Structure:**

### **Frontend (React-based Application)**:

```
frontend/
│
├── components/
│   ├── AssistantMessage.tsx       # Displays the assistant's response with citations.
│   ├── SourcePreview.tsx          # Previews the source when hovering over citations.
│   ├── CitationInline.tsx         # Inline citations to link evidence.
│   └── DocumentSelect.tsx         # Dropdown for selecting documents.
│
├── pages/
│   ├── index.tsx                  # Main chat interface page (handle state, interactions).
│
├── styles/
│   └── tailwind.css                # Tailwind CSS for UI styling.
│
├── utils/
│   └── fetchDocuments.ts          # Helper functions to fetch documents from backend.
│
├── public/
│   └── assets/                    # Static files (icons, logos, etc).
│
└── package.json                   # Dependencies for React frontend.
```

### **Backend (API Service for Document Processing)**:

```
api/
│
├── ingestion.py                   # Handles document ingestion and parsing (OCR + text extraction).
├── rag_service.py                 # Handles the retrieval of relevant data and generates answers.
├── supabase_client.py             # Interacts with Supabase (storing documents, embeddings).
├── embedding_service.py           # Service for generating embeddings from the text content.
├── ocr_service.py                 # Handles OCR-based text extraction for image-based PDFs.
├── app.py                         # Main API server (FastAPI) that integrates all services.
└── requirements.txt               # Python dependencies for the backend.
```

### **Database Schema (Supabase/PostgreSQL)**:

Supabase is used for both document storage and metadata management. The following tables are essential for document handling:

#### **1. Documents Table:**

Stores metadata for each uploaded document.

```
documents
| id           | UUID, PRIMARY KEY   |
| filename     | VARCHAR(255)         |
| storage_path | TEXT                 |
| status       | TEXT                 |
| created_at   | TIMESTAMP            |
| updated_at   | TIMESTAMP            |
```

#### **2. Text Blocks Table:**

Stores the extracted text blocks from the document.

```
text_blocks
| id           | UUID, PRIMARY KEY   |
| document_id  | UUID, FK -> documents.id  |
| page_number  | INTEGER             |
| text         | TEXT                |
| bbox         | JSONB               |
| source_type  | TEXT (pdf_text, ocr_text) |
| similarity   | FLOAT               |
| created_at   | TIMESTAMP           |
```

#### **3. Table Blocks Table:**

Stores extracted table data from the PDF.

```
table_blocks
| id           | UUID, PRIMARY KEY   |
| document_id  | UUID, FK -> documents.id |
| page_number  | INTEGER             |
| table_markdown | TEXT              |
| table_json   | JSONB               |
| bbox         | JSONB               |
| created_at   | TIMESTAMP           |
```

#### **4. Embeddings Table:**

Stores embeddings for text data for retrieval and similarity matching.

```
embeddings
| id           | UUID, PRIMARY KEY   |
| document_id  | UUID, FK -> documents.id |
| embedding    | VECTOR (768 dimensions) |
| created_at   | TIMESTAMP           |
```

---

## **API Endpoints:**

### **1. Document Upload:**

* **POST `/documents/upload`**: Uploads a PDF document.

  * **Request Body**: FormData (file)
  * **Response**: Document ID and filename.

### **2. Document Parsing:**

* **POST `/documents/{document_id}/parse`**: Parses the uploaded document and extracts text and tables.

  * **Request**: Document ID in the URL.
  * **Response**: Status message ("Parsing started").

### **3. Document Embedding:**

* **POST `/documents/{document_id}/embed`**: Embeds the parsed content into vector space for efficient retrieval.

  * **Request**: Document ID in the URL.
  * **Response**: Status message ("Embedding complete").

### **4. Document Retrieval (RAG Answering):**

* **POST `/rag/answer`**: Receives a query and retrieves relevant answers based on the document content.

  * **Request Body**: `{ document_id: string, query: string, k: integer }`
  * **Response**: `{ answer: string, sources: array }`
  * **Explanation**: Retrieves `k` most relevant document blocks (text or table) and uses the RAG model to answer the query.

### **5. List Documents:**

* **GET `/documents`**: Retrieves a list of uploaded documents.

  * **Response**: Array of documents with `id` and `filename`.

---

## **Current State and Functionality:**

1. **Document Upload**:

   * Users can upload PDFs to the backend.
   * The uploaded PDF is processed for text and table extraction using **`pdfplumber`** and **`fitz`**.
   * If any images are detected in the PDF, **OCR (Optical Character Recognition)** is applied using **`ocr_service.py`** to extract text from images.

2. **Document Processing**:

   * After extraction, both text blocks and table blocks are stored in **Supabase**.
   * Embeddings for the extracted content are generated and stored for efficient similarity search and retrieval.

3. **User Interaction**:

   * Users select a document from the list and ask questions related to its content.
   * The **RAG system** uses **Embeddings** for similarity matching, retrieving the most relevant sections of the document.
   * The assistant provides an answer along with citations (which are text or table excerpts from the document).

---

## **Future Features:**

1. **Enhanced Document Types**: Currently, only PDFs are supported, but future work could include adding support for other document types like Word, Excel, and images.
2. **Multimodal Inputs**: Implement support for multimodal queries, where the user can ask questions about images (e.g., images in the document).
3. **Advanced Query Capabilities**: Allow users to ask more complex questions, such as searching by topics or specific keywords.
4. **Real-time Collaboration**: Implement real-time collaboration where multiple users can interact with the document at the same time.
5. **Exporting Results**: Users could export their conversation and the citations in a downloadable format, like PDF or CSV.

---

## **End Goal:**

The goal of this project is to create a dynamic and interactive document-based querying system where users can upload documents, ask questions, and get answers with evidence directly from the document content. This system could be expanded to be used in educational, research, and corporate environments where document-heavy data needs to be queried interactively and efficiently.

The end goal is to make this a fully automated system for information retrieval from documents, ensuring fast, accurate, and context-backed answers for the user.

---

### **Next Steps:**

1. **Fix Hydration Issues**: Address the mismatch in hydration during the rendering process. This can be resolved by ensuring consistent state management between server-side and client-side React rendering.
2. **Test RAG Model**: Ensure that the RAG model is fetching the correct and relevant content based on user queries.
3. **Refine the Database Schema**: Review the schema for further optimization, particularly the embedding and table data storage.
4. **User Testing**: Test the entire workflow with real users to ensure usability and refine based on feedback.

Let me know if you need further clarification on any part or if you'd like help with the next steps!
