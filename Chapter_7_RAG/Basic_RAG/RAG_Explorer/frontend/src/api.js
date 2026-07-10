import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ragAPI = {
  // Health check
  health: () => api.get('/health'),

  // Get available PDFs
  getAvailablePDFs: () => api.get('/available-pdfs'),

  // Initialize with PDF
  initialize: (pdfPath) => api.post('/init', { pdf_path: pdfPath }),

  // Query the system
  query: (queryText) => api.post('/query', { query: queryText }),

  // Get collection stats
  getCollectionStats: () => api.get('/collection-stats'),
};

export default api;
