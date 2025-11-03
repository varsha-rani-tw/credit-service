# Docker Deployment Guide

This guide explains how to build, run, and deploy the Credit Service using Docker.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Building the Docker Image](#building-the-docker-image)
3. [Running with Docker Compose](#running-with-docker-compose)
4. [Running Standalone Container](#running-standalone-container)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

**Verify installations:**

```bash
docker --version
# Docker version 24.0.0 or higher

docker-compose --version
# Docker Compose version v2.20.0 or higher
```

---

## 🏗️ Building the Docker Image

### Method 1: Build Using Docker Command

```bash
# Navigate to project directory
cd /Users/varsharani/credit-service

# Build the image
docker build -t credit-service:latest .

# Build with specific tag
docker build -t credit-service:v1.0.0 .

# Build without cache (if you made dependency changes)
docker build --no-cache -t credit-service:latest .
```

**Expected Output:**

```
[+] Building 45.2s (15/15) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [builder 1/6] FROM python:3.11-slim
 => [builder 2/6] RUN apt-get update && apt-get install -y curl build-essential
 => [builder 3/6] RUN curl -sSL https://install.python-poetry.org | python3 -
 => [builder 4/6] WORKDIR /app
 => [builder 5/6] COPY pyproject.toml poetry.lock* ./
 => [builder 6/6] RUN poetry install --no-dev --no-root
 => [stage-1 1/3] WORKDIR /app
 => [stage-1 2/3] COPY --from=builder /app/.venv /app/.venv
 => [stage-1 3/3] COPY --chown=appuser:appuser . .
 => exporting to image
 => => naming to docker.io/library/credit-service:latest
```

### Method 2: Build Using Docker Compose

```bash
# Build the service defined in docker-compose.yml
docker-compose build credit-service

# Build with no cache
docker-compose build --no-cache credit-service
```

### Verify Image Was Built

```bash
docker images | grep credit-service
```

**Expected Output:**

```
credit-service    latest    abc123def456    2 minutes ago    250MB
```

---

## 🐳 Running with Docker Compose (Recommended)

This method starts the entire stack: Kafka, Zookeeper, Kafka UI, and your application.

### Step 1: Start All Services

```bash
cd /Users/varsharani/credit-service

# Start in detached mode
docker-compose up -d

# Or start with logs visible
docker-compose up
```

**Expected Output:**

```
[+] Running 5/5
 ✔ Network credit-service_credit-service-network  Created    0.1s
 ✔ Container credit-service-zookeeper             Started    0.8s
 ✔ Container credit-service-kafka                 Healthy    15.2s
 ✔ Container credit-service-kafka-init            Started    16.1s
 ✔ Container credit-service-kafka-ui              Started    16.3s
 ✔ Container credit-service-app                   Started    17.5s
```

### Step 2: Verify Services Are Running

```bash
docker-compose ps
```

**Expected Output:**

```
NAME                          STATUS              PORTS
credit-service-app            Up (healthy)        0.0.0.0:8000->8000/tcp
credit-service-kafka          Up (healthy)        0.0.0.0:9092->9092/tcp
credit-service-kafka-ui       Up                  0.0.0.0:8080->8080/tcp
credit-service-zookeeper      Up                  0.0.0.0:2181->2181/tcp
```

### Step 3: Check Application Logs

```bash
# View all logs
docker-compose logs -f

# View only credit-service logs
docker-compose logs -f credit-service

# View last 50 lines
docker-compose logs --tail=50 credit-service
```

**Healthy logs should show:**

```
credit-service-app  | 2024-11-03 10:15:30 - root - INFO - Starting up Credit Service...
credit-service-app  | 2024-11-03 10:15:31 - src.kafka.kafka_producer - INFO - Kafka producer started successfully. Connected to: ['kafka:29092']
credit-service-app  | INFO:     Application startup complete.
credit-service-app  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Test the Application

```bash
curl -X POST http://localhost:8000/simulate-cibil-score \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "pan_number": "ABCDE1234F",
    "monthly_income_inr": 80000,
    "loan_type": "HOME"
  }'
```

**Expected Response:**

```json
{
  "application_id": 1,
  "cibil_score": 700,
  "status": "success",
  "message": "CIBIL score calculated and published to Kafka successfully"
}
```

### Step 5: Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **API Documentation** | http://localhost:8000/docs | Swagger UI |
| **Kafka UI** | http://localhost:8080 | View Kafka messages |
| **Health Check** | http://localhost:8000/docs | API is responsive |

### Step 6: Stop Services

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (clears data)
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

---

## 🚀 Running Standalone Container

If you want to run just the application container (assumes Kafka is already running elsewhere):

### Step 1: Run the Container

```bash
docker run -d \
  --name credit-service \
  -p 8000:8000 \
  -e KAFKA_BOOTSTRAP_SERVERS=localhost:9092 \
  -e KAFKA_TOPIC_LOAN_APPLICATIONS=loan_applications_submitted \
  --network host \
  credit-service:latest
```

**Options Explained:**

- `-d`: Run in detached mode (background)
- `--name credit-service`: Container name
- `-p 8000:8000`: Map port 8000 (host:container)
- `-e`: Set environment variables
- `--network host`: Use host network (allows connecting to localhost Kafka)

### Step 2: Check Container Status

```bash
docker ps | grep credit-service
```

### Step 3: View Logs

```bash
docker logs -f credit-service
```

### Step 4: Stop Container

```bash
docker stop credit-service
docker rm credit-service
```

---

## ⚙️ Environment Configuration

### Docker Compose Environment (.env.docker)

The application uses `.env.docker` when running in Docker Compose:

```env
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:29092  # Use Docker service name
KAFKA_TOPIC_LOAN_APPLICATIONS=loan_applications_submitted
KAFKA_CLIENT_ID=credit-service-docker

# Application settings
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

### Standalone Container Environment

For standalone containers, pass environment variables:

```bash
docker run -d \
  -e KAFKA_BOOTSTRAP_SERVERS=your-kafka-host:9092 \
  -e KAFKA_CLIENT_ID=credit-service-prod \
  -e LOG_LEVEL=DEBUG \
  -p 8000:8000 \
  credit-service:latest
```

### All Available Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka broker addresses |
| `KAFKA_TOPIC_LOAN_APPLICATIONS` | `loan_applications_submitted` | Topic name |
| `KAFKA_CLIENT_ID` | `credit-service` | Client identifier |
| `KAFKA_COMPRESSION_TYPE` | `gzip` | Message compression |
| `KAFKA_ACKS` | `all` | Acknowledgment level |
| `KAFKA_RETRIES` | `3` | Number of retries |
| `KAFKA_REQUEST_TIMEOUT_MS` | `30000` | Request timeout |
| `KAFKA_ENABLE_IDEMPOTENCE` | `true` | Prevent duplicates |

---

## 🔧 Troubleshooting

### Problem 1: Build Fails with "poetry not found"

**Solution:** Ensure Docker has internet access to download Poetry.

```bash
# Rebuild with no cache
docker build --no-cache -t credit-service:latest .
```

### Problem 2: Container Exits Immediately

**Check logs:**

```bash
docker logs credit-service
```

**Common causes:**
- Kafka not reachable (check `KAFKA_BOOTSTRAP_SERVERS`)
- Port 8000 already in use
- Missing environment variables

### Problem 3: "Connection refused" to Kafka

**For Docker Compose:**

```bash
# Ensure Kafka is healthy
docker-compose ps

# Kafka should show "healthy" status
# If not, wait longer or check Kafka logs
docker-compose logs kafka
```

**For Standalone:**

```bash
# Use correct Kafka address
# Inside Docker: kafka:29092 (service name)
# Outside Docker: localhost:9092 (host network)
```

### Problem 4: Application Not Responding

**Check health:**

```bash
docker exec credit-service-app python -c "import requests; print(requests.get('http://localhost:8000/docs').status_code)"
```

**Should return:** `200`

### Problem 5: Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use different port
docker run -p 8001:8000 credit-service:latest
```

---

## 🏭 Production Deployment

### Best Practices

#### 1. Use Specific Image Tags

```bash
# Bad
docker build -t credit-service:latest .

# Good
docker build -t credit-service:1.0.0 .
docker build -t credit-service:$(git rev-parse --short HEAD) .
```

#### 2. Multi-Stage Build (Already Implemented)

Our Dockerfile uses multi-stage build:
- **Builder stage**: Installs dependencies
- **Runtime stage**: Only includes runtime files
- **Result**: Smaller image size (~250MB vs ~800MB)

#### 3. Run as Non-Root User (Already Implemented)

```dockerfile
USER appuser  # Security best practice
```

#### 4. Health Checks (Already Implemented)

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs', timeout=5)"
```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  credit-service:
    image: credit-service:1.0.0
    restart: always
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=prod-kafka:9092
      - KAFKA_SECURITY_PROTOCOL=SASL_SSL
      - KAFKA_SASL_USERNAME=${KAFKA_USERNAME}
      - KAFKA_SASL_PASSWORD=${KAFKA_PASSWORD}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Run:**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Container Registry

#### Push to Docker Hub

```bash
# Login
docker login

# Tag image
docker tag credit-service:latest yourusername/credit-service:1.0.0

# Push
docker push yourusername/credit-service:1.0.0
```

#### Push to AWS ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag
docker tag credit-service:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/credit-service:1.0.0

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/credit-service:1.0.0
```

### Kubernetes Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: credit-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: credit-service
  template:
    metadata:
      labels:
        app: credit-service
    spec:
      containers:
      - name: credit-service
        image: credit-service:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka:9092"
        livenessProbe:
          httpGet:
            path: /docs
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "0.5"
            memory: "256Mi"
```

**Deploy:**

```bash
kubectl apply -f deployment.yaml
```

---

## 📊 Image Size Optimization

### Current Image Size

```bash
docker images credit-service:latest
```

**Expected:** ~250MB

### Why So Small?

1. **Multi-stage build**: Build dependencies not in final image
2. **Slim base image**: `python:3.11-slim` instead of full Python
3. **No dev dependencies**: Only production packages included
4. **.dockerignore**: Tests, docs, and unnecessary files excluded

### Further Optimization (Optional)

Use Alpine Linux for even smaller size:

```dockerfile
FROM python:3.11-alpine

# Note: Requires additional build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev
```

---

## 🔍 Image Inspection

### View Image Layers

```bash
docker history credit-service:latest
```

### Inspect Image

```bash
docker inspect credit-service:latest
```

### Scan for Vulnerabilities

```bash
docker scan credit-service:latest
```

---

## 📝 Quick Reference Commands

```bash
# Build
docker build -t credit-service:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f credit-service

# Stop
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Execute command in running container
docker exec -it credit-service-app bash

# Check health
docker exec credit-service-app curl http://localhost:8000/docs
```

---

## 🎯 Summary

✅ **Dockerfile created** - Multi-stage, optimized, secure
✅ **.dockerignore created** - Excludes unnecessary files
✅ **Docker Compose updated** - Full stack deployment
✅ **Environment configuration** - Flexible configuration
✅ **Health checks** - Automatic health monitoring
✅ **Production ready** - Security best practices implemented

**Next Steps:**
1. Build the image: `docker build -t credit-service:latest .`
2. Start the stack: `docker-compose up -d`
3. Test the API: `curl http://localhost:8000/simulate-cibil-score`
4. View messages: Open `http://localhost:8080` (Kafka UI)
