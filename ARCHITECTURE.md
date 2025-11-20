# Mini-RAG Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Design Patterns](#design-patterns)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)

---

## System Overview

Mini-RAG is a **Retrieval-Augmented Generation (RAG)** system built with FastAPI that enables semantic search and AI-powered question answering over your documents.

### What is RAG?

RAG combines two powerful AI capabilities:
1. **Retrieval**: Finding relevant document chunks using semantic search (vector similarity)
2. **Generation**: Using an LLM to generate natural language answers based on retrieved context

### Key Features

- 📄 **Multi-format Support**: Text files (.txt), PDFs (.pdf), and Markdown (.md)
- 🔍 **Semantic Search**: Find relevant information using meaning, not just keywords
- 🤖 **AI Answers**: Get coherent answers generated from your documents
- 🏗️ **Modular Design**: Pluggable LLM and vector database providers
- 🐳 **Docker Support**: Easy deployment with MongoDB containerization
- 🌐 **Local-First**: Works with local LLMs via Ollama (no cloud dependency)

---

## Core Components

### 1. **API Layer** (`routes/`)

The REST API provides three main endpoint groups:

#### **Base Routes** (`base.py`)
- Health checks and system information
- Entry point: `/`

#### **Data Routes** (`data.py`)
- **Upload**: `POST /api/v1/data/upload/{project_id}`
  - Accept file uploads (TXT, PDF, MD)
  - Validate file types and sizes
  - Store files in project-specific directories
  
- **Process**: `POST /api/v1/data/process/{project_id}`
  - Extract text from uploaded files
  - Split text into overlapping chunks
  - Store chunks in MongoDB with metadata

#### **NLP Routes** (`nlp.py`)
- **Index/Push**: `POST /api/v1/nlp/index/push/{project_id}`
  - Generate embeddings for all document chunks
  - Store vectors in Qdrant vector database
  
- **Search**: `POST /api/v1/nlp/index/search/{project_id}`
  - Perform semantic search using query embeddings
  - Return top-K most similar document chunks
  
- **Answer**: `POST /api/v1/nlp/index/answer/{project_id}`
  - Retrieve relevant documents
  - Generate AI answer using LLM with RAG prompts
  
- **Info**: `GET /api/v1/nlp/index/info/{project_id}`
  - Get vector collection metadata and statistics

---

### 2. **Controllers Layer** (`controllers/`)

Controllers implement business logic and orchestrate operations.

#### **DataController** (`DataController.py`)
```python
- validate_uploaded_file()  # Check file type and size
- generate_unique_filepath() # Create unique filenames with timestamps
```

#### **ProcessController** (`ProcessController.py`)
```python
- get_file_loader()         # Factory for file type loaders (TXT/PDF/MD)
- get_file_content()        # Load and parse file content
- process_file_content()    # Split text into chunks with overlap
```

Uses **LangChain** components:
- `TextLoader` for .txt files
- `PyMuPDFLoader` for .pdf files
- `UnstructuredMarkdownLoader` for .md files
- `RecursiveCharacterTextSplitter` for intelligent text chunking

#### **NLPController** (`NLPController.py`)
```python
- create_collection_name()           # Generate collection ID from project
- index_into_vector_db()            # Embed and store chunks
- search_vector_db_collection()     # Semantic search
- answer_rag_question()             # Full RAG pipeline
- get_vector_db_collection_info()   # Collection metadata
```

#### **ProjectController** (`ProjectController.py`)
```python
- get_project_path()     # Get filesystem path for project
- ensure directories exist
```

---

### 3. **Models Layer** (`models/`)

#### **Database Schemes** (`db_schemes/`)

Pydantic models for MongoDB documents:

**Project** (`project.py`)
```python
{
  "project_id": str,        # Unique project identifier
  "created_at": datetime,
  "updated_at": datetime
}
```

**Asset** (`asset.py`)
```python
{
  "asset_project_id": ObjectId,  # Reference to project
  "asset_type": str,             # "file", "url", etc.
  "asset_name": str,             # File ID/name
  "asset_size": int,             # File size in bytes
  "created_at": datetime
}
```

**DataChunk** (`data_chunk.py`)
```python
{
  "chunk_text": str,           # Extracted text content
  "chunk_metadata": dict,      # Source file, page number, etc.
  "chunk_order": int,          # Position in source document
  "chunk_project_id": ObjectId,
  "chunk_asset_id": ObjectId,
  "created_at": datetime
}
```

**RetrievedDocument** (in-memory model)
```python
{
  "score": float,    # Similarity score (0-1)
  "text": str        # Retrieved chunk text
}
```

#### **Data Models** (`*Model.py`)

MongoDB interaction layer using Motor (async MongoDB driver):

**ProjectModel** - Manages projects
**AssetModel** - Manages uploaded files
**ChunkModel** - Manages text chunks

All models implement:
- `create_instance()` - Factory with DB client injection
- `create_*()` - Insert operations
- `get_*()` - Query operations
- `delete_*()` - Deletion operations

---

### 4. **Stores Layer** (`stores/`)

#### **LLM Store** (`stores/llm/`)

**Factory Pattern**: `LLMProviderFactory`
- Creates provider instances based on config
- Supports: OpenAI (including Ollama), Cohere

**Providers**:

**OpenAIProvider** (`providers/OpenAIProvider.py`)
```python
# Works with both OpenAI API and Ollama (OpenAI-compatible)
- generate_text()   # Text generation with chat history
- embed_text()      # Convert text to embeddings
- set_generation_model()
- set_embedding_model()
```

**CoHereProvider** (`providers/CoHereProvider.py`)
```python
# Cohere API integration
- generate_text()
- embed_text()
```

**Templates** (`templates/`)

Prompt engineering for RAG:

```python
# System Prompt - Sets AI behavior and guidelines
system_prompt = """
You are a helpful and knowledgeable assistant.
Guidelines:
1. Use ONLY information from provided documents
2. Cite sources when relevant
3. Be accurate and complete
...
"""

# Document Prompt - Formats each retrieved chunk
document_prompt = """
---
Document #$doc_num:
$chunk_text
---
"""

# Footer Prompt - Final question formatting
footer_prompt = """
Based on documents above, answer:
Question: $query
Answer:
"""
```

#### **Vector DB Store** (`stores/vectordb/`)

**Factory Pattern**: `VectorDBProviderFactory`
- Creates provider instances
- Currently supports: Qdrant

**QdrantDBProvider** (`providers/QdrantDBProvider.py`)
```python
- connect()                  # Initialize client
- create_collection()        # Create vector collection with dimension
- insert_one()              # Insert single vector
- insert_many()             # Batch insert with batching
- search_by_vector()        # Vector similarity search
- is_collection_existed()   # Check collection exists
- get_collection_info()     # Get metadata
- delete_collection()       # Remove collection
```

Uses **Qdrant** local storage mode:
- Stores vectors on disk (no separate server needed)
- Supports COSINE and DOT distance metrics
- Efficient similarity search with HNSW index

---

### 5. **Configuration** (`helpers/config.py`)

**Settings Management** using Pydantic Settings:
- Auto-loads from `.env` file
- Type validation and conversion
- Environment variable override support

**Key Configuration Groups**:

1. **Application**
   - `APP_NAME`, `APP_VERSION`

2. **File Handling**
   - `FILE_ALLOWED_TYPES`, `FILE_MAX_SIZE`, `FILE_DEFAULT_CHUNK_SIZE`

3. **Database**
   - `MONGODB_URL`, `MONGODB_DATABASE`

4. **LLM Configuration**
   - `GENERATION_BACKEND`, `EMBEDDING_BACKEND`
   - `GENERATION_MODEL_ID`, `EMBEDDING_MODEL_ID`
   - `INPUT_DAFAULT_MAX_CHARACTERS`, `GENERATION_DAFAULT_MAX_TOKENS`
   - `GENERATION_DAFAULT_TEMPERATURE`

5. **Vector Database**
   - `VECTOR_DB_BACKEND`, `VECTOR_DB_PATH`, `VECTOR_DB_DISTANCE_METHOD`

6. **Internationalization**
   - `PRIMARY_LANG`, `DEFAULT_LANG`

---

## Design Patterns

### 1. **Factory Pattern**
Used for LLM and VectorDB providers to enable easy swapping of implementations.

```python
# Switch from OpenAI to Cohere by changing config
GENERATION_BACKEND = "COHERE"  # or "OPENAI"
```

### 2. **Repository Pattern**
Data models abstract MongoDB operations, separating data access from business logic.

### 3. **Dependency Injection**
FastAPI's dependency system injects settings and clients into routes.

### 4. **Async/Await**
All I/O operations (DB, file, API) use async for better performance.

### 5. **Strategy Pattern**
Different file loaders (TXT, PDF, MD) implement same interface.

---

## Data Flow

### **Document Ingestion Flow**

```
1. Upload File
   ↓
2. Validate (type, size)
   ↓
3. Save to filesystem (/projects/{id}/files/)
   ↓
4. Create Asset record in MongoDB
   ↓
5. Process File
   ↓
6. Extract text using appropriate loader
   ↓
7. Split into chunks (with overlap)
   ↓
8. Store chunks in MongoDB with metadata
```

### **Indexing Flow**

```
1. Fetch chunks from MongoDB (paginated)
   ↓
2. Generate embeddings for each chunk
   ↓
3. Create/Reset Qdrant collection
   ↓
4. Batch insert vectors with payloads
   ↓
5. Build HNSW index (automatic)
```

### **Search Flow**

```
1. Receive user query
   ↓
2. Generate query embedding
   ↓
3. Vector similarity search in Qdrant
   ↓
4. Retrieve top-K chunks with scores
   ↓
5. Return results with metadata
```

### **RAG Answer Flow**

```
1. Search (steps above)
   ↓
2. Format documents with template
   ↓
3. Construct prompt (system + docs + query)
   ↓
4. Call LLM with chat history
   ↓
5. Return generated answer + sources
```

---

## Technology Stack

### **Backend Framework**
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### **Database**
- **MongoDB** - Document store for metadata and chunks
- **Motor** - Async MongoDB driver
- **Qdrant** - Vector database for embeddings

### **AI/ML**
- **OpenAI SDK** - LLM API client (also works with Ollama)
- **Cohere SDK** - Alternative LLM provider
- **LangChain** - Document loaders and text splitters

### **File Processing**
- **PyMuPDF** - PDF parsing
- **Unstructured** - Markdown processing
- **aiofiles** - Async file I/O

### **Development**
- **Python 3.10+** - Core language
- **Conda** - Environment management
- **Docker** - Containerization

---

## Project Structure

```
mini-rag/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                   # Configuration (not in git)
│   │
│   ├── routes/                # API endpoints
│   │   ├── base.py
│   │   ├── data.py            # Upload/Process endpoints
│   │   ├── nlp.py             # Search/Answer endpoints
│   │   └── schemes/           # Request/Response models
│   │
│   ├── controllers/           # Business logic
│   │   ├── BaseController.py
│   │   ├── DataController.py
│   │   ├── ProcessController.py
│   │   ├── NLPController.py
│   │   └── ProjectController.py
│   │
│   ├── models/                # Data layer
│   │   ├── BaseDataModel.py
│   │   ├── ProjectModel.py
│   │   ├── AssetModel.py
│   │   ├── ChunkModel.py
│   │   ├── db_schemes/        # MongoDB schemas
│   │   └── enums/             # Constants
│   │
│   ├── stores/                # External service adapters
│   │   ├── llm/               # LLM providers
│   │   │   ├── LLMProviderFactory.py
│   │   │   ├── providers/     # OpenAI, Cohere
│   │   │   └── templates/     # RAG prompts
│   │   │
│   │   └── vectordb/          # Vector DB providers
│   │       ├── VectorDBProviderFactory.py
│   │       └── providers/     # Qdrant
│   │
│   └── helpers/               # Utilities
│       └── config.py          # Settings management
│
├── docker/                    # Docker services
│   └── docker-compose.yml     # MongoDB container
│
├── projects/                  # User data (created at runtime)
│   └── {project_id}/
│       └── files/             # Uploaded files
│
├── qdrant_storage/           # Vector DB data (created at runtime)
│
└── README.md                 # This file
```

---

## Key Improvements & Optimizations

### Recent Enhancements

1. **Qdrant API Updates** (v1.16.0)
   - Migrated from `search()` to `query_points()`
   - Migrated from `upload_records()` to `upsert()`
   - Migrated from `models.Record` to `models.PointStruct`

2. **Markdown Support**
   - Added `.md` file processing
   - Integrated `UnstructuredMarkdownLoader`

3. **Configuration Tuning**
   - Increased `INPUT_DAFAULT_MAX_CHARACTERS` to 8000 (from 1024)
   - Increased `GENERATION_DAFAULT_MAX_TOKENS` to 1000 (from 200)
   - Adjusted `GENERATION_DAFAULT_TEMPERATURE` to 0.3 (from 0.1)

4. **Embedding Size Correction**
   - Fixed `qwen3-embedding:4b` dimension to 2560 (was incorrectly 384)

5. **Improved RAG Prompts**
   - More structured system instructions
   - Clearer document formatting
   - Better question-answer flow

### Performance Considerations

**Chunking Strategy**:
- Recommended chunk_size: 800-1500 characters
- Recommended overlap: 15-20% of chunk_size
- Balances context vs. precision

**Search Parameters**:
- limit=3-5 for most queries (balance relevance vs. noise)
- Higher limits (7-10) for broad exploratory queries

**Batch Processing**:
- Embedding generation: Processes sequentially (to avoid rate limits)
- Vector insertion: Batches of 50 (configurable)
- Chunk retrieval from MongoDB: Paginated

---

## Security Considerations

1. **File Validation**: Type and size checks before processing
2. **Path Sanitization**: Prevents directory traversal attacks
3. **Database Isolation**: Projects stored in separate collections
4. **API Key Security**: Stored in `.env`, not committed to git
5. **Error Handling**: Logs errors without exposing internals

---

## Scalability Notes

**Current Design** (Single-server deployment):
- MongoDB: Handles metadata and chunks
- Qdrant: Local file-based storage
- FastAPI: Single process (can scale with Gunicorn/multiple workers)

**Future Scaling Options**:
1. Use Qdrant server mode (instead of local)
2. Implement caching layer (Redis)
3. Queue processing for heavy operations (Celery)
4. Horizontal scaling with load balancer
5. Separate read/write databases

---

## Next Steps & Roadmap

Potential enhancements:
- [ ] Add user authentication
- [ ] Implement multi-tenancy
- [ ] Support more file types (DOCX, HTML)
- [ ] Add re-ranking for better retrieval
- [ ] Implement streaming responses
- [ ] Add conversation memory/history
- [ ] Create web UI
- [ ] Add monitoring and analytics
- [ ] Implement incremental updates (avoid full re-indexing)
- [ ] Support hybrid search (keyword + semantic)
