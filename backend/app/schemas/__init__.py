"""Schemas module initialization."""

from app.schemas.schemas import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
    CategoryCreate,
    CategoryResponse,
    CategoryTree,
    CategoryUpdate,
    CustomerAnalytics,
    LoginRequest,
    OrderCreate,
    OrderItemCreate,
    OrderItemResponse,
    OrderResponse,
    OrderStatusUpdate,
    PaginatedResponse,
    ProductAnalytics,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    RecommendationRequest,
    RecommendationResponse,
    RecommendedProduct,
    RefreshTokenRequest,
    ReviewCreate,
    ReviewResponse,
    SalesAnalytics,
    Token,
    TokenPayload,
    UserCreate,
    UserProfile,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RefreshTokenRequest",
    # Product
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductListResponse",
    # Category
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryTree",
    # Order
    "OrderCreate",
    "OrderItemCreate",
    "OrderItemResponse",
    "OrderResponse",
    "OrderStatusUpdate",
    # Review
    "ReviewCreate",
    "ReviewResponse",
    # Cart
    "CartItemCreate",
    "CartItemUpdate",
    "CartItemResponse",
    "CartResponse",
    # Recommendation
    "RecommendationRequest",
    "RecommendationResponse",
    "RecommendedProduct",
    # Analytics
    "SalesAnalytics",
    "CustomerAnalytics",
    "ProductAnalytics",
    # Utils
    "PaginatedResponse",
]
