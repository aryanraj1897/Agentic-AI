# Deployment Guide

This guide details instructions for deploying the Autonomous Data Analysis Agent across development, staging, and production environments using Docker, Docker Compose, and cloud containers.

---

## 1. Prerequisites

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Node.js**: Version 18+ (for local frontend dev)
- **Python**: Version 3.11+ (for local backend dev)
- **OpenAI API Key**: Required for LLM code generation and reporting.

---

## 2. Environment Setup

Create a production `.env` file in the project root:

```bash
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-production-openai-key-here
MODEL_NAME=gpt-4o

# Execution & File Limits
MAX_FILE_SIZE_MB=50
EXECUTION_TIMEOUT=30
MAX_RETRIES=3

# Server & CORS Setup
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost,http://localhost:80,http://yourdomain.com
LOG_LEVEL=INFO
```

---

## 3. Docker Compose Deployment (Single-Host Production)

To spin up backend, frontend, and sandbox isolation image in containerized mode:

```bash
# Build and start services in detached mode
docker-compose up -d --build
```

### Container Architecture
- **`backend`**: Running FastAPI under Uvicorn (`http://localhost:8000`).
- **`frontend`**: Built SPA served via Nginx with API reverse proxy (`http://localhost:80` and `http://localhost:5173`).
- **`sandbox`**: Read-only base container image tagged as `data-agent-sandbox:latest`.

### Checking Health & Logs
```bash
# View running container status
docker-compose ps

# Stream logs from backend
docker-compose logs -f backend

# Stream logs from frontend
docker-compose logs -f frontend
```

---

## 4. Manual / Kubernetes / Cloud Container Deployment

For cloud platforms (AWS ECS, GCP Cloud Run, Azure Container Apps, Kubernetes):

### Building Production Images
```bash
# Backend Image
docker build -t your-registry/data-agent-backend:latest ./backend
docker push your-registry/data-agent-backend:latest

# Frontend Image
docker build -t your-registry/data-agent-frontend:latest ./frontend
docker push your-registry/data-agent-frontend:latest

# Sandbox Image
docker build -t your-registry/data-agent-sandbox:latest ./sandbox
docker push your-registry/data-agent-sandbox:latest
```

---

## 5. Security & Scaling Recommendations

1. **API Keys**: Inject `OPENAI_API_KEY` via cloud secret manager (AWS Secrets Manager, GCP Secret Manager).
2. **Persistent Volumes**: Mount persistent storage for `/app/uploads` and `/app/generated` directories or store in S3/GCS.
3. **Database**: For high concurrency, configure `DATABASE_URL` pointing to PostgreSQL instance (`postgresql://user:pass@db-host:5432/dataagent`).
4. **Ingress SSL**: Configure TLS certificates via Nginx or Cloud Load Balancer.
