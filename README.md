
# Policy Assistant

An AI-powered employee policy assistant built using Retrieval-Augmented Generation (RAG). It allows users to upload PDF policy documents and ask questions, receiving answers grounded in the uploaded content with source references.

## 1. Project Overview

Policy Assistant is a modular monolithic application built with Python and FastAPI.

It uses:

- PDF extraction to read policy documents.
- Token-based chunking to divide documents into smaller sections.
- Sentence Transformers to generate embeddings.
- FAISS to perform semantic similarity search.
- SQLite to persist document and chunk metadata.
- Gemini to generate answers using retrieved policy content.

The application checks retrieval relevance and applies security validation before returning answers to reduce unsupported or unsafe responses.

## 2. Features

- Upload and validate PDF documents.
- Extract text while preserving page numbers.
- Split documents into overlapping token-based chunks.
- Generate and store vector embeddings.
- Retrieve relevant policy content using semantic similarity.
- Generate context-grounded answers using Gemini.
- Return document and page references.
- Abstain when relevant policy information cannot be found.
- List and delete uploaded documents.
- Persist vector indexes and metadata across application restarts.
- Detect basic prompt-injection patterns in user questions.
- Filter suspicious retrieved document chunks.
- Validate generated answers for potentially sensitive information.

## 3. Technology Stack

| Component             | Technology            |
| --------------------- | --------------------- |
| Language              | Python 3.12           |
| Package management    | uv                    |
| API framework         | FastAPI               |
| Data validation       | Pydantic v2           |
| PDF extraction        | PyPDF                 |
| Tokenization          | tiktoken              |
| Embeddings            | Sentence Transformers |
| Embedding model       | all-MiniLM-L6-v2      |
| Vector database/index | FAISS CPU             |
| Vector similarity     | IndexFlatIP           |
| Metadata persistence  | SQLite                |
| LLM provider          | Google Gemini         |
| Testing               | pytest                |

## 4. Architecture

The application follows Clean Architecture principles and is organized into layers.

```text
API
 |
 v
Application
 |
 v
Domain

Infrastructure implements
the interfaces defined by
the inner layers.
```

### Domain Layer

Contains core business entities, interfaces and application-independent rules.

### Application Layer

Contains use cases that coordinate business operations, including document ingestion, querying and deletion. It also contains application services such as input, context and output guardrails.

### Infrastructure Layer

Contains implementations for PDF processing, embeddings, vector storage, SQLite persistence and Gemini integration.

### API Layer

Exposes HTTP endpoints through FastAPI and connects incoming requests to application use cases.

### Core

Contains application configuration, logging and application startup.

## 5. Application Workflows

### Document Ingestion

```text
PDF Upload
    |
    v
File Validation
    |
    v
PDF Text Extraction
    |
    v
Page-aware Chunking
    |
    v
Embedding Generation
    |
    v
FAISS Vector Index
    |
    v
SQLite Metadata Persistence
```

### Question Answering

```text
Employee Question
    |
    v
Input Validation
    |
    v
Input Guardrail
    |
    v
Query Embedding
    |
    v
FAISS Similarity Search
    |
    v
Relevance Filtering
    |
    v
Active Document Validation
    |
    v
Context Guardrail
    |
    v
Grounded Prompt Construction
    |
    v
Gemini Answer Generation
    |
    v
Output Guardrail
    |
    v
Answer + Source References
```

If no sufficiently relevant and safe context is retrieved, the application abstains rather than generating an unsupported answer.

Source references are generated from retrieved document metadata by the application, not from LLM-generated citations.

## 6. Configuration

The application requires a Gemini API key.

Create a `.env` file in the project root using `.env.example` as a template.

```dotenv
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Keep `.env` private. Never commit API keys or other secrets to source control.

Model availability and API quotas depend on the provider and account.

## 7. Installation and Setup

### Prerequisites

- Python 3.12
- uv package manager
- Gemini API key

### Install dependencies

```powershell
uv sync --python 3.12
```

### Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env` and provide your Gemini API key.

### Start the application

```powershell
uv run uvicorn policy_assistant.core.main:app --host 127.0.0.1 --port 8000 --reload
```

### Open Swagger UI

```text
http://127.0.0.1:8000/docs
```

## 8. API Endpoints

| Method | Endpoint                     | Purpose               |
| ------ | ---------------------------- | --------------------- |
| GET    | `/health`                  | Health check          |
| POST   | `/api/v1/documents/upload` | Upload a PDF          |
| GET    | `/api/v1/documents`        | List documents        |
| POST   | `/api/v1/chat/query`       | Ask a policy question |
| DELETE | `/api/v1/documents/{id}`   | Delete a document     |

## 9. Running Tests

Run the complete test suite:

```powershell
uv run pytest -v
```

The test suite contains unit and integration tests covering:

- Input validation and input guardrails.
- Context guardrail behavior.
- Output guardrail behavior.
- PDF validation.
- Policy query use cases.
- Chat API behavior.

## 10. Current MVP Configuration

- Maximum PDF upload size: 10 MB.
- Maximum question length: 2,000 characters.
- Chunk size: 500 tokens.
- Chunk overlap: 50 tokens.
- Embedding dimensions: 384.
- Retrieval top-k: 5.
- Similarity threshold: 0.40 (experimental; requires evaluation against a representative policy dataset).

The similarity threshold is an experimental configuration selected for the current demonstration dataset. It is not a production-calibrated relevance threshold.

## 11. Security and Production Limitations

The current application is a local, single-user MVP intended for demonstration and engineering evaluation.

### Current protections

- PDF extension, signature and size validation.
- Server-generated upload filenames.
- Environment-based API key configuration.
- Input validation.
- Input prompt-injection pattern detection.
- Retrieved-context injection pattern filtering.
- Prompt-level instructions to treat retrieved content as untrusted data.
- Generated-output filtering for potential secrets and contact information.
- Generic API error responses.
- Basic application logging.

### Current security limitations

The implemented guardrails use pattern-based validation and are not comprehensive security controls.

- Input guardrails detect selected suspicious instruction patterns, not every possible prompt-injection attempt.
- Context guardrails reject an entire suspicious chunk, which can also discard legitimate information in that chunk.
- Output guardrails use pattern matching and may not detect every type of sensitive information.
- Email addresses and phone numbers are restricted by the current output-validation configuration unless explicitly allowed.
- Prompt-level instructions do not guarantee that an LLM will always follow them.

### Not yet implemented

- Authentication and authorization.
- Role-based or tenant-based access control.
- Rate limiting.
- Malware scanning.
- Comprehensive prompt-injection protection.
- Coordinated atomic transactions across SQLite and FAISS.
- Production-grade monitoring and distributed deployment.

Do not expose this MVP to company-wide users or upload confidential company documents to an external LLM provider without appropriate authorization.

## 12. Future Production Improvements

Potential improvements include:

- Authentication and role-based access control.
- Background document ingestion.
- Robust document version lifecycle management.
- Atomic persistence and index recovery.
- Retrieval evaluation and similarity-threshold tuning.
- Stronger prompt-injection and data-leakage defenses.
- Monitoring, tracing and audit logging.
- PostgreSQL and pgvector evaluation.
- Horizontal scaling and production deployment.

These are future engineering improvements, not requirements of the current MVP.
