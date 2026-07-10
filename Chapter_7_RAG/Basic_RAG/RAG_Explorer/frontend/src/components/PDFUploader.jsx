import React, { useEffect, useState } from 'react';
import { ragAPI } from '../api';
import { useRAGStore } from '../store';
import '../styles/PDFUploader.css';

export function PDFUploader() {
  const [pdfs, setPDFs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { 
    currentPDF, 
    setCurrentPDF, 
    isInitializing, 
    setIsInitializing,
    setIsInitialized,
    setPDFInfo,
  } = useRAGStore();

  useEffect(() => {
    fetchAvailablePDFs();
  }, []);

  const fetchAvailablePDFs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await ragAPI.getAvailablePDFs();
      setPDFs(response.data.pdfs || []);
    } catch (err) {
      setError('Failed to fetch PDFs: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPDF = (pdf) => {
    setCurrentPDF(pdf);
  };

  const handleInitialize = async () => {
    if (!currentPDF) {
      setError('Please select a PDF first');
      return;
    }

    try {
      setIsInitializing(true);
      setError(null);
      const response = await ragAPI.initialize(currentPDF.path);
      
      if (response.data.status === 'success') {
        setIsInitialized(true);
        setPDFInfo(response.data.pdf_info);
        setError(null);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError('Failed to initialize: ' + err.message);
    } finally {
      setIsInitializing(false);
    }
  };

  return (
    <div className="pdf-uploader">
      <h2>📄 Step 1: Load PDF Document</h2>
      
      {error && <div className="error-message">{error}</div>}

      <div className="pdf-list">
        {loading ? (
          <p>Loading PDFs...</p>
        ) : pdfs.length === 0 ? (
          <p>No PDFs found in the data folder</p>
        ) : (
          pdfs.map((pdf) => (
            <div
              key={pdf.path}
              className={`pdf-item ${currentPDF?.path === pdf.path ? 'selected' : ''}`}
              onClick={() => handleSelectPDF(pdf)}
            >
              <div className="pdf-info">
                <span className="pdf-name">{pdf.name}</span>
                <span className="pdf-size">
                  {(pdf.size / 1024).toFixed(2)} KB
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {currentPDF && (
        <div className="selected-pdf">
          <h3>Selected: {currentPDF.name}</h3>
          <button
            className="init-button"
            onClick={handleInitialize}
            disabled={isInitializing}
          >
            {isInitializing ? 'Processing...' : 'Initialize RAG System'}
          </button>
        </div>
      )}
    </div>
  );
}
