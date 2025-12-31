"""Review management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models import Order, OrderItem, Product, Review, User, UserRole
from app.schemas import PaginatedResponse, ReviewCreate, ReviewResponse

router = APIRouter()


@router.get("/product/{product_id}", response_model=PaginatedResponse[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a product."""
    query = (
        select(Review)
        .where(Review.product_id == product_id, Review.is_approved == True)
        .options(selectinload(Review.user))
    )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Review.created_at.desc())
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return PaginatedResponse(
        items=reviews,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a product review."""
    # Check if product exists
    product_result = await db.execute(
        select(Product).where(Product.id == review_data.product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed this product
    existing_review = await db.execute(
        select(Review).where(
            Review.user_id == current_user.id,
            Review.product_id == review_data.product_id
        )
    )
    if existing_review.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    # Check if verified purchase
    order_item_result = await db.execute(
        select(OrderItem)
        .join(Order)
        .where(
            Order.user_id == current_user.id,
            OrderItem.product_id == review_data.product_id
        )
    )
    is_verified_purchase = order_item_result.scalar_one_or_none() is not None
    
    # Create review
    review = Review(
        user_id=current_user.id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        is_verified_purchase=is_verified_purchase
    )
    
    db.add(review)
    
    # Update product rating
    rating_result = await db.execute(
        select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("count")
        ).where(
            Review.product_id == review_data.product_id,
            Review.is_approved == True
        )
    )
    rating_data = rating_result.one()
    
    # Include new review in calculation
    total_reviews = (rating_data.count or 0) + 1
    current_sum = (rating_data.avg_rating or 0) * (rating_data.count or 0)
    new_avg = (current_sum + review_data.rating) / total_reviews
    
    product.average_rating = round(new_avg, 2)
    product.review_count = total_reviews
    
    await db.commit()
    await db.refresh(review)
    
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a review (owner or admin only)."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    product_id = review.product_id
    await db.delete(review)
    
    # Recalculate product rating
    product_result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if product:
        rating_result = await db.execute(
            select(
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("count")
            ).where(
                Review.product_id == product_id,
                Review.is_approved == True,
                Review.id != review_id
            )
        )
        rating_data = rating_result.one()
        
        product.average_rating = round(rating_data.avg_rating or 0, 2)
        product.review_count = rating_data.count or 0
    
    await db.commit()
