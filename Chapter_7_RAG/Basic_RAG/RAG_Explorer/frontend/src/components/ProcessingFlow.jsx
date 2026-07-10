import React, { useEffect } from 'react';
import { useRAGStore } from '../store';
import '../styles/ProcessingFlow.css';

export function ProcessingFlow() {
  const { pdfInfo, collectionStats } = useRAGStore();

  return (
    <div className="processing-flow">
      <h2>📊 Processing Pipeline Status</h2>
      
      <div className="flow-container">
        {/* Step 1: PDF Ingestion */}
        <div className="flow-step completed">
          <div className="step-icon">📥</div>
          <div className="step-content">
            <h3>PDF Ingestion</h3>
            {pdfInfo && (
              <div className="step-details">
                <p><strong>File:</strong> {pdfInfo.file_name}</p>
                <p><strong>Characters:</strong> {pdfInfo.total_characters.toLocaleString()}</p>
              </div>
            )}
          </div>
        </div>

        <div className="flow-arrow">→</div>

        {/* Step 2: Chunking */}
        <div className="flow-step completed">
          <div className="step-icon">✂️</div>
          <div className="step-content">
            <h3>Chunking</h3>
            {pdfInfo && (
              <div className="step-details">
                <p><strong>Total Chunks:</strong> {pdfInfo.total_chunks}</p>
                <p><strong>Chunk Size:</strong> 500 chars</p>
              </div>
            )}
          </div>
        </div>

        <div className="flow-arrow">→</div>

        {/* Step 3: Embedding Generation */}
        <div className="flow-step completed">
          <div className="step-icon">🧠</div>
          <div className="step-content">
            <h3>Embeddings</h3>
            <div className="step-details">
              <p><strong>Model:</strong> Nomic Embed</p>
              <p><strong>Type:</strong> Dense Vectors</p>
            </div>
          </div>
        </div>

        <div className="flow-arrow">→</div>

        {/* Step 4: Storage */}
        <div className="flow-step completed">
          <div className="step-icon">💾</div>
          <div className="step-content">
            <h3>Vector Storage</h3>
            <div className="step-details">
              <p><strong>Database:</strong> ChromaDB</p>
              {collectionStats && (
                <p><strong>Stored:</strong> {collectionStats.total_documents} vectors</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="flow-footer">
        <p>✓ All components ready for querying</p>
      </div>
    </div>
  );
}
