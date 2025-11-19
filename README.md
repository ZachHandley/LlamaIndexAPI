# LlamaIndexAPI

A Docker image with modern LlamaIndex and FastAPI using Astral UV for dependency management.

## Features

- **Modern LlamaIndex**: Uses the latest modular LlamaIndex packages (v0.12+)
- **UV Package Manager**: Fast, reliable Python package management with Astral UV
- **FastAPI**: High-performance async API framework
- **Multi-Modal Support**: Text and image ingestion with OpenAI integration
- **Vector Database**: Qdrant integration for efficient vector storage
- **Python 3.11+**: Modern Python with full type hints support

## Usage

### Docker

```bash
docker pull zachhandley/llamaindexapi
```

### Local Development with UV

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"

# Run the application
uvicorn app.main:start --reload
```

## Dependencies

This project uses modern, modular LlamaIndex packages:
- `llama-index-core>=0.12.0`
- `llama-index-llms-openai>=0.3.0`
- `llama-index-multi-modal-llms-openai>=0.3.0`
- `llama-index-vector-stores-qdrant>=0.4.0`

## Migration from Poetry

This project has been migrated from Poetry to UV for faster dependency resolution and installation. All dependencies have been updated to their latest stable versions.