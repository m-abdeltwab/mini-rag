# Mini-RAG: Retrieval-Augmented Generation System

A production-ready RAG (Retrieval-Augmented Generation) system built with FastAPI that enables semantic search and AI-powered question answering over your documents.

## 🌟 Features

- 📄 **Multi-Format Support**: Process `.txt`, `.pdf`, and `.md` files
- 🔍 **Semantic Search**: Find relevant information using meaning, not just keywords
- 🤖 **AI-Powered Answers**: Generate accurate answers from your documents using LLMs
- 🏗️ **Modular Architecture**: Easily swap LLM providers (OpenAI, Ollama, Cohere)
- 🐳 **Docker Ready**: Simple deployment with containerized MongoDB
- 🌐 **Local-First**: Works with Ollama for completely local, private AI
- ⚡ **Async Processing**: Fast, non-blocking operations
- 📊 **Vector Database**: Efficient similarity search with Qdrant

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in minutes
- **[Architecture Documentation](ARCHITECTURE.md)** - Detailed system design and components
- **[API Documentation](http://localhost:5000/docs)** - Interactive API docs (when server is running)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker (for MongoDB)
- Ollama (for local LLM) or OpenAI API key

### Installation

```bash
# 1. Create environment
conda create -n mini-rag python=3.10
conda activate mini-rag

# 2. Install dependencies
cd src
pip install -r requirements.txt

# 3. Start MongoDB
cd ../docker
sudo docker compose up -d

# 4. Install Ollama models
ollama pull qwen3:4b-instruct-2507-q4_K_M
ollama pull qwen3-embedding:4b

# 5. Configure environment
cd ../src
cp .env.example .env  # Edit with your settings

# 6. Start the server
fastapi dev main.py --host 0.0.0.0 --port 5000
```

Visit http://localhost:5000/docs for interactive API documentation.

### Basic Usage

```bash
# 1. Upload a document
curl -X POST "http://localhost:5000/api/v1/data/upload/my-project" \
  -F "file=@document.pdf"

# 2. Process the document
curl -X POST "http://localhost:5000/api/v1/data/process/my-project" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size": 1000, "overlap_size": 200, "do_reset": 1}'

# 3. Index into vector database
curl -X POST "http://localhost:5000/api/v1/nlp/index/push/my-project" \
  -H "Content-Type: application/json" \
  -d '{"do_reset": true}'

# 4. Ask questions
curl -X POST "http://localhost:5000/api/v1/nlp/index/answer/my-project" \
  -H "Content-Type: application/json" \
  -d '{"text": "What is this document about?", "limit": 5}'
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Vector search powered by [Qdrant](https://qdrant.tech/)
- Document processing with [LangChain](https://python.langchain.com/)
- Local LLM support via [Ollama](https://ollama.com/)

---

## 📞 Support

- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) and [QUICKSTART.md](QUICKSTART.md)
- **API Reference**: <http://localhost:5000/docs> (when server is running)
- **Issues**: For bugs and feature requests, please open an issue

---

**Happy RAG-ing! 🚀**


## 📋 Requirements

### System Requirements

- Python 3.10 or later
- Docker (for MongoDB container)
- 4GB+ RAM recommended
- 10GB+ free disk space

### Optional

- **Ollama** - For local LLM inference (privacy-focused)
- **OpenAI API Key** - For cloud-based LLM
- **Cohere API Key** - Alternative LLM provider

---

## 💻 Detailed Installation

For complete installation instructions, see **[QUICKSTART.md](QUICKSTART.md)**.

### Python Environment Setup

**Using MiniConda (Recommended)**:

1. Download and install [MiniConda](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)

2. Create a new environment:

```bash
conda create -n mini-rag python=3.10
```

3. Activate the environment:

```bash
conda activate mini-rag
```

### Install Dependencies

```bash
cd src
pip install -r requirements.txt
```

### Environment Configuration

Create `.env` file in the `src/` directory with your settings. See `.env.example` or [QUICKSTART.md](QUICKSTART.md) for configuration details.

Key settings:
- `MONGODB_URL` - MongoDB connection string
- `GENERATION_MODEL_ID` - LLM for text generation
- `EMBEDDING_MODEL_ID` - Model for text embeddings
- `EMBEDDING_MODEL_SIZE` - Embedding dimension (must match model)

---

## 🐳 Running with Docker

### Start MongoDB

```bash
cd docker
sudo docker compose up -d
```

This starts MongoDB on `localhost:27007` with default credentials (see `docker/.env`).

---

## 🚀 Start the Server

### Development Mode

```bash
cd src
fastapi dev main.py --host 0.0.0.0 --port 5000
```

### Production Mode

```bash
fastapi run main.py --host 0.0.0.0 --port 5000
```

**Access Points**:
- API: <http://localhost:5000>
- Interactive Docs: <http://localhost:5000/docs>
- Alternative Docs: <http://localhost:5000/redoc>

---

## 📖 API Usage

### Postman Collection

Download the Postman collection: `src/assets/mini-rag-app.postman_collection.json`

Import into Postman for pre-configured API requests.

### Complete Workflow Example

See [QUICKSTART.md](QUICKSTART.md) for detailed API examples and best practices.

**Pipeline Steps**:
1. Upload documents
2. Process into chunks
3. Index into vector database
4. Search or get AI answers

---

## 🏗️ Project Architecture

```
mini-rag/
├── src/
│   ├── main.py              # FastAPI application entry
│   ├── routes/              # API endpoints
│   ├── controllers/         # Business logic
│   ├── models/              # Data models & schemas
│   ├── stores/              # LLM & Vector DB adapters
│   └── helpers/             # Utilities & config
├── docker/                  # Docker services
├── ARCHITECTURE.md          # System design docs
├── QUICKSTART.md           # Setup guide
└── README.md               # This file
```

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for detailed component documentation.

---

## ⚙️ Configuration Examples

### Using Ollama (Local, Private)

```env
GENERATION_BACKEND="OPENAI"
OPENAI_API_URL="http://localhost:11434/v1/"
GENERATION_MODEL_ID="qwen3:4b-instruct-2507-q4_K_M"
EMBEDDING_MODEL_ID="qwen3-embedding:4b"
EMBEDDING_MODEL_SIZE=2560
```


See [QUICKSTART.md](QUICKSTART.md) for more configuration options.

---

## 🔧 Troubleshooting

### Common Issues

**MongoDB Connection Error**:

```bash
sudo docker compose restart
```

**Ollama Connection Error**:

```bash
ollama serve
```

**Vector Dimension Mismatch**:

```bash
rm -rf src/qdrant_storage
# Update EMBEDDING_MODEL_SIZE in .env
# Re-index documents
```

See [QUICKSTART.md](QUICKSTART.md) for comprehensive troubleshooting.

---

## 📚 Learning Resources

### Video Course (Arabic)

This educational project is explained step-by-step in Arabic YouTube videos:
[mini-RAG Course](https://www.youtube.com/playlist?list=PLvLvlVqNQGHCUR2p0b8a0QpVjDUg50wQj)