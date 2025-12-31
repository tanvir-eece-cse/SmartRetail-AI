"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# Generic type for pagination
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


# ============== User Schemas ==============

class UserBase(BaseModel):
    """Base user schema."""
    
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")


class UserCreate(UserBase):
    """User registration schema."""
    
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """User update schema."""
    
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime


class UserProfile(UserResponse):
    """Extended user profile schema."""
    
    last_login: Optional[datetime]
    order_count: int = 0
    review_count: int = 0


# ============== Auth Schemas ==============

class Token(BaseModel):
    """Token response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Token payload schema."""
    
    sub: str
    exp: datetime
    type: str


class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    
    refresh_token: str


# ============== Product Schemas ==============

class ProductBase(BaseModel):
    """Base product schema."""
    
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    attributes: Optional[dict] = None


class ProductCreate(ProductBase):
    """Product creation schema."""
    
    sku: str = Field(..., min_length=3, max_length=50)
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    cost_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class ProductUpdate(BaseModel):
    """Product update schema."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    images: Optional[List[str]] = None
    attributes: Optional[dict] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProductResponse(ProductBase):
    """Product response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    sku: str
    slug: str
    stock_quantity: int
    is_active: bool
    is_featured: bool
    view_count: int
    sold_count: int
    average_rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Product list item schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: str
    name: str
    slug: str
    price: Decimal
    compare_at_price: Optional[Decimal]
    images: Optional[List[str]]
    average_rating: float
    review_count: int
    is_featured: bool
    stock_quantity: int


# ============== Category Schemas ==============

class CategoryBase(BaseModel):
    """Base category schema."""
    
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Category creation schema."""
    pass


class CategoryUpdate(BaseModel):
    """Category update schema."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    """Category response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    is_active: bool
    display_order: int
    product_count: int = 0


class CategoryTree(CategoryResponse):
    """Category with children."""
    
    children: List["CategoryTree"] = []


# ============== Order Schemas ==============

class OrderItemCreate(BaseModel):
    """Order item creation schema."""
    
    product_id: int
    quantity: int = Field(..., gt=0)
    variant_options: Optional[dict] = None


class OrderCreate(BaseModel):
    """Order creation schema."""
    
    items: List[OrderItemCreate]
    shipping_address_id: int
    payment_method: str
    customer_notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Order item response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: Optional[int]
    product_name: str
    product_sku: str
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    variant_options: Optional[dict]


class OrderResponse(BaseModel):
    """Order response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_number: str
    status: str
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    shipping_address: dict
    shipping_method: Optional[str]
    tracking_number: Optional[str]
    payment_method: Optional[str]
    payment_status: str
    customer_notes: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]


class OrderStatusUpdate(BaseModel):
    """Order status update schema."""
    
    status: str
    tracking_number: Optional[str] = None
    admin_notes: Optional[str] = None


# ============== Review Schemas ==============

class ReviewCreate(BaseModel):
    """Review creation schema."""
    
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    """Review response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    product_id: int
    rating: int
    title: Optional[str]
    content: Optional[str]
    sentiment_score: Optional[float]
    is_verified_purchase: bool
    created_at: datetime
    user: Optional[UserResponse] = None


# ============== Cart Schemas ==============

class CartItemCreate(BaseModel):
    """Cart item creation schema."""
    
    product_id: int
    quantity: int = Field(default=1, gt=0)
    variant_options: Optional[dict] = None


class CartItemUpdate(BaseModel):
    """Cart item update schema."""
    
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    """Cart item response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    product_id: int
    quantity: int
    variant_options: Optional[dict]
    product: ProductListResponse


class CartResponse(BaseModel):
    """Cart response schema."""
    
    items: List[CartItemResponse]
    subtotal: Decimal
    item_count: int


# ============== Recommendation Schemas ==============

class RecommendationRequest(BaseModel):
    """Recommendation request schema."""
    
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    limit: int = Field(default=10, ge=1, le=50)
    include_reasons: bool = False


class RecommendedProduct(ProductListResponse):
    """Recommended product with score."""
    
    recommendation_score: float
    recommendation_reason: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Recommendation response schema."""
    
    recommendations: List[RecommendedProduct]
    model_version: str
    generated_at: datetime


# ============== Analytics Schemas ==============

class SalesAnalytics(BaseModel):
    """Sales analytics schema."""
    
    total_revenue: Decimal
    total_orders: int
    average_order_value: Decimal
    revenue_change_percent: float
    orders_change_percent: float
    revenue_by_day: List[dict]
    top_products: List[dict]
    top_categories: List[dict]


class CustomerAnalytics(BaseModel):
    """Customer analytics schema."""
    
    total_customers: int
    new_customers: int
    returning_customers: int
    customer_segments: List[dict]
    acquisition_by_source: List[dict]
    customer_lifetime_value: Decimal


class ProductAnalytics(BaseModel):
    """Product analytics schema."""
    
    product_id: int
    product_name: str
    views: int
    add_to_cart_count: int
    purchases: int
    conversion_rate: float
    revenue: Decimal
    average_rating: float
    stock_status: str
