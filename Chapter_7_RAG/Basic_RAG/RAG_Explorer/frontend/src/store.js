import create from 'zustand';

export const useRAGStore = create((set) => ({
  // PDF and initialization state
  currentPDF: null,
  pdfInfo: null,
  isInitialized: false,
  isInitializing: false,

  // Query and results state
  query: '',
  retrievedChunks: [],
  answer: null,
  isQuerying: false,
  queryError: null,

  // Collection state
  collectionStats: null,

  // Actions
  setCurrentPDF: (pdf) => set({ currentPDF: pdf }),
  setPDFInfo: (info) => set({ pdfInfo: info }),
  setIsInitialized: (value) => set({ isInitialized: value }),
  setIsInitializing: (value) => set({ isInitializing: value }),

  setQuery: (text) => set({ query: text }),
  setRetrievedChunks: (chunks) => set({ retrievedChunks: chunks }),
  setAnswer: (answer) => set({ answer }),
  setIsQuerying: (value) => set({ isQuerying: value }),
  setQueryError: (error) => set({ queryError: error }),

  setCollectionStats: (stats) => set({ collectionStats: stats }),

  resetState: () => set({
    currentPDF: null,
    pdfInfo: null,
    isInitialized: false,
    isInitializing: false,
    query: '',
    retrievedChunks: [],
    answer: null,
    isQuerying: false,
    queryError: null,
    collectionStats: null,
  }),
}));
