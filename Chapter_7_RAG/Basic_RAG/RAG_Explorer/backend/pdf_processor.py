"""
PDF Processing Module
Handles PDF reading, text extraction, and chunking
"""
import os
import re
from typing import List, Dict
from PyPDF2 import PdfReader


class PDFProcessor:
    """Process PDF files and split into chunks"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize PDF processor
        
        Args:
            chunk_size: Number of characters per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n"
                return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def split_into_chunks(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Full text to split
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "text": current_chunk.strip(),
                        "chunk_index": chunk_id
                    })
                    chunk_id += 1
                    # Add overlap
                    words = current_chunk.split()
                    overlap_count = int(len(words) * (self.chunk_overlap / self.chunk_size))
                    current_chunk = " ".join(words[-overlap_count:]) if overlap_count > 0 else ""
                
                current_chunk += " " + sentence
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": current_chunk.strip(),
                "chunk_index": chunk_id
            })
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with chunks and metadata
        """
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Split into chunks
        chunks = self.split_into_chunks(text)
        
        return {
            "file_name": os.path.basename(pdf_path),
            "total_characters": len(text),
            "total_chunks": len(chunks),
            "chunks": chunks
        }
