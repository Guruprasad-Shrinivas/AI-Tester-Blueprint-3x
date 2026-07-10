"""
RAG Explorer Flask Application
Main backend server for RAG pipeline
"""
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pdf_processor import PDFProcessor
from embeddings import EmbeddingStore
from llm_chain import GroqLLMChain

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize components
pdf_processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
embedding_store = EmbeddingStore(db_path="./chroma_db")
llm_chain = None

# Global state
current_pdf_info = None
chunks_data = None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "RAG Explorer backend is running"})


@app.route('/init', methods=['POST'])
def initialize():
    """
    Initialize the RAG system with a PDF file
    Endpoint: POST /init
    """
    global current_pdf_info, chunks_data, llm_chain
    
    try:
        # Get PDF path from request
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({
                "status": "error",
                "message": f"PDF file not found: {pdf_path}"
            }), 400
        
        # Initialize LLM chain
        if llm_chain is None:
            llm_chain = GroqLLMChain()
        
        # Step 1: Process PDF
        pdf_result = pdf_processor.process_pdf(pdf_path)
        chunks_data = pdf_result['chunks']
        
        # Step 2: Create ChromaDB collection
        embedding_store.create_collection("pdf_chunks")
        
        # Step 3: Add chunks to ChromaDB with embeddings
        embedding_result = embedding_store.add_chunks(chunks_data)
        
        # Store current PDF info
        current_pdf_info = {
            "file_name": pdf_result['file_name'],
            "total_characters": pdf_result['total_characters'],
            "total_chunks": pdf_result['total_chunks']
        }
        
        return jsonify({
            "status": "success",
            "message": "PDF ingested successfully",
            "pdf_info": current_pdf_info,
            "embedding_info": embedding_result,
            "collection_stats": embedding_store.get_collection_stats()
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/query', methods=['POST'])
def query():
    """
    Query the RAG system
    Endpoint: POST /query
    Body: {"query": "your question"}
    """
    try:
        global llm_chain
        
        if not embedding_store.collection:
            return jsonify({
                "status": "error",
                "message": "System not initialized. Call /init first."
            }), 400
        
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                "status": "error",
                "message": "Query cannot be empty"
            }), 400
        
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = embedding_store.retrieve_chunks(user_query, top_k=4)
        
        # Step 2: Generate answer using Groq LLM
        if llm_chain is None:
            llm_chain = GroqLLMChain()
        
        answer_result = llm_chain.generate_answer(user_query, retrieved_chunks)
        
        return jsonify({
            "status": "success",
            "query": user_query,
            "retrieved_chunks": retrieved_chunks,
            "answer": answer_result
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/collection-stats', methods=['GET'])
def collection_stats():
    """Get collection statistics"""
    try:
        stats = embedding_store.get_collection_stats()
        return jsonify({
            "status": "success",
            "stats": stats,
            "pdf_info": current_pdf_info
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/available-pdfs', methods=['GET'])
def available_pdfs():
    """List available PDFs in data folder"""
    try:
        data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
        
        if not os.path.exists(data_folder):
            return jsonify({
                "status": "error",
                "message": "Data folder not found"
            }), 400
        
        pdfs = [
            {
                "name": f,
                "path": os.path.join(data_folder, f),
                "size": os.path.getsize(os.path.join(data_folder, f))
            }
            for f in os.listdir(data_folder)
            if f.lower().endswith('.pdf')
        ]
        
        return jsonify({
            "status": "success",
            "pdfs": pdfs
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    print("Starting RAG Explorer Backend...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /available-pdfs - List available PDFs")
    print("  POST /init - Initialize with PDF")
    print("  POST /query - Query the system")
    print("  GET  /collection-stats - Get collection statistics")
    print("\nServer running on http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
