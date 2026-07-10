# RAG Explorer - Developer Guide

## 👨‍💻 Development Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Groq API Key
- Basic understanding of React, Flask, and RAG concepts

### Quick Development Setup

```bash
# Clone/navigate to project
cd c:\AI\3x\AI_TEST_3X\RAG_Explorer

# Run setup script
# On Windows:
.\setup.ps1

# On Mac/Linux:
chmod +x setup.sh
./setup.sh
```

---

## 🗂️ Project Structure Deep Dive

```
RAG_Explorer/
│
├── backend/                      # Flask backend
│   ├── app.py                   # Main application & API routes
│   ├── pdf_processor.py         # PDF handling & chunking
│   ├── embeddings.py            # ChromaDB & embeddings
│   ├── llm_chain.py             # Groq LLM integration
│   │
│   ├── venv/                    # Python virtual environment
│   ├── chroma_db/               # ChromaDB persistent storage
│   │   ├── api_data/
│   │   └── {uuid}.pickle        # Collection data
│   │
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (gitignored)
│   └── .env.example              # Template for .env
│
├── frontend/                     # React frontend
│   ├── public/
│   │   └── index.html            # HTML entry point
│   │
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── RAGExplorer.jsx   # Main app container
│   │   │   ├── PDFUploader.jsx   # PDF loading (Step 1)
│   │   │   ├── ProcessingFlow.jsx # Pipeline visualization
│   │   │   └── QueryInterface.jsx # Query & results (Step 2)
│   │   │
│   │   ├── styles/               # CSS files
│   │   │   ├── index.css
│   │   │   ├── RAGExplorer.css
│   │   │   ├── PDFUploader.css
│   │   │   ├── ProcessingFlow.css
│   │   │   └── QueryInterface.css
│   │   │
│   │   ├── api.js                # API client (axios)
│   │   ├── store.js              # State management (zustand)
│   │   └── index.js              # React entry point
│   │
│   ├── node_modules/             # Node dependencies
│   ├── package.json              # Node configuration
│   └── package-lock.json         # Dependency lock file
│
├── docs/                         # Documentation
│   ├── README.md                 # Main documentation
│   ├── QUICKSTART.md             # Quick start
│   ├── ARCHITECTURE.md           # System design
│   ├── API.md                    # API documentation
│   └── DEVELOPER.md              # This file
│
├── .gitignore                    # Git ignore rules
├── setup.ps1                     # Windows setup script
├── setup.sh                      # Unix setup script
└── {root}
```

---

## 🔧 Modifying Core Components

### 1. Changing PDF Processing Logic

**File**: `backend/pdf_processor.py`

```python
# Modify chunking parameters
pdf_processor = PDFProcessor(
    chunk_size=500,      # Increase for larger chunks
    chunk_overlap=100    # Increase for more context
)

# Example: Change to 1000-char chunks with 200-char overlap
pdf_processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
```

**Custom Chunking Strategy**:
```python
def split_into_chunks(self, text: str) -> List[Dict]:
    # Override with custom logic
    # Could use sentence boundaries, paragraph boundaries, etc.
    pass
```

---

### 2. Switching Embedding Models

**File**: `backend/embeddings.py`

```python
# Current model
self.embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    ...
)

# Alternative models:
# Option 1: Sentence Transformers
model_name="sentence-transformers/all-MiniLM-L6-v2"  # Smaller, faster

# Option 2: OpenAI (requires API key)
from langchain.embeddings.openai import OpenAIEmbeddings
self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Option 3: Local model
model_name="sentence-transformers/all-mpnet-base-v2"  # Larger, slower
```

---

### 3. Changing the LLM Model

**File**: `backend/llm_chain.py`

```python
# Current model
self.model = "mixtral-8x7b-32768"

# Available Groq models:
# - "llama2-70b-4096" (Llama 2)
# - "mixtral-8x7b-32768" (Mixtral - default)
# - "gemma-7b-it" (Gemma)

# Example: Switch to Llama 2
self.model = "llama2-70b-4096"
```

---

### 4. Adjusting Retrieval Parameters

**File**: `backend/app.py`

```python
# Current: retrieve top 4 chunks
retrieved_chunks = embedding_store.retrieve_chunks(user_query, top_k=4)

# Change to top 6 chunks
retrieved_chunks = embedding_store.retrieve_chunks(user_query, top_k=6)

# Adjust max tokens in answer
# In llm_chain.py:
message = self.client.messages.create(
    model=self.model,
    messages=[...],
    max_tokens=1024,  # Increase for longer answers
    temperature=0.7   # Adjust creativity (0-1)
)
```

---

## 🎨 Modifying Frontend Components

### 1. Adding New Visualization

**Example**: Add a chunk count progress indicator

```jsx
// In ProcessingFlow.jsx
<div className="progress-bar">
  <div 
    className="progress-fill" 
    style={{width: `${(pdfInfo.total_chunks / 1000) * 100}%`}}
  >
    {pdfInfo.total_chunks} chunks
  </div>
</div>
```

### 2. Customizing UI Colors

**File**: `frontend/src/styles/RAGExplorer.css`

```css
/* Change primary color from purple to blue */
.header {
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
}

.badge-ready {
  background: #10b981;  /* Green instead of predefined */
}
```

### 3. Adding Loading Animation

**File**: `frontend/src/components/QueryInterface.jsx`

```jsx
{isQuerying && (
  <div className="loading-spinner">
    <div className="spinner"></div>
    <p>Processing your query...</p>
  </div>
)}
```

---

## 🐛 Debugging

### Backend Debugging

**Enable Verbose Logging**:
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug prints
@app.route('/query', methods=['POST'])
def query():
    logger.debug(f"Query received: {request.json}")
    # ... rest of code
```

**Run with Debugger**:
```bash
# Using pdb
python -m pdb app.py

# Or use VSCode debugger:
# Add to .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {"FLASK_APP": "app.py", "FLASK_ENV": "development"},
      "args": ["run"],
      "jinja": true
    }
  ]
}
```

### Frontend Debugging

**Browser DevTools**:
```javascript
// In components
console.log("State:", useRAGStore.getState());
console.log("Query result:", response.data);
```

**React DevTools**:
- Install React DevTools browser extension
- Inspect component state and props
- Track component re-renders

---

## ✅ Testing

### Backend Unit Tests

**Create**: `backend/test_pdf_processor.py`

```python
import unittest
from pdf_processor import PDFProcessor

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()
    
    def test_chunk_size(self):
        chunks = self.processor.split_into_chunks("a" * 1000)
        assert all(len(c["text"]) <= 600 for c in chunks)
    
    def test_chunk_count(self):
        text = "sentence. " * 100
        chunks = self.processor.split_into_chunks(text)
        assert len(chunks) > 0

if __name__ == '__main__':
    unittest.main()
```

**Run Tests**:
```bash
python -m pytest backend/test_pdf_processor.py -v
```

### Frontend Component Tests

**Create**: `frontend/src/components/__tests__/PDFUploader.test.jsx`

```jsx
import { render, screen } from '@testing-library/react';
import { PDFUploader } from '../PDFUploader';

test('renders PDF uploader', () => {
  render(<PDFUploader />);
  expect(screen.getByText(/Step 1/i)).toBeInTheDocument();
});
```

---

## 🚀 Adding New Features

### Feature: Export Results to PDF

**Steps**:
1. Install library: `pip install reportlab`
2. Add endpoint:
```python
@app.route('/export-results', methods=['POST'])
def export_results():
    data = request.json
    # Generate PDF
    return send_file(pdf_buffer, ...)
```
3. Add button in React UI

### Feature: Chat History

**Steps**:
1. Add Zustand store for history
2. Save queries/answers to localStorage
3. Add history sidebar in UI
4. Implement query replay

### Feature: Multiple PDF Collections

**Steps**:
1. Modify ChromaDB to support multiple collections
2. Add collection selection in UI
3. Update backend routing

---

## 📦 Adding Dependencies

### Python Package
```bash
# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt

# Or manually add and version
echo "package_name==version" >> requirements.txt
```

### Node Package
```bash
# Install new package
npm install package_name

# Or for dev dependency
npm install --save-dev package_name

# Update package.json (automatic)
```

---

## 🔄 Common Development Tasks

### 1. Clear All Data
```bash
# Delete ChromaDB
rm -r backend/chroma_db

# Clear browser cache
# DevTools → Application → Clear Storage
```

### 2. Reset Frontend State
```javascript
// In browser console
useRAGStore.getState().resetState();
```

### 3. Test API Manually
```bash
# Test initialization
curl -X POST http://localhost:5000/init \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "path/to/pdf.pdf"}'

# Test query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

---

## 🎯 Performance Optimization

### Backend

1. **Batch Embedding Generation**:
```python
# Instead of embedding one at a time
embeddings_list = self.embeddings.embed_documents(texts)  # Batch
```

2. **Cache Embeddings**:
```python
@functools.lru_cache(maxsize=1000)
def get_embedding(text):
    return self.embeddings.embed_query(text)
```

3. **Optimize Chunk Retrieval**:
```python
# Use metadata filtering
results = collection.query(
    query_texts=[query],
    n_results=4,
    where={"chunk_index": {"$gte": 0}}  # Optional filtering
)
```

### Frontend

1. **Code Splitting**:
```javascript
// Use React.lazy for component splitting
const PDFUploader = React.lazy(() => import('./PDFUploader'));
```

2. **Memoization**:
```jsx
const ProcessingFlow = React.memo(({ pdfInfo }) => {
  // Component won't re-render unless pdfInfo changes
});
```

---

## 📚 Code Style Guide

### Python
```python
# Follow PEP 8
# Use type hints
def process_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Process PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with processed data
    """
    pass

# Docstrings for all functions
# Max line length: 100 chars
# Use meaningful variable names
```

### JavaScript/React
```jsx
// Use const/let (not var)
// Use arrow functions
const handleQuery = async () => {
  // Code
};

// Meaningful component names (PascalCase)
export function QueryInterface() {
  return <div>Content</div>;
}

// Props validation
function Component({ prop1, prop2 }) {
  // Code
}
```

---

## 🔗 Useful Resources

### Documentation
- Flask: https://flask.palletsprojects.com
- React: https://react.dev
- ChromaDB: https://docs.trychroma.com
- Groq API: https://console.groq.com/docs
- LangChain: https://python.langchain.com

### Learning
- RAG Concepts: https://www.promptingguide.ai/applications/rag
- Vector Databases: https://www.pinecone.io/learn/vector-database/
- LLM Fine-tuning: https://huggingface.co/docs

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Test thoroughly
4. Create pull request with description

---

## 📊 Architecture Decisions

### Why Zustand for state management?
- Lightweight
- Simple API
- No boilerplate
- Easy debugging

### Why ChromaDB for vectors?
- Open source
- Local storage
- Easy to set up
- Good performance for demo

### Why Groq for LLM?
- Fast inference
- Free tier available
- Multiple model options
- Good API

---

## 🚀 Deployment Checklist

- [ ] Update all dependencies to stable versions
- [ ] Remove debug logging
- [ ] Add error handling
- [ ] Add input validation
- [ ] Test with production data
- [ ] Set up monitoring
- [ ] Configure HTTPS
- [ ] Add authentication
- [ ] Document API
- [ ] Prepare rollback plan

---

**Last Updated**: 2024  
**Version**: 1.0  
**Maintainer**: Development Team
