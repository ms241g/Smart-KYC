# Citi KYC Backend Skeleton

## Run locally
1) Start dependencies:
docker-compose up -d

2) Install deps:
pip install -r requirements.txt

3) Run API:
uvicorn app.main:app --reload --port 8000

4) Run Celery Worker:
celery -A app.workflows.celery_app.celery_app worker --loglevel=info
