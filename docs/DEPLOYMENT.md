# SmartRetail-AI Deployment Guide

## Overview

This guide covers deploying SmartRetail-AI to various environments.

## Prerequisites

- Docker & Docker Compose
- Kubernetes cluster (for production)
- Domain name with SSL certificate
- PostgreSQL 15+
- Redis 7+

## Local Development

### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/tanvir-eece-cse/SmartRetail-AI.git
cd SmartRetail-AI

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services:**
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- ML Service: http://localhost:8001
- MLflow: http://localhost:5000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Configure Secrets

```bash
# Create secrets
kubectl create secret generic smartretail-secrets \
  --from-literal=DATABASE_PASSWORD=<your-password> \
  --from-literal=SECRET_KEY=<your-secret-key> \
  -n smartretail
```

### 3. Deploy Services

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/database.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/ml-service-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
kubectl get pods -n smartretail
kubectl get services -n smartretail
kubectl get ingress -n smartretail
```

## CI/CD Pipeline

The project includes GitHub Actions workflows for:

1. **CI Pipeline** (`.github/workflows/ci-cd.yml`)
   - Runs tests for backend, frontend, and ML service
   - Security scanning with Trivy
   - Builds and pushes Docker images
   - Deploys to Kubernetes

2. **Security Pipeline** (`.github/workflows/security.yml`)
   - CodeQL analysis
   - Dependency review
   - Secret scanning
   - Container vulnerability scanning

### Required Secrets

Configure these secrets in GitHub:

| Secret | Description |
|--------|-------------|
| `KUBECONFIG` | Base64 encoded kubeconfig |
| `CODECOV_TOKEN` | Codecov upload token |

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | Required |
| `SECRET_KEY` | JWT signing key | Required |
| `ML_SERVICE_URL` | ML service URL | http://ml-service:8001 |

### ML Service

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `MLFLOW_TRACKING_URI` | MLflow server URL | http://mlflow:5000 |
| `MODEL_PATH` | Path to ML models | /app/models |

## Monitoring

### Prometheus

Access at: http://localhost:9090

Metrics available:
- HTTP request duration
- Request count by endpoint
- Error rates
- Database connection pool

### Grafana

Access at: http://localhost:3000

Default credentials: admin / admin123

Pre-configured dashboards:
- API Performance
- ML Service Metrics
- Database Health

## Scaling

### Horizontal Pod Autoscaler

The backend and ML service include HPA configurations:

```yaml
# Backend: 3-10 replicas based on CPU/memory
# ML Service: 2-5 replicas based on CPU
```

### Database Scaling

For production, consider:
- PostgreSQL read replicas
- Redis cluster mode
- Connection pooling with PgBouncer

## Backup & Recovery

### Database Backup

```bash
# Backup
pg_dump -h localhost -U postgres smartretail > backup.sql

# Restore
psql -h localhost -U postgres smartretail < backup.sql
```

### ML Models Backup

```bash
# Models are stored in PersistentVolume
kubectl cp smartretail/ml-service-xxx:/app/models ./models-backup
```

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check DATABASE_URL format
   - Verify PostgreSQL is running
   - Check network connectivity

2. **ML models not loading**
   - Verify MODEL_PATH exists
   - Check volume mounts
   - Review ML service logs

3. **High latency**
   - Check Redis connection
   - Review database query performance
   - Scale backend replicas

### Logs

```bash
# Docker Compose
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/backend -n smartretail
```

---

For questions, contact: tanvir.eece.mist@gmail.com
