# SmartRetail-AI API Documentation

## Overview

SmartRetail-AI provides a comprehensive REST API for e-commerce analytics and AI-powered recommendations.

**Base URL:** `https://api.smartretail.example.com/api/v1`

## Authentication

All API endpoints (except auth) require Bearer token authentication.

```http
Authorization: Bearer <access_token>
```

### Obtain Token

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Endpoints

### Products

#### List Products

```http
GET /products?page=1&limit=20&category_id=1&search=phone
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| limit | int | Items per page (default: 20) |
| category_id | int | Filter by category |
| search | string | Search query |

#### Get Product

```http
GET /products/{product_id}
```

#### Create Product (Admin)

```http
POST /products
Content-Type: application/json

{
  "name": "Wireless Earbuds Pro",
  "description": "Premium wireless earbuds with ANC",
  "price": 2999.00,
  "category_id": 1,
  "stock_quantity": 100,
  "sku": "WE-PRO-001",
  "images": ["https://..."]
}
```

### Orders

#### Create Order

```http
POST /orders
Content-Type: application/json

{
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 3, "quantity": 1}
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "Dhaka",
    "postal_code": "1205"
  }
}
```

#### Get User Orders

```http
GET /orders?status=pending&page=1
```

### Recommendations

#### Get User Recommendations

```http
POST /ml/recommendations/user
Content-Type: application/json

{
  "user_id": 123,
  "limit": 10,
  "include_reasons": true
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "product_id": 45,
      "score": 0.92,
      "reason": "Based on your preferences"
    }
  ],
  "model_version": "1.0.0",
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Similar Products

```http
POST /ml/recommendations/similar
Content-Type: application/json

{
  "product_id": 45,
  "limit": 10
}
```

### Customer Segmentation

#### Segment Customers

```http
POST /ml/segmentation/segment
Content-Type: application/json

{
  "customers": [
    {
      "customer_id": 1,
      "recency": 15,
      "frequency": 8,
      "monetary": 15000
    }
  ]
}
```

**Response:**
```json
[
  {
    "customer_id": 1,
    "segment_id": 0,
    "segment_name": "Champions",
    "rfm_score": "554"
  }
]
```

### Demand Forecasting

#### Forecast Product Demand

```http
POST /ml/forecasting/demand
Content-Type: application/json

{
  "product_id": 45,
  "horizon_days": 14
}
```

### Analytics

#### Sales Overview

```http
GET /analytics/sales?period=30d
```

#### Top Products

```http
GET /analytics/top-products?limit=10&period=7d
```

## Error Responses

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## Rate Limiting

- 100 requests per minute per IP
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
