# 🛒 SmartRetail-AI

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28+-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **AI-Powered E-commerce Analytics & Recommendation Platform** - A production-ready full-stack application demonstrating advanced software engineering, machine learning, and DevSecOps practices.

![SmartRetail-AI Dashboard](docs/images/dashboard-preview.png)

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [ML Models](#-ml-models)
- [DevSecOps](#-devsecops)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Author](#-author)
- [License](#-license)

## 🎯 Overview

**SmartRetail-AI** is a comprehensive e-commerce analytics and recommendation platform designed for the rapidly growing retail sector in Bangladesh. This platform helps e-commerce businesses:

- **Personalize** shopping experiences with AI-powered product recommendations
- **Analyze** customer behavior patterns and purchasing trends
- **Predict** inventory demands using machine learning
- **Optimize** marketing campaigns with customer segmentation
- **Monitor** real-time sales analytics and KPIs

### Why This Project?

Bangladesh's e-commerce market is projected to reach **$8.5 billion by 2025**, with platforms like Daraz, Chaldal, and Evaly leading the digital transformation. This project demonstrates the technical skills required to build and scale such platforms.

## ✨ Key Features

### 🤖 Machine Learning Capabilities
- **Product Recommendation Engine** - Collaborative filtering & content-based recommendations
- **Customer Segmentation** - RFM analysis with K-Means clustering
- **Demand Forecasting** - Time series prediction for inventory optimization
- **Sentiment Analysis** - Product review analysis using NLP
- **Churn Prediction** - Identify at-risk customers

### 🛍️ E-commerce Features
- **Product Catalog Management** - Full CRUD with categories and variants
- **User Authentication** - JWT-based auth with OAuth2 support
- **Shopping Cart & Wishlist** - Persistent cart with real-time updates
- **Order Management** - Complete order lifecycle tracking
- **Search & Filtering** - Elasticsearch-powered full-text search
- **Review & Rating System** - Customer feedback with sentiment scores

### 📊 Analytics Dashboard
- **Real-time Sales Analytics** - Live revenue and order tracking
- **Customer Insights** - Behavioral analytics and cohort analysis
- **Product Performance** - Best sellers, conversion rates, and trends
- **Inventory Analytics** - Stock levels and reorder predictions
- **Marketing Analytics** - Campaign performance and ROI tracking

### 🔒 Security Features
- **OWASP Compliance** - Protection against common vulnerabilities
- **Rate Limiting** - API abuse prevention
- **Data Encryption** - AES-256 encryption for sensitive data
- **Audit Logging** - Complete activity trail
- **GDPR Compliance** - Data privacy and consent management

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LOAD BALANCER (Nginx/Ingress)                   │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│   Frontend    │           │   Backend     │           │  ML Service   │
│   (React)     │◄─────────►│   (FastAPI)   │◄─────────►│  (FastAPI)    │
│   Port: 3000  │           │   Port: 8000  │           │   Port: 8001  │
└───────────────┘           └───────┬───────┘           └───────┬───────┘
                                    │                           │
                    ┌───────────────┼───────────────┐           │
                    │               │               │           │
                    ▼               ▼               ▼           ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
            │PostgreSQL │   │   Redis   │   │Elasticsearch│  │  MLflow   │
            │   :5432   │   │   :6379   │   │   :9200   │   │   :5000   │
            └───────────┘   └───────────┘   └───────────┘   └───────────┘
                    │
                    ▼
            ┌───────────────────────────────────────────────────────────┐
            │                    Monitoring Stack                        │
            │  ┌───────────┐  ┌───────────┐  ┌───────────┐              │
            │  │Prometheus │  │  Grafana  │  │  Jaeger   │              │
            │  │   :9090   │  │   :3001   │  │  :16686   │              │
            │  └───────────┘  └───────────┘  └───────────┘              │
            └───────────────────────────────────────────────────────────┘
```

### Microservices Architecture

| Service | Description | Technology |
|---------|-------------|------------|
| **Frontend** | React SPA with TypeScript | React 18, Vite, TailwindCSS |
| **Backend API** | Core business logic & REST API | FastAPI, SQLAlchemy, Pydantic |
| **ML Service** | Machine learning inference & training | FastAPI, Scikit-learn, TensorFlow |
| **Database** | Primary data storage | PostgreSQL 15 |
| **Cache** | Session & query caching | Redis 7 |
| **Search** | Full-text search engine | Elasticsearch 8 |
| **ML Tracking** | Model versioning & experiments | MLflow |

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language |
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| Pydantic | Data validation |
| Celery | Task queue |
| pytest | Testing |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI library |
| TypeScript | Type safety |
| Vite | Build tool |
| TailwindCSS | Styling |
| React Query | Data fetching |
| Zustand | State management |
| Vitest | Testing |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| Scikit-learn | Classical ML |
| TensorFlow | Deep learning |
| Pandas | Data manipulation |
| NumPy | Numerical computing |
| MLflow | Model tracking |
| SHAP | Model explainability |

### DevSecOps
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Kubernetes | Orchestration |
| GitHub Actions | CI/CD |
| Terraform | Infrastructure as Code |
| Prometheus | Monitoring |
| Grafana | Visualization |
| Trivy | Security scanning |
| SonarQube | Code quality |

## 🚀 Getting Started

### Prerequisites

- **Docker** v24.0+
- **Docker Compose** v2.20+
- **Node.js** v18+ (for local frontend development)
- **Python** v3.11+ (for local backend development)
- **Git** v2.40+

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/tanvir-eece-cse/SmartRetail-AI.git
cd SmartRetail-AI

# Copy environment files
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# ML Service: http://localhost:8001
# Grafana: http://localhost:3001
```

### Local Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed sample data
python -m app.scripts.seed_data

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### ML Service Setup
```bash
cd ml-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train initial models
python -m app.training.train_all

# Start the service
uvicorn app.main:app --reload --port 8001
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smartretail
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Service
ML_SERVICE_URL=http://localhost:8001
MLFLOW_TRACKING_URI=http://localhost:5000

# External Services
ELASTICSEARCH_URL=http://localhost:9200
SENTRY_DSN=your-sentry-dsn
```

## 📚 API Documentation

### REST API Endpoints

#### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh token |
| POST | `/api/v1/auth/logout` | User logout |

#### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products` | List products |
| GET | `/api/v1/products/{id}` | Get product details |
| POST | `/api/v1/products` | Create product (Admin) |
| PUT | `/api/v1/products/{id}` | Update product (Admin) |
| DELETE | `/api/v1/products/{id}` | Delete product (Admin) |

#### Recommendations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/recommendations/user/{user_id}` | Get personalized recommendations |
| GET | `/api/v1/recommendations/product/{product_id}` | Get similar products |
| GET | `/api/v1/recommendations/trending` | Get trending products |

#### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/sales` | Sales analytics |
| GET | `/api/v1/analytics/customers` | Customer analytics |
| GET | `/api/v1/analytics/products` | Product analytics |

📖 **Full API documentation available at:** `/docs` (Swagger UI) or `/redoc` (ReDoc)

## 🤖 ML Models

### 1. Product Recommendation Engine

**Algorithm:** Hybrid Collaborative Filtering + Content-Based

```python
# Example usage
recommendations = recommendation_engine.get_recommendations(
    user_id=123,
    n_recommendations=10,
    include_reasons=True
)
```

**Features:**
- User-item interaction matrix
- Product embeddings from descriptions
- Real-time personalization
- A/B testing support

**Metrics:**
- Precision@10: 0.82
- Recall@10: 0.75
- NDCG@10: 0.88

### 2. Customer Segmentation

**Algorithm:** K-Means with RFM Analysis

| Segment | Description | Action |
|---------|-------------|--------|
| Champions | High value, frequent buyers | Reward loyalty |
| Loyal | Regular customers | Upsell premium |
| At Risk | Previously active, now dormant | Re-engagement |
| New | Recent first-time buyers | Onboarding |

### 3. Demand Forecasting

**Algorithm:** LSTM Neural Network + Prophet

- Predicts product demand for next 30 days
- Accounts for seasonality and trends
- Integrates external factors (holidays, promotions)

### 4. Churn Prediction

**Algorithm:** XGBoost Classifier

- Identifies customers likely to churn
- Feature importance analysis
- Automated intervention triggers

## 🔄 DevSecOps

### CI/CD Pipeline

```yaml
# GitHub Actions workflow stages
stages:
  - lint          # Code quality checks
  - test          # Unit & integration tests
  - security      # Vulnerability scanning
  - build         # Docker image build
  - deploy        # Kubernetes deployment
```

### Security Scanning

- **SAST:** SonarQube for static analysis
- **DAST:** OWASP ZAP for dynamic testing
- **Container:** Trivy for image scanning
- **Dependencies:** Dependabot for updates

### Infrastructure as Code

```hcl
# Terraform modules
modules/
├── vpc/           # Network configuration
├── eks/           # Kubernetes cluster
├── rds/           # Database
├── elasticache/   # Redis cluster
└── monitoring/    # Observability stack
```

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm run test

# E2E tests
npm run test:e2e

# Load testing
locust -f tests/load/locustfile.py
```

### Test Coverage

| Component | Coverage |
|-----------|----------|
| Backend | 85%+ |
| Frontend | 80%+ |
| ML Service | 75%+ |

## 📦 Deployment

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n smartretail
```

### Helm Chart

```bash
# Install using Helm
helm install smartretail ./helm/smartretail \
  --namespace smartretail \
  --values ./helm/values-production.yaml
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

<div align="center">
  <img src="https://github.com/tanvir-eece-cse.png" width="100" height="100" style="border-radius: 50%;">
  
  ### **Md. Tanvir Hossain**
  
  🎓 **M.Sc. in CSE** (Pursuing) - BRAC University  
  🎓 **B.Sc. in EECE** - Military Institute of Science and Technology (MIST)
  
  [![GitHub](https://img.shields.io/badge/GitHub-tanvir--eece--cse-181717?style=for-the-badge&logo=github)](https://github.com/tanvir-eece-cse)
  [![LinkedIn](https://img.shields.io/badge/LinkedIn-tanvir--eece-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/tanvir-eece/)
  [![Email](https://img.shields.io/badge/Email-tanvir.eece.mist@gmail.com-EA4335?style=for-the-badge&logo=gmail)](mailto:tanvir.eece.mist@gmail.com)
</div>

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  
  ⭐ **Star this repository if you find it helpful!** ⭐
  
  Made with ❤️ in Bangladesh 🇧🇩
  
</div>
