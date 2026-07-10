import React from 'react';
import ReactDOM from 'react-dom/client';
import RAGExplorer from './components/RAGExplorer';
import './styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RAGExplorer />
  </React.StrictMode>
);
