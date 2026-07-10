"""
Embeddings and ChromaDB Storage Module
Generates embeddings using Nomic Embed and stores in ChromaDB
"""
import os
import chromadb
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingStore:
    """Handle embeddings generation and ChromaDB storage"""

    def __init__(self, db_path: str = "./chroma_db"):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)

        # chromadb >= 0.4 uses PersistentClient
        self.client = chromadb.PersistentClient(path=db_path)

        # Nomic Embed via HuggingFace (downloaded locally)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="nomic-ai/nomic-embed-text-v1.5",
            model_kwargs={"trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.collection = None

    def create_collection(self, collection_name: str = "pdf_chunks") -> None:
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: List[Dict]) -> Dict:
        if not self.collection:
            raise Exception("Collection not created. Call create_collection first.")

        ids = []
        texts = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["id"])
            texts.append(chunk["text"])
            metadatas.append({"chunk_index": str(chunk["chunk_index"])})

        embeddings_list = self.embeddings.embed_documents(texts)

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings_list,
            metadatas=metadatas,
        )

        return {
            "status": "success",
            "chunks_added": len(chunks),
            "collection_name": self.collection.name,
        }

    def retrieve_chunks(self, query: str, top_k: int = 4) -> List[Dict]:
        if not self.collection:
            raise Exception("Collection not created. Call create_collection first.")

        # Embed query with the same Nomic model used for documents
        query_embedding = self.embeddings.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        retrieved_chunks = []
        for i in range(len(results["ids"][0])):
            retrieved_chunks.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "distance": results["distances"][0][i],
                "similarity": 1 - results["distances"][0][i],
            })

        return retrieved_chunks

    def get_collection_stats(self) -> Dict:
        if not self.collection:
            return {"status": "error", "message": "No collection created"}

        return {
            "collection_name": self.collection.name,
            "total_documents": self.collection.count(),
        }
