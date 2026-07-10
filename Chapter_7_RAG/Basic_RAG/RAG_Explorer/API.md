# RAG Explorer - API Documentation

## 📡 Base URL
```
http://localhost:5000
```

## 🔐 Authentication
Currently, no authentication is required. In production, add Bearer token authentication.

---

## Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | System health check |
| GET | /available-pdfs | List available PDF files |
| POST | /init | Initialize RAG system with PDF |
| POST | /query | Submit query and get answer |
| GET | /collection-stats | Get ChromaDB statistics |

---

## 📋 Detailed Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

**Description**: Check if the backend server is running.

**Response**:
```json
{
  "status": "ok",
  "message": "RAG Explorer backend is running"
}
```

**Status Code**: 200

**Example**:
```bash
curl http://localhost:5000/health
```

---

### 2. List Available PDFs

**Endpoint**: `GET /available-pdfs`

**Description**: Get list of PDF files available in the data folder.

**Response**:
```json
{
  "status": "success",
  "pdfs": [
    {
      "name": "Product Requirements Document (PRD) VWO.com.pdf",
      "path": "../Chapter_7_RAG/Basic_RAG/data/Product Requirements Document (PRD) VWO.com.pdf",
      "size": 1048576
    }
  ]
}
```

**Status Code**: 
- 200: Success
- 400: Data folder not found
- 500: Server error

**Example**:
```bash
curl http://localhost:5000/available-pdfs
```

---

### 3. Initialize RAG System

**Endpoint**: `POST /init`

**Description**: Load a PDF file, process it into chunks, generate embeddings, and store in ChromaDB.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "pdf_path": "c:/AI/3x/AI_TEST_3X/Chapter_7_RAG/Basic_RAG/data/Product Requirements Document (PRD) VWO.com.pdf"
}
```

**Success Response** (200):
```json
{
  "status": "success",
  "message": "PDF ingested successfully",
  "pdf_info": {
    "file_name": "Product Requirements Document (PRD) VWO.com.pdf",
    "total_characters": 125000,
    "total_chunks": 250
  },
  "embedding_info": {
    "status": "success",
    "chunks_added": 250,
    "collection_name": "pdf_chunks"
  },
  "collection_stats": {
    "collection_name": "pdf_chunks",
    "total_documents": 250
  }
}
```

**Error Response** (400/500):
```json
{
  "status": "error",
  "message": "PDF file not found: /path/to/file.pdf"
}
```

**Status Codes**:
- 200: Successfully initialized
- 400: Invalid PDF path
- 500: Processing error

**Processing Steps**:
1. Extract text from PDF (PyPDF2)
2. Split into chunks (500 chars, 100 char overlap)
3. Generate embeddings (Nomic Embed - 768 dimensions)
4. Store in ChromaDB with cosine similarity indexing

**Timing**: 5-30 seconds depending on PDF size

**Example**:
```bash
curl -X POST http://localhost:5000/init \
  -H "Content-Type: application/json" \
  -d "{\"pdf_path\": \"c:/AI/3x/AI_TEST_3X/Chapter_7_RAG/Basic_RAG/data/Product Requirements Document (PRD) VWO.com.pdf\"}"
```

---

### 4. Query the System

**Endpoint**: `POST /query`

**Description**: Submit a query to the RAG system. Returns retrieved chunks and LLM-generated answer.

**Prerequisites**: `/init` must be called first

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "query": "What are the main features of VWO?"
}
```

**Success Response** (200):
```json
{
  "status": "success",
  "query": "What are the main features of VWO?",
  "retrieved_chunks": [
    {
      "id": "chunk_23",
      "text": "VWO provides advanced visual editing capabilities...",
      "distance": 0.125,
      "similarity": 0.875
    },
    {
      "id": "chunk_45",
      "text": "Key features include A/B testing, multivariate testing...",
      "distance": 0.150,
      "similarity": 0.850
    },
    {
      "id": "chunk_67",
      "text": "The platform offers comprehensive analytics and reporting...",
      "distance": 0.175,
      "similarity": 0.825
    },
    {
      "id": "chunk_89",
      "text": "Integration with popular tools and platforms...",
      "distance": 0.200,
      "similarity": 0.800
    }
  ],
  "answer": {
    "status": "success",
    "query": "What are the main features of VWO?",
    "answer": "Based on the PRD, VWO's main features include advanced visual editing, A/B testing, multivariate testing, comprehensive analytics, and integrations with popular platforms...",
    "model": "mixtral-8x7b-32768",
    "context_chunks": 4,
    "token_usage": {
      "input_tokens": 1850,
      "output_tokens": 420
    }
  }
}
```

**Error Responses**:
```json
{
  "status": "error",
  "message": "System not initialized. Call /init first."
}
```

```json
{
  "status": "error",
  "message": "Query cannot be empty"
}
```

**Status Codes**:
- 200: Query successful
- 400: Not initialized or empty query
- 500: Server error

**Query Processing Steps**:
1. Embed user query using Nomic Embed
2. Search ChromaDB for top 4 similar chunks (cosine similarity)
3. Format context from retrieved chunks
4. Call Groq API with system prompt + context + query
5. Return answer with metadata

**Timing**: 2-5 seconds typically

**Example**:
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is VWO?\"}"
```

**Query Tips**:
- Be specific for better results
- Ask one question at a time
- Use natural language
- Examples: "List the features", "Who is the target user?", "What platforms are supported?"

---

### 5. Collection Statistics

**Endpoint**: `GET /collection-stats`

**Description**: Get statistics about the ChromaDB collection and current PDF.

**Response**:
```json
{
  "status": "success",
  "stats": {
    "collection_name": "pdf_chunks",
    "total_documents": 250
  },
  "pdf_info": {
    "file_name": "Product Requirements Document (PRD) VWO.com.pdf",
    "total_characters": 125000,
    "total_chunks": 250
  }
}
```

**Status Code**: 200

**Example**:
```bash
curl http://localhost:5000/collection-stats
```

---

## 🔄 Complete Workflow Example

### Step 1: Check Health
```bash
curl http://localhost:5000/health
```

### Step 2: List Available PDFs
```bash
curl http://localhost:5000/available-pdfs
```

### Step 3: Initialize with PDF
```bash
curl -X POST http://localhost:5000/init \
  -H "Content-Type: application/json" \
  -d "{\"pdf_path\": \"path/to/pdf.pdf\"}"
```

### Step 4: Submit Query
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"Your question here\"}"
```

### Step 5: Check Collection Stats
```bash
curl http://localhost:5000/collection-stats
```

---

## 📊 Response Field Explanations

### Chunks Structure
```json
{
  "id": "chunk_23",           // Unique chunk identifier
  "text": "The text content...", // Actual text from PDF
  "distance": 0.125,          // Lower = more similar (0-1, cosine distance)
  "similarity": 0.875         // Higher = more similar (1 - distance)
}
```

### Token Usage
```json
{
  "input_tokens": 1850,    // Tokens sent to LLM
  "output_tokens": 420     // Tokens returned by LLM
}
```

---

## ⚠️ Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "PDF file not found" | Invalid path | Verify PDF exists at specified path |
| "System not initialized" | /init not called | Call /init endpoint first |
| "GROQ_API_KEY not set" | Missing env variable | Add GROQ_API_KEY to .env file |
| "Connection refused" | Backend not running | Start backend with `python app.py` |
| "Out of memory" | Large PDF | Reduce chunk size or increase RAM |

---

## 🚀 Performance Metrics

### Typical Times
- Health check: < 10ms
- List PDFs: < 50ms
- Initialize (100 chunks): 15-30 seconds
- Query processing: 2-5 seconds
- Collection stats: < 50ms

### Factors Affecting Speed
- **PDF Size**: Larger PDFs take longer to process
- **Chunk Count**: More chunks = longer embedding time
- **Network**: Groq API latency affects query time
- **System Resources**: CPU/RAM available for processing

---

## 🔐 Security Considerations

### Current Implementation
- No authentication (localhost only)
- No rate limiting
- No input sanitization for queries

### Production Recommendations
- Add API authentication (Bearer tokens)
- Implement rate limiting
- Validate file paths (prevent directory traversal)
- Sanitize LLM inputs
- Use HTTPS for API calls
- Add request logging and monitoring

---

## 📝 API Client Examples

### JavaScript/Fetch
```javascript
async function queryRAG(query) {
  const response = await fetch('http://localhost:5000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  return response.json();
}
```

### Python/Requests
```python
import requests

def query_rag(query):
    response = requests.post(
        'http://localhost:5000/query',
        json={'query': query}
    )
    return response.json()
```

### cURL
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"your question"}'
```

---

## 🔄 CORS Headers

The backend includes CORS headers for cross-origin requests:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## 📚 Related Documentation

- [README.md](./README.md) - Setup and usage guide
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [DEVELOPER.md](./DEVELOPER.md) - Development guide

---

**Last Updated**: 2024  
**API Version**: 1.0  
**Status**: Production Ready
