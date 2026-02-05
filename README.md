
# Smart KYC Platform

A modular Know Your Customer (KYC) platform with a FastAPI backend and Streamlit UI, supporting async validation, document processing, and policy-driven workflows.

## Features

- **Backend (FastAPI):**
  - RESTful API for KYC case management, evidence upload, and policy handling
  - Async processing with Celery and Redis
  - PostgreSQL database integration
  - S3-compatible evidence storage
  - Modular AI plugins for document classification, field extraction, OCR, translation, and discrepancy reasoning

- **Frontend (Streamlit):**
  - User-friendly interface for case initiation, evidence upload, and case tracking
  - Real-time status updates and navigation

## Project Structure

```
citi-kyc-backend/
  app/
	 api/         # FastAPI endpoints
	 core/        # Config, logging, security
	 db/          # Database models and session
	 models/      # ORM models
	 schemas/     # Pydantic schemas
	 services/    # Business logic
	 ai/          # AI plugins and integrations
	 workflows/   # Celery tasks
	 utils/       # Utility functions
	 tests/       # Test cases

citi-kyc-ui/
  core/          # Streamlit session and UI components
  pages/         # Streamlit pages (Home, Initiate Case, Upload Evidence, Tracker)
  api/           # API client for backend
```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker (for Postgres/Redis)
- Node.js (optional, for advanced UI)

### Backend Setup

1. **Start dependencies:**
	```
	docker-compose up -d
	```

2. **Install Python dependencies:**
	```
	pip install -r requirements.txt
	```

3. **Run FastAPI server:**
	```
	uv run uvicorn app.main:app --reload --port 8000
	```

4. **Run Celery worker:**
	```
	celery -A app.workflows.celery_app.celery_app worker --loglevel=info
	celery -A app.workflows.celery_app.celery_app worker --loglevel=info --pool=solo

	```

5. **Environment variables (example):**
	```
	export USE_GEMINI_PLUGINS=true
	export GEMINI_API_KEY="YOUR_KEY"
	export GEMINI_MODEL="gemini-2.0-flash"
	```

### Frontend Setup

1. **Install Streamlit:**
	```
	pip install streamlit
	```

2. **Run the UI:**
	```
	uv run streamlit run app.py
	```

## Configuration

- Edit `app/core/config.py` for DB, Redis, S3, and service URLs.
- Use `.env` for environment-specific overrides.

## API

- Base URL: `http://localhost:8000/v1`
- Health check: `GET /health`
- Main endpoints: `/policies`, `/cases`, `/evidence`

## License

See [LICENSE](LICENSE).
