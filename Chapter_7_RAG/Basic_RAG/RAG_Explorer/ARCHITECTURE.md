# RAG Explorer - System Architecture & Design

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG Explorer System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FRONTEND (React)                      │  │
│  │  - PDF Selection Interface                              │  │
│  │  - Processing Pipeline Visualization                    │  │
│  │  - Query Input & Results Display                        │  │
│  │  - Real-time Status Updates                             │  │
│  │  - Responsive Design (Mobile/Tablet/Desktop)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ▲                                    │
│                            │ HTTP/REST                          │
│                            │                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   BACKEND (Flask)                        │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │ API Layer                                          │ │  │
│  │  │ - /health, /available-pdfs, /init, /query, /stats│ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                          ▲                              │  │
│  │                          │                              │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │ Processing Pipeline                               │ │  │
│  │  │                                                    │ │  │
│  │  │  ┌──────────────┐                                │ │  │
│  │  │  │ PDF Loader   │ ─── Extract text from PDF    │ │  │
│  │  │  └──────────────┘                                │ │  │
│  │  │         │                                         │ │  │
│  │  │         ▼                                         │ │  │
│  │  │  ┌──────────────┐                                │ │  │
│  │  │  │ Text Chunker │ ─── Split into 500-char       │ │  │
│  │  │  │              │      chunks with overlap       │ │  │
│  │  │  └──────────────┘                                │ │  │
│  │  │         │                                         │ │  │
│  │  │         ▼                                         │ │  │
│  │  │  ┌──────────────────┐                            │ │  │
│  │  │  │ Embedding Engine │ ─── Generate Nomic        │ │  │
│  │  │  │ (HuggingFace)    │      vectors (768-dim)    │ │  │
│  │  │  └──────────────────┘                            │ │  │
│  │  │         │                                         │ │  │
│  │  │         ▼                                         │ │  │
│  │  │  ┌──────────────────┐                            │ │  │
│  │  │  │ ChromaDB Store   │ ─── Store vectors with    │ │  │
│  │  │  │                  │      metadata & indexing  │ │  │
│  │  │  └──────────────────┘                            │ │  │
│  │  │         │                                         │ │  │
│  │  │         ▼                                         │ │  │
│  │  │  ┌──────────────────┐                            │ │  │
│  │  │  │ Retrieval Engine │ ─── Query embedding &     │ │  │
│  │  │  │                  │      return top K chunks  │ │  │
│  │  │  └──────────────────┘                            │ │  │
│  │  │         │                                         │ │  │
│  │  │         ▼                                         │ │  │
│  │  │  ┌──────────────────┐                            │ │  │
│  │  │  │ LLM Chain        │ ─── Call Groq API with    │ │  │
│  │  │  │ (Groq Client)    │      context & generate   │ │  │
│  │  │  │                  │      answer               │ │  │
│  │  │  └──────────────────┘                            │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             EXTERNAL SERVICES                            │  │
│  │  - Groq API (LLM: Mixtral 8x7B)                         │  │
│  │  - HuggingFace (Nomic Embed Model)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             LOCAL DATA STORAGE                           │  │
│  │  - chroma_db/ (Vector database)                         │  │
│  │  - data/ (Input PDFs)                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ USER INTERACTION (Frontend)                                │
└─────────────────────────────────────────────────────────────┘
              │
              │ 1. Select PDF & Click Initialize
              ▼
┌─────────────────────────────────────────────────────────────┐
│ PDF Processing (Backend)                                  │
│                                                            │
│ Step 1: Load PDF                                          │
│   Input: File path to PDF                                │
│   Output: Raw text content                               │
│                                                            │
│ Step 2: Chunk Text                                        │
│   Input: Raw text                                         │
│   Output: List of chunks (500 chars, 100 overlap)        │
│   Example: [                                             │
│     "chunk_0": "Introduction to VWO...",                │
│     "chunk_1": "Key features include...",               │
│     ...                                                 │
│   ]                                                      │
│                                                            │
│ Step 3: Generate Embeddings                              │
│   Input: Chunks (text)                                   │
│   Model: nomic-ai/nomic-embed-text-v1.5                │
│   Output: Dense vectors (768-dimensional)               │
│                                                            │
│ Step 4: Store in ChromaDB                                │
│   Input: Vectors + metadata                              │
│   Storage: Local database (chroma_db/)                  │
│   Indexing: Cosine similarity                           │
└─────────────────────────────────────────────────────────────┘
              │
              │ 2. Send Query
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Query Processing (Backend)                                │
│                                                            │
│ Step 1: Embed Query                                       │
│   Input: User question                                   │
│   Model: Same Nomic Embed                                │
│   Output: Query vector (768-dimensional)                 │
│                                                            │
│ Step 2: Similarity Search                                │
│   Input: Query vector                                    │
│   Database: ChromaDB                                     │
│   Method: Cosine similarity                              │
│   Output: Top 4 chunks with scores                       │
│                                                            │
│ Step 3: Generate Context                                 │
│   Input: Top 4 chunks                                    │
│   Format: Concatenated text with chunk headers          │
│                                                            │
│ Step 4: LLM Generation                                   │
│   Input: System message + context + query                │
│   Model: Groq (Mixtral 8x7B)                            │
│   Output: Natural language answer                        │
└─────────────────────────────────────────────────────────────┘
              │
              │ 3. Return Results
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Display Results (Frontend)                                │
│ - Retrieved chunks with similarity scores                │
│ - Generated answer with token usage                      │
│ - Complete RAG pipeline visualization                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Component Interactions

### Backend Components

#### 1. **pdf_processor.py**
- **Responsibility**: PDF text extraction and chunking
- **Key Methods**:
  - `extract_text_from_pdf()`: Reads PDF using PyPDF2
  - `split_into_chunks()`: Intelligently chunks text
  - `process_pdf()`: End-to-end PDF processing

#### 2. **embeddings.py**
- **Responsibility**: Vector embedding and ChromaDB storage
- **Key Methods**:
  - `create_collection()`: Initialize ChromaDB collection
  - `add_chunks()`: Generate embeddings and store vectors
  - `retrieve_chunks()`: Query-based similarity search

#### 3. **llm_chain.py**
- **Responsibility**: LLM integration and answer generation
- **Key Methods**:
  - `generate_answer()`: Call Groq API with context
  - Context formatting and prompt engineering

#### 4. **app.py**
- **Responsibility**: REST API and request routing
- **Endpoints**:
  - `GET /health` - System health check
  - `GET /available-pdfs` - List available PDFs
  - `POST /init` - Initialize RAG system with PDF
  - `POST /query` - Process user queries
  - `GET /collection-stats` - Database statistics

### Frontend Components

#### 1. **RAGExplorer.jsx** (Main)
- App container and orchestration
- Manages main state and component lifecycle

#### 2. **PDFUploader.jsx** (Step 1)
- Lists available PDFs
- Handles PDF selection and initialization
- Shows processing status

#### 3. **ProcessingFlow.jsx**
- Visualizes the RAG pipeline
- Shows completion status of each step
- Displays processing statistics

#### 4. **QueryInterface.jsx** (Step 2)
- Query input interface
- Displays retrieved chunks with similarity scores
- Shows LLM-generated answer
- Displays token usage metrics

---

## 💾 Database Schema (ChromaDB)

```
Collection: pdf_chunks
├── ID: chunk_0
├── Document: "Text content..."
├── Embedding: [0.234, -0.123, ..., 0.456]  # 768 dimensions
├── Metadata: {
│   └── chunk_index: "0"
└── Distance metric: cosine

Collection: pdf_chunks
├── ID: chunk_1
├── Document: "More text..."
├── Embedding: [0.111, 0.222, ..., 0.333]
├── Metadata: {
│   └── chunk_index: "1"
...
```

---

## 🔐 API Contracts

### Initialize Endpoint
```javascript
// Request
POST /init
{
  "pdf_path": "/path/to/document.pdf"
}

// Response
{
  "status": "success",
  "message": "PDF ingested successfully",
  "pdf_info": {
    "file_name": "document.pdf",
    "total_characters": 45000,
    "total_chunks": 90
  },
  "embedding_info": {
    "status": "success",
    "chunks_added": 90,
    "collection_name": "pdf_chunks"
  },
  "collection_stats": {
    "collection_name": "pdf_chunks",
    "total_documents": 90
  }
}
```

### Query Endpoint
```javascript
// Request
POST /query
{
  "query": "What is VWO?"
}

// Response
{
  "status": "success",
  "query": "What is VWO?",
  "retrieved_chunks": [
    {
      "id": "chunk_5",
      "text": "VWO is a visual website optimizer...",
      "distance": 0.15,
      "similarity": 0.85
    },
    // ... top 4 chunks
  ],
  "answer": {
    "status": "success",
    "query": "What is VWO?",
    "answer": "VWO is a visual website optimizer that...",
    "model": "mixtral-8x7b-32768",
    "context_chunks": 4,
    "token_usage": {
      "input_tokens": 1200,
      "output_tokens": 350
    }
  }
}
```

---

## ⚙️ Configuration & Performance Tuning

### Tunable Parameters

| Parameter | Location | Default | Impact |
|-----------|----------|---------|--------|
| chunk_size | pdf_processor.py | 500 | Larger = fewer chunks, less granular |
| chunk_overlap | pdf_processor.py | 100 | More context between chunks |
| top_k | app.py (query) | 4 | Number of chunks retrieved |
| embedding_model | embeddings.py | nomic-embed-text-v1.5 | Quality of vectors |
| llm_model | llm_chain.py | mixtral-8x7b-32768 | Answer quality & speed |
| max_tokens | llm_chain.py | 1024 | Max answer length |

### Performance Optimization

1. **Embedding Generation**: 
   - Batch processing for multiple chunks
   - GPU acceleration available (HuggingFace)

2. **Vector Search**:
   - Cosine similarity (fast, suitable for 768-dim vectors)
   - Indexed storage in ChromaDB

3. **LLM Calls**:
   - Cached embeddings
   - Context-aware prompting

---

## 🧪 Testing Strategy

### Unit Tests
- PDF text extraction
- Chunking logic
- Embedding generation
- API endpoint validation

### Integration Tests
- End-to-end RAG pipeline
- API response formats
- ChromaDB interactions

### Performance Tests
- Embedding generation time
- Query retrieval speed
- LLM response time

---

## 🔄 Deployment Considerations

### Local Development
- Single machine setup
- SQLite-based ChromaDB
- Direct file access

### Production Ready
- Container orchestration (Docker/Kubernetes)
- Persistent ChromaDB storage
- Load balancing for multiple queries
- API authentication
- Rate limiting

---

## 📈 Scalability Path

```
Single PDF
    ↓
Multiple PDFs → Multiple Collections
    ↓
Distributed ChromaDB
    ↓
Multi-user queuing
    ↓
Horizontal scaling (Multiple backends)
    ↓
Enterprise RAG Platform
```

---

## 🔗 Integration Points

1. **External APIs**:
   - Groq API (LLM)
   - HuggingFace (Embeddings)

2. **Data Sources**:
   - PDF files
   - Local file system

3. **Storage**:
   - Local ChromaDB
   - Extendable to remote DBs

---

**Last Updated**: 2024  
**Architecture Version**: 1.0
