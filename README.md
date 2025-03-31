# RAG API with OpenRouter and ChromaDB

A scalable and production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, OpenRouter, and ChromaDB.

## Features

- **Document Management**: Upload, retrieve, update, and delete documents
- **Automatic Text Processing**: Chunk documents and convert to vector embeddings
- **Vector Search**: Semantic search across your document collection
- **RAG Chat**: Generate LLM responses with context from your documents
- **Session Management**: Track conversations and maintain context
- **API-First Design**: Easy integration with any frontend or application

## Architecture

This project follows a modular architecture:

- **FastAPI Backend**: High-performance asynchronous API
- **MongoDB**: Document and metadata storage
- **ChromaDB**: Vector database for embeddings and semantic search
- **OpenRouter**: Access to state-of-the-art embedding and LLM models

## Project Structure

```
fastapi-rag-project/
├── app/
│   ├── core/          # Core components (config, database connections)
│   ├── api/           # API routes and endpoints
│   ├── models/        # Data models
│   ├── schemas/       # Pydantic schemas for validation
│   ├── services/      # Business logic
│   └── utils/         # Utility functions
└── tests/             # Test suite
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB
- ChromaDB (can be run as a service or embedded)
- OpenRouter API Key

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ZulfiFazhar/fastapi-r1-zero-rag.git
   cd fastapi-r1-zero-rag
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the provided `.env.example`:

   ```bash
   cp .env.example .env
   ```

5. Update the `.env` file with your configuration:
   ```
   MONGODB_URL=mongodb://127.0.0.1:27017
   MONGODB_DB_NAME=rag_db
   OPENROUTER_API_KEY=your_openrouter_api_key
   OPENROUTER_API_URL=https://openrouter.ai/api/v1
   DEFAULT_LLM_MODEL=deepseek/deepseek-r1-zero:free
   EMBEDDING_MODEL=openai/text-embedding-3-small
   CHROMADB_HOST=localhost
   CHROMADB_PORT=8000
   CHROMADB_COLLECTION=documents
   ```

### Running ChromaDB

You can run ChromaDB either as an embedded database or as a separate service:

#### Embedded Mode

No additional setup is required. Just leave `CHROMADB_HOST` and `CHROMADB_PORT` empty in your `.env` file.

#### Server Mode

1. Install ChromaDB server:

   ```bash
   pip install chromadb
   ```

2. Run the ChromaDB server:

   ```bash
   chroma run --host localhost --port 8000
   ```

3. Configure the `.env` file to point to your ChromaDB server:
   ```
   CHROMADB_HOST=localhost
   CHROMADB_PORT=8000
   ```

### Running the Application

Start the FastAPI server:

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.
The interactive API documentation is available at http://localhost:8000/docs.

## API Endpoints

### Documents

- `POST /api/v1/documents`: Create a new document
- `GET /api/v1/documents`: List all documents
- `GET /api/v1/documents/{document_id}`: Get a specific document
- `PUT /api/v1/documents/{document_id}`: Update a document
- `DELETE /api/v1/documents/{document_id}`: Delete a document

### Embeddings

- `GET /api/v1/embedding/chunks/{document_id}`: Get document chunks

### Search

- `POST /api/v1/search`: Search for relevant documents

### Chat

- `POST /api/v1/chat/sessions`: Create a new chat session
- `GET /api/v1/chat/sessions`: List all chat sessions
- `GET /api/v1/chat/sessions/{session_id}/messages`: Get messages in a session
- `POST /api/v1/chat/generate`: Generate a RAG-enhanced response
- `DELETE /api/v1/chat/sessions/{session_id}`: Delete a chat session
