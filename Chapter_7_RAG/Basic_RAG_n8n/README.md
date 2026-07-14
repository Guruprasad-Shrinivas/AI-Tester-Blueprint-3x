# Chapter 7 - Basic RAG (n8n)

An end-to-end **Retrieval-Augmented Generation (RAG)** workflow built in n8n. It ingests documents into a Pinecone vector database using OpenAI embeddings, then lets you query that knowledge base through a chat interface backed by an AI agent.

## Overview

The workflow has two independent phases:

### Phase 1 - Ingestion
1. **On form submission** - a Form Trigger accepts uploaded files (PDF, CSV, JSON, TXT, HTML).
2. **Default Data Loader** + **Recursive Character Text Splitter** - the binary file is loaded and split into overlapping chunks (chunk overlap: 200), with `fileName` and `uploadedAt` metadata attached.
3. **Embeddings OpenAI Small** - each chunk is embedded with OpenAI (1536 dimensions).
4. **Store the Documents to Vector DB** - embeddings are upserted into the Pinecone index `ai3x-1536`.

### Phase 2 - RAG Fetching
1. **When chat message received** - a Chat Trigger receives a user question.
2. **RAG Agent** - an AI agent answers using ONLY the retrieved documents, and cites the source `fileName`. If nothing relevant is found it replies that it could not find the answer in the uploaded documents.
3. **Pinecone Vector Store** (retrieve-as-tool) + **Embeddings OpenAI** - the agent searches the knowledge base for relevant chunks.
4. **Brain - gpt-5-mini** - the language model powering the agent.
5. **Model Chat memory** - a buffer-window memory keeps short conversation context.

## Prerequisites

- An **OpenAI** API credential (for embeddings and the chat model).
- A **Pinecone** API credential with an index named `ai3x-1536` (1536-dimension, matching the embedding model).

## Setup

1. Import `Basic_RAG_n8n.json` into your n8n instance.
2. Connect your OpenAI and Pinecone credentials on the relevant nodes.
3. Ensure the Pinecone index `ai3x-1536` exists.

## Usage

1. **Ingest** - open the Form Trigger URL and upload one or more documents. They are embedded and stored in Pinecone.
2. **Ask** - open the chat and ask questions. The agent retrieves relevant chunks and answers with citations.

## Files

- `Basic_RAG_n8n.json` - the exported n8n workflow.
