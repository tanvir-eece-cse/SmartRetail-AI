"""ML-powered recommendation endpoints."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models import Product, User, UserActivity
from app.schemas import RecommendationResponse, RecommendedProduct

router = APIRouter()


@router.get("/user/{user_id}", response_model=RecommendationResponse)
async def get_user_recommendations(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    include_reasons: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized product recommendations for a user."""
    # Verify user has permission
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view recommendations for this user"
        )
    
    try:
        # Call ML service for recommendations
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/api/v1/recommendations/user",
                json={
                    "user_id": user_id,
                    "limit": limit,
                    "include_reasons": include_reasons
                },
                timeout=settings.ML_SERVICE_TIMEOUT
            )
            
            if response.status_code == 200:
                ml_recommendations = response.json()
                
                # Fetch product details
                product_ids = [r["product_id"] for r in ml_recommendations["recommendations"]]
                products_result = await db.execute(
                    select(Product).where(
                        Product.id.in_(product_ids),
                        Product.is_active == True
                    )
                )
                products = {p.id: p for p in products_result.scalars().all()}
                
                recommendations = []
                for rec in ml_recommendations["recommendations"]:
                    product = products.get(rec["product_id"])
                    if product:
                        recommendations.append(RecommendedProduct(
                            id=product.id,
                            uuid=str(product.uuid),
                            name=product.name,
                            slug=product.slug,
                            price=product.price,
                            compare_at_price=product.compare_at_price,
                            images=product.images,
                            average_rating=product.average_rating,
                            review_count=product.review_count,
                            is_featured=product.is_featured,
                            stock_quantity=product.stock_quantity,
                            recommendation_score=rec["score"],
                            recommendation_reason=rec.get("reason")
                        ))
                
                return RecommendationResponse(
                    recommendations=recommendations,
                    model_version=ml_recommendations.get("model_version", "1.0.0"),
                    generated_at=datetime.now(timezone.utc)
                )
    except httpx.RequestError:
        pass  # Fall back to simple recommendations
    
    # Fallback: Return popular products
    products_result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .order_by(Product.sold_count.desc())
        .limit(limit)
    )
    products = products_result.scalars().all()
    
    recommendations = [
        RecommendedProduct(
            id=p.id,
            uuid=str(p.uuid),
            name=p.name,
            slug=p.slug,
            price=p.price,
            compare_at_price=p.compare_at_price,
            images=p.images,
            average_rating=p.average_rating,
            review_count=p.review_count,
            is_featured=p.is_featured,
            stock_quantity=p.stock_quantity,
            recommendation_score=0.5,
            recommendation_reason="Popular product"
        )
        for p in products
    ]
    
    return RecommendationResponse(
        recommendations=recommendations,
        model_version="fallback",
        generated_at=datetime.now(timezone.utc)
    )


@router.get("/product/{product_id}", response_model=RecommendationResponse)
async def get_similar_products(
    product_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get similar products based on a product."""
    # Check if product exists
    product_result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        # Call ML service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/api/v1/recommendations/similar",
                json={
                    "product_id": product_id,
                    "limit": limit
                },
                timeout=settings.ML_SERVICE_TIMEOUT
            )
            
            if response.status_code == 200:
                ml_recommendations = response.json()
                
                product_ids = [r["product_id"] for r in ml_recommendations["recommendations"]]
                products_result = await db.execute(
                    select(Product).where(
                        Product.id.in_(product_ids),
                        Product.is_active == True
                    )
                )
                products = {p.id: p for p in products_result.scalars().all()}
                
                recommendations = []
                for rec in ml_recommendations["recommendations"]:
                    p = products.get(rec["product_id"])
                    if p:
                        recommendations.append(RecommendedProduct(
                            id=p.id,
                            uuid=str(p.uuid),
                            name=p.name,
                            slug=p.slug,
                            price=p.price,
                            compare_at_price=p.compare_at_price,
                            images=p.images,
                            average_rating=p.average_rating,
                            review_count=p.review_count,
                            is_featured=p.is_featured,
                            stock_quantity=p.stock_quantity,
                            recommendation_score=rec["score"],
                            recommendation_reason=rec.get("reason")
                        ))
                
                return RecommendationResponse(
                    recommendations=recommendations,
                    model_version=ml_recommendations.get("model_version", "1.0.0"),
                    generated_at=datetime.now(timezone.utc)
                )
    except httpx.RequestError:
        pass
    
    # Fallback: Products from same category
    products_result = await db.execute(
        select(Product)
        .where(
            Product.is_active == True,
            Product.category_id == product.category_id,
            Product.id != product_id
        )
        .order_by(Product.average_rating.desc())
        .limit(limit)
    )
    products = products_result.scalars().all()
    
    recommendations = [
        RecommendedProduct(
            id=p.id,
            uuid=str(p.uuid),
            name=p.name,
            slug=p.slug,
            price=p.price,
            compare_at_price=p.compare_at_price,
            images=p.images,
            average_rating=p.average_rating,
            review_count=p.review_count,
            is_featured=p.is_featured,
            stock_quantity=p.stock_quantity,
            recommendation_score=0.5,
            recommendation_reason="Same category"
        )
        for p in products
    ]
    
    return RecommendationResponse(
        recommendations=recommendations,
        model_version="fallback",
        generated_at=datetime.now(timezone.utc)
    )


@router.get("/trending", response_model=RecommendationResponse)
async def get_trending_products(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get trending products."""
    products_result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .order_by(
            (Product.sold_count * 2 + Product.view_count).desc()
        )
        .limit(limit)
    )
    products = products_result.scalars().all()
    
    recommendations = [
        RecommendedProduct(
            id=p.id,
            uuid=str(p.uuid),
            name=p.name,
            slug=p.slug,
            price=p.price,
            compare_at_price=p.compare_at_price,
            images=p.images,
            average_rating=p.average_rating,
            review_count=p.review_count,
            is_featured=p.is_featured,
            stock_quantity=p.stock_quantity,
            recommendation_score=(p.sold_count * 2 + p.view_count) / 1000,
            recommendation_reason="Trending now"
        )
        for p in products
    ]
    
    return RecommendationResponse(
        recommendations=recommendations,
        model_version="trending-v1",
        generated_at=datetime.now(timezone.utc)
    )


@router.post("/track")
async def track_activity(
    activity_type: str,
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    search_query: Optional[str] = None,
    session_id: str = "",
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Track user activity for improving recommendations."""
    activity = UserActivity(
        user_id=current_user.id if current_user else None,
        session_id=session_id,
        activity_type=activity_type,
        product_id=product_id,
        category_id=category_id,
        search_query=search_query
    )
    
    db.add(activity)
    await db.commit()
    
    return {"message": "Activity tracked"}
