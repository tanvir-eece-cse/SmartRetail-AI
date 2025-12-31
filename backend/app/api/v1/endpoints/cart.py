"""Shopping cart endpoints."""

from typing import List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models import CartItem, Product, User
from app.schemas import CartItemCreate, CartItemResponse, CartItemUpdate, CartResponse

router = APIRouter()


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's cart."""
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == current_user.id)
        .options(selectinload(CartItem.user))
    )
    cart_items = result.scalars().all()
    
    # Fetch products for cart items
    items_with_products = []
    subtotal = Decimal("0")
    
    for item in cart_items:
        product_result = await db.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = product_result.scalar_one_or_none()
        
        if product and product.is_active:
            item_total = product.price * item.quantity
            subtotal += item_total
            
            items_with_products.append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "variant_options": item.variant_options,
                "product": {
                    "id": product.id,
                    "uuid": str(product.uuid),
                    "name": product.name,
                    "slug": product.slug,
                    "price": product.price,
                    "compare_at_price": product.compare_at_price,
                    "images": product.images,
                    "average_rating": product.average_rating,
                    "review_count": product.review_count,
                    "is_featured": product.is_featured,
                    "stock_quantity": product.stock_quantity
                }
            })
    
    return {
        "items": items_with_products,
        "subtotal": subtotal,
        "item_count": len(items_with_products)
    }


@router.post("/items", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add item to cart."""
    # Check if product exists
    product_result = await db.execute(
        select(Product).where(Product.id == item_data.product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check stock
    if product.track_inventory and product.stock_quantity < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )
    
    # Check if item already in cart
    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == item_data.product_id
        )
    )
    existing_item = result.scalar_one_or_none()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += item_data.quantity
        await db.commit()
        return {"message": "Cart updated", "cart_item_id": existing_item.id}
    
    # Create new cart item
    cart_item = CartItem(
        user_id=current_user.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
        variant_options=item_data.variant_options
    )
    
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    
    return {"message": "Item added to cart", "cart_item_id": cart_item.id}


@router.put("/items/{item_id}", response_model=dict)
async def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update cart item quantity."""
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.user_id == current_user.id
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Check stock
    product_result = await db.execute(
        select(Product).where(Product.id == cart_item.product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if product and product.track_inventory and product.stock_quantity < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock"
        )
    
    cart_item.quantity = item_data.quantity
    await db.commit()
    
    return {"message": "Cart item updated"}


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove item from cart."""
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.user_id == current_user.id
        )
    )
    cart_item = result.scalar_one_or_none()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    await db.delete(cart_item)
    await db.commit()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all items from cart."""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == current_user.id)
    )
    cart_items = result.scalars().all()
    
    for item in cart_items:
        await db.delete(item)
    
    await db.commit()
