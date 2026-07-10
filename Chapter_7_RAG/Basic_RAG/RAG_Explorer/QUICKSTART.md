# RAG Explorer - Quick Start Guide

## ⚡ 5-Minute Setup

### Prerequisites
- Python 3.9+, Node.js 16+
- Groq API key (free from groq.com)

---

## 🚀 Start the Application

### Terminal 1: Backend
```bash
cd c:\AI\3x\AI_TEST_3X\RAG_Explorer\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with your Groq API key
echo GROQ_API_KEY=your_key_here > .env
echo FLASK_ENV=development >> .env

python app.py
```

**Expected Output:**
```
Server running on http://localhost:5000
```

### Terminal 2: Frontend
```bash
cd c:\AI\3x\AI_TEST_3X\RAG_Explorer\frontend
npm install
npm start
```

**Browser opens to:** `http://localhost:3000`

---

## 📱 Using the App

1. **Select PDF** → Click the VWO PRD document
2. **Initialize** → Click "Initialize RAG System" (wait for processing)
3. **Ask Questions** → Type your query in the query box
4. **View Results** → See retrieved chunks and LLM-generated answer

---

## 🔑 Getting Your Groq API Key

1. Visit: https://console.groq.com
2. Sign up/login
3. Create an API key
4. Copy to backend/.env file

---

## 📊 What Happens Behind the Scenes

```
PDF Upload → Text Extraction → Chunking (500 chars)
                                    ↓
                            Nomic Embeddings (768D vectors)
                                    ↓
                            ChromaDB Storage (Local)
                                    ↓
User Query → Embedding → Similarity Search → Top 4 Chunks
                                    ↓
                        Groq LLM (Mixtral 8x7B)
                                    ↓
                            LLM-Generated Answer
```

---

## 💾 File Locations

- **PDF to Process**: `c:\AI\3x\AI_TEST_3X\Chapter_7_RAG\Basic_RAG\data\`
- **Vector Database**: `c:\AI\3x\AI_TEST_3X\RAG_Explorer\backend\chroma_db\`
- **Backend Logs**: Terminal running `python app.py`
- **Frontend Logs**: Browser console (F12 → Console)

---

## ❓ Common Issues

| Issue | Solution |
|-------|----------|
| "GROQ_API_KEY not set" | Add key to backend/.env and restart |
| "Cannot find PDF" | Ensure PDF is in data folder path |
| "Connection refused" | Make sure backend runs on port 5000 |
| "Slow processing" | Normal for large PDFs; Nomic Embed is thorough |

---

## 📚 Example Queries

```
"What is VWO?"
"List the main features"
"Who is the target user?"
"What integrations are supported?"
"What are the key metrics?"
```

---

**Happy RAG exploring! 🎉**
