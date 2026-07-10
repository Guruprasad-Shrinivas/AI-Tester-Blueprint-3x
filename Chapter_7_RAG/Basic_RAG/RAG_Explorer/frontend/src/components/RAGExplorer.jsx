import React, { useEffect } from 'react';
import { ragAPI } from '../api';
import { useRAGStore } from '../store';
import '../styles/RAGExplorer.css';
import { PDFUploader } from './PDFUploader';
import { ProcessingFlow } from './ProcessingFlow';
import { QueryInterface } from './QueryInterface';

function RAGExplorer() {
  const { isInitialized, setCollectionStats } = useRAGStore();

  useEffect(() => {
    // Fetch collection stats periodically when initialized
    if (isInitialized) {
      const interval = setInterval(async () => {
        try {
          const response = await ragAPI.getCollectionStats();
          if (response.data.status === 'success') {
            setCollectionStats(response.data.stats);
          }
        } catch (err) {
          console.error('Failed to fetch collection stats:', err);
        }
      }, 5000); // Update every 5 seconds

      return () => clearInterval(interval);
    }
  }, [isInitialized, setCollectionStats]);

  return (
    <div className="rag-explorer">
      <header className="header">
        <div className="header-content">
          <h1>🤖 RAG Explorer</h1>
          <p>Retrieval-Augmented Generation Pipeline Demonstration</p>
        </div>
        <div className="header-badge">
          {isInitialized ? (
            <span className="badge-ready">✓ System Ready</span>
          ) : (
            <span className="badge-waiting">⏳ Awaiting PDF</span>
          )}
        </div>
      </header>

      <main className="main-content">
        <section className="section">
          <PDFUploader />
        </section>

        {isInitialized && (
          <>
            <section className="section">
              <ProcessingFlow />
            </section>

            <section className="section">
              <QueryInterface />
            </section>
          </>
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>
            <strong>RAG Pipeline:</strong> PDF → Chunks → Embeddings (Nomic) →
            ChromaDB → Retrieval → Groq LLM → Answer
          </p>
          <p className="tech-stack">
            <strong>Tech Stack:</strong> Python (Flask) | React | ChromaDB |
            Nomic Embed | Groq API
          </p>
        </div>
      </footer>
    </div>
  );
}

export default RAGExplorer;
