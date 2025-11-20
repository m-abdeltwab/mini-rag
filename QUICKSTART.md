# Mini-RAG Quick Start Guide

## Prerequisites

### Required Software
- **Python 3.10+** (recommended: Python 3.10)
- **MongoDB** (via Docker or local installation)
- **Ollama** (for local LLM support)
- **Conda** (recommended for environment management)

---

## Installation Steps

### Step 1: Clone and Navigate
```bash
cd mini-rag
```

### Step 2: Create Python Environment

**Using Conda (Recommended)**:
```bash
conda create -n mini-rag python=3.10
conda activate mini-rag
```

**Using venv** (Alternative):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
cd src
pip install -r requirements.txt
```

### Step 4: Set Up MongoDB

**Option A: Using Docker (Recommended)**:
```bash
cd ../docker
sudo docker compose up -d
```

This starts MongoDB on port `27007` with credentials `admin:admin`.

**Option B: Local MongoDB**:
Install MongoDB locally and update `.env` with your connection string.

### Step 5: Install and Configure Ollama

**Install Ollama**:
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows: Download from https://ollama.com
```

**Pull Required Models**:
```bash
ollama pull qwen3:4b-instruct-2507-q4_K_M  # For text generation
ollama pull qwen3-embedding:4b              # For embeddings
```

**Start Ollama Server**:
```bash
ollama serve  # Runs on http://localhost:11434
```

### Step 6: Configure Environment

Create `.env` file in `src/` directory:
```bash
cd ../src
cp .env.example .env  # If example exists, otherwise create manually
```

**Edit `.env` with the following configuration**:
```env
APP_NAME="mini-RAG"
APP_VERSION="0.1"

# File Upload Settings
FILE_ALLOWED_TYPES=["text/plain", "application/pdf", "text/markdown"]
FILE_MAX_SIZE=10
FILE_DEFAULT_CHUNK_SIZE=512000

# MongoDB Configuration
MONGODB_URL="mongodb://admin:admin@localhost:27007"
MONGODB_DATABASE="mini-rag"

# LLM Configuration
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"

# Ollama Configuration (uses OpenAI-compatible API)
OPENAI_API_KEY=""
OPENAI_API_URL="http://localhost:11434/v1/"
COHERE_API_KEY=""

# Model Settings
GENERATION_MODEL_ID="qwen3:4b-instruct-2507-q4_K_M"
EMBEDDING_MODEL_ID="qwen3-embedding:4b"
EMBEDDING_MODEL_SIZE=2560

# LLM Parameters (Optimized for Quality)
INPUT_DAFAULT_MAX_CHARACTERS=8000
GENERATION_DAFAULT_MAX_TOKENS=1000
GENERATION_DAFAULT_TEMPERATURE=0.3

# Vector Database Configuration
VECTOR_DB_BACKEND="QDRANT"
VECTOR_DB_PATH="./qdrant_storage"
VECTOR_DB_DISTANCE_METHOD="cosine"

# Language Settings
PRIMARY_LANG="en"
DEFAULT_LANG="en"
```

### Step 7: Start the Application

**Development Mode**:
```bash
fastapi dev main.py --host 0.0.0.0 --port 5000
```

**Production Mode**:
```bash
fastapi run main.py --host 0.0.0.0 --port 5000
```

The API will be available at:
- **API**: http://localhost:5000
- **Interactive Docs**: http://localhost:5000/docs
- **Alternative Docs**: http://localhost:5000/redoc

---

## Usage Workflow

### Complete RAG Pipeline Example

#### 1. Upload a Document
```bash
curl -X POST "http://localhost:5000/api/v1/data/upload/my-project" \
  -F "file=@/path/to/document.txt"
```

**Response**:
```json
{
  "signal": "file_upload_success",
  "file_id": "65abc123..."
}
```

#### 2. Process the Document
```bash
curl -X POST "http://localhost:5000/api/v1/data/process/my-project" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 1000,
    "overlap_size": 200,
    "do_reset": 1
  }'
```

**Parameters**:
- `chunk_size`: Characters per chunk (recommended: 800-1500)
- `overlap_size`: Overlap between chunks (recommended: 15-20% of chunk_size)
- `do_reset`: 1 to delete old chunks, 0 to keep them

**Response**:
```json
{
  "signal": "processing_success",
  "inserted_chunks": 42,
  "processed_files": 1
}
```

#### 3. Index into Vector Database
```bash
curl -X POST "http://localhost:5000/api/v1/nlp/index/push/my-project" \
  -H "Content-Type: application/json" \
  -d '{
    "do_reset": true
  }'
```

**Response**:
```json
{
  "signal": "insert_into_vectordb_success",
  "inserted_items_count": 42
}
```

#### 4. Get Collection Info (Optional)
```bash
curl -X GET "http://localhost:5000/api/v1/nlp/index/info/my-project"
```

**Response**:
```json
{
  "signal": "vectordb_collection_retrieved",
  "collection_info": {
    "vectors_count": 42,
    "indexed_vectors_count": 42,
    "points_count": 42,
    "status": "green"
  }
}
```

#### 5. Semantic Search
```bash
curl -X POST "http://localhost:5000/api/v1/nlp/index/search/my-project" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is the main topic of the document?",
    "limit": 5
  }'
```

**Response**:
```json
{
  "signal": "vectordb_search_success",
  "results": [
    {
      "score": 0.8547,
      "text": "The document discusses..."
    },
    {
      "score": 0.7821,
      "text": "Another relevant section..."
    }
  ]
}
```

#### 6. Get RAG Answer
```bash
curl -X POST "http://localhost:5000/api/v1/nlp/index/answer/my-project" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is the main topic of the document?",
    "limit": 5
  }'
```

**Response**:
```json
{
  "signal": "rag_answer_success",
  "answer": "Based on the provided documents, the main topic is...",
  "full_prompt": "System: You are a helpful...\n\nDocuments:\n...",
  "chat_history": [...]
}
```

---

## Using Postman

### Import Collection
1. Download the Postman collection: `src/assets/mini-rag-app.postman_collection.json`
2. Open Postman
3. Click "Import" → Select the JSON file
4. Collection "mini-rag-app" will be added

### Pre-configured Requests
The collection includes all endpoints with example payloads.

---

## Project Structure & File Organization

### Runtime Directories (Auto-created)

```
mini-rag/
├── src/
│   ├── projects/                    # Created at runtime
│   │   └── {project_id}/
│   │       └── files/               # Uploaded files
│   │           ├── file_20231120_123456.txt
│   │           └── document_20231120_123457.pdf
│   │
│   └── qdrant_storage/              # Created at runtime
│       └── collection_{project_id}/ # Vector embeddings
```

### MongoDB Collections

```
mini-rag database:
├── projects       # Project metadata
├── assets         # File metadata
└── chunks         # Processed text chunks
```

---

## Configuration Guide

### LLM Provider Options

**OpenAI (Cloud)**:
```env
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"
OPENAI_API_KEY="sk-..."
OPENAI_API_URL=""  # Leave empty for official API
GENERATION_MODEL_ID="gpt-4o-mini"
EMBEDDING_MODEL_ID="text-embedding-3-small"
EMBEDDING_MODEL_SIZE=1536
```

**Ollama (Local - Current Default)**:
```env
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"
OPENAI_API_KEY=""  # Can be empty
OPENAI_API_URL="http://localhost:11434/v1/"
GENERATION_MODEL_ID="qwen3:4b-instruct-2507-q4_K_M"
EMBEDDING_MODEL_ID="qwen3-embedding:4b"
EMBEDDING_MODEL_SIZE=2560
```

**Cohere**:
```env
GENERATION_BACKEND="COHERE"
EMBEDDING_BACKEND="COHERE"
COHERE_API_KEY="your-api-key"
GENERATION_MODEL_ID="command-r"
EMBEDDING_MODEL_ID="embed-english-v3.0"
EMBEDDING_MODEL_SIZE=1024
```

### Tuning Parameters

**For Better Quality**:
```env
INPUT_DAFAULT_MAX_CHARACTERS=8000      # More context
GENERATION_DAFAULT_MAX_TOKENS=1000     # Longer answers
GENERATION_DAFAULT_TEMPERATURE=0.3     # Balanced creativity
```

**For Faster Response**:
```env
INPUT_DAFAULT_MAX_CHARACTERS=4000
GENERATION_DAFAULT_MAX_TOKENS=500
GENERATION_DAFAULT_TEMPERATURE=0.1     # More deterministic
```

**For Creative Answers**:
```env
GENERATION_DAFAULT_TEMPERATURE=0.7     # More varied responses
```

---

## Troubleshooting

### Common Issues

#### 1. **"ModuleNotFoundError" on startup**
```bash
# Ensure you're in the correct environment
conda activate mini-rag
# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. **"Connection refused" - MongoDB**
```bash
# Check if MongoDB container is running
docker ps

# Restart MongoDB
cd docker
sudo docker compose restart

# Check logs
sudo docker compose logs mongodb
```

#### 3. **"Connection refused" - Ollama**
```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

#### 4. **"Collection does not exist" error**
You need to index documents first:
```bash
# 1. Upload files
# 2. Process files
# 3. Index/push to vector DB
# 4. Then search/answer
```

#### 5. **Poor Search Results / Low Scores**
- Check embedding model is correct for your language
- Ensure `EMBEDDING_MODEL_SIZE` matches your model's output
- Try adjusting chunk_size (recommended: 800-1500)
- Increase overlap_size (15-20% of chunk size)
- Use more specific queries

#### 6. **Dimension Mismatch Error**
```bash
# Delete old vector storage
rm -rf src/qdrant_storage

# Verify correct embedding size
ollama list | grep embedding

# Test embedding dimension
curl http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-embedding:4b", "input": "test"}'

# Update .env with correct EMBEDDING_MODEL_SIZE
# Re-index all documents
```

#### 7. **"AttributeError: 'QdrantClient' object has no attribute 'search'"**
This means you have old code. The codebase now uses `query_points()` instead of `search()`.

---

## Performance Tips

### 1. **Optimal Chunk Sizes by Document Type**

| Document Type | Chunk Size | Overlap |
|--------------|------------|---------|
| Technical docs | 1200-1500 | 250-300 |
| Articles/blogs | 800-1000 | 150-200 |
| Books/novels | 1000-1200 | 200-250 |
| Q&A/FAQ | 500-800 | 100-150 |

### 2. **Search Limit Guidelines**

| Query Type | Recommended Limit |
|-----------|-------------------|
| Specific question | 3-5 |
| Broad topic | 7-10 |
| Exploratory | 10-15 |

### 3. **Batch Processing**
For large document sets:
- Upload files in batches
- Process in smaller groups
- Monitor memory usage

---

## Monitoring & Debugging

### Enable Detailed Logging
FastAPI automatically logs to stdout. View logs:
```bash
# If running in terminal, logs appear directly
# With Docker/systemd, use appropriate log viewer
```

### Check Vector DB Status
```bash
# List all collections
curl http://localhost:5000/api/v1/nlp/index/info/my-project
```

### Database Queries
```bash
# Connect to MongoDB
docker exec -it mongodb mongosh -u admin -p admin

# Use database
use mini-rag

# Count documents
db.projects.countDocuments()
db.assets.countDocuments()
db.chunks.countDocuments()

# Find project
db.projects.findOne({project_id: "my-project"})
```

---

## Development Tips

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when available)
pytest
```

### Code Formatting
```bash
pip install black isort
black src/
isort src/
```

### API Documentation
Interactive API docs available at:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

---

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5000
```

### Using Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "5000"]
```

### Environment Variables
Use environment variables instead of `.env` file:
```bash
export MONGODB_URL="mongodb://user:pass@host:port"
export OPENAI_API_KEY="..."
# etc.
```

---

## Getting Help

### Resources
- **Architecture Docs**: See `ARCHITECTURE.md`
- **API Docs**: http://localhost:5000/docs
- **Postman Collection**: `src/assets/mini-rag-app.postman_collection.json`

### Checking Versions
```bash
# Python
python --version

# Dependencies
pip list

# Ollama models
ollama list

# MongoDB
docker exec mongodb mongosh --version
```

---

## Next Steps

After completing the quick start:
1. Read `ARCHITECTURE.md` for detailed system design
2. Experiment with different chunk sizes
3. Try different LLM models via Ollama
4. Customize RAG prompts in `src/stores/llm/templates/`
5. Add your own document loaders for custom formats
