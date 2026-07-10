import React from 'react';
import { ragAPI } from '../api';
import { useRAGStore } from '../store';
import '../styles/QueryInterface.css';

export function QueryInterface() {
  const {
    query,
    setQuery,
    isQuerying,
    setIsQuerying,
    retrievedChunks,
    setRetrievedChunks,
    answer,
    setAnswer,
    queryError,
    setQueryError,
    isInitialized,
  } = useRAGStore();

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSubmitQuery = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setQueryError('Please enter a query');
      return;
    }

    if (!isInitialized) {
      setQueryError('System not initialized. Please load a PDF first.');
      return;
    }

    try {
      setIsQuerying(true);
      setQueryError(null);
      setAnswer(null);
      setRetrievedChunks([]);

      const response = await ragAPI.query(query);

      if (response.data.status === 'success') {
        setRetrievedChunks(response.data.retrieved_chunks || []);
        setAnswer(response.data.answer);
        setQueryError(null);
      } else {
        setQueryError(response.data.message);
      }
    } catch (err) {
      setQueryError('Failed to process query: ' + err.message);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <div className="query-interface">
      <h2>🔍 Step 2: Query the System</h2>

      <form onSubmit={handleSubmitQuery} className="query-form">
        <textarea
          className="query-input"
          placeholder="Ask a question about the PDF document..."
          value={query}
          onChange={handleQueryChange}
          disabled={isQuerying || !isInitialized}
          rows={4}
        />
        <button
          type="submit"
          className="query-button"
          disabled={isQuerying || !isInitialized}
        >
          {isQuerying ? '⏳ Processing...' : '🚀 Submit Query'}
        </button>
      </form>

      {queryError && <div className="query-error">{queryError}</div>}

      {/* Retrieved Chunks Section */}
      {retrievedChunks.length > 0 && (
        <div className="retrieved-chunks">
          <h3>📚 Retrieved Chunks (Top 4)</h3>
          <div className="chunks-container">
            {retrievedChunks.map((chunk, index) => (
              <div key={chunk.id} className="chunk-card">
                <div className="chunk-header">
                  <span className="chunk-number">Chunk {index + 1}</span>
                  <span className="chunk-similarity">
                    Similarity: {(chunk.similarity * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="chunk-text">{chunk.text}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Answer Section */}
      {answer && (
        <div className="answer-section">
          <h3>💡 Generated Answer</h3>
          <div className="answer-box">
            <div className="answer-text">{answer.answer}</div>
            {answer.token_usage && (
              <div className="answer-stats">
                <span>Model: {answer.model}</span>
                <span>
                  Tokens: {answer.token_usage.input_tokens} →{' '}
                  {answer.token_usage.output_tokens}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
