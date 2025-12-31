"""Order management endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models import (
    Address,
    CartItem,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    User,
    UserRole,
)
from app.schemas import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    PaginatedResponse,
)

router = APIRouter()


def generate_order_number() -> str:
    """Generate unique order number."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"


@router.get("", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: OrderStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List orders for current user or all orders (admin)."""
    query = select(Order).options(selectinload(Order.items))
    
    # Filter by user if not admin
    if current_user.role != UserRole.ADMIN:
        query = query.where(Order.user_id == current_user.id)
    
    if status:
        query = query.where(Order.status == status)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Order.created_at.desc())
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return PaginatedResponse(
        items=orders,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID."""
    query = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    
    # Filter by user if not admin
    if current_user.role != UserRole.ADMIN:
        query = query.where(Order.user_id == current_user.id)
    
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new order from cart or direct items."""
    # Get shipping address
    address_result = await db.execute(
        select(Address).where(
            Address.id == order_data.shipping_address_id,
            Address.user_id == current_user.id
        )
    )
    address = address_result.scalar_one_or_none()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipping address not found"
        )
    
    # Process order items
    order_items = []
    subtotal = Decimal("0")
    
    for item_data in order_data.items:
        product_result = await db.execute(
            select(Product).where(Product.id == item_data.product_id)
        )
        product = product_result.scalar_one_or_none()
        
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_data.product_id} not found or unavailable"
            )
        
        # Check stock
        if product.track_inventory and product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}"
            )
        
        item_total = product.price * item_data.quantity
        subtotal += item_total
        
        order_items.append({
            "product": product,
            "quantity": item_data.quantity,
            "unit_price": product.price,
            "total_price": item_total,
            "variant_options": item_data.variant_options
        })
    
    # Calculate totals
    tax_amount = subtotal * Decimal("0.05")  # 5% tax
    shipping_amount = Decimal("50.00") if subtotal < Decimal("1000") else Decimal("0")
    total_amount = subtotal + tax_amount + shipping_amount
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id,
        status=OrderStatus.PENDING,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        discount_amount=Decimal("0"),
        total_amount=total_amount,
        shipping_address={
            "full_name": address.full_name,
            "phone": address.phone,
            "street_address": address.street_address,
            "city": address.city,
            "district": address.district,
            "postal_code": address.postal_code
        },
        payment_method=order_data.payment_method,
        customer_notes=order_data.customer_notes
    )
    
    db.add(order)
    await db.flush()  # Get order ID
    
    # Create order items
    for item_info in order_items:
        product = item_info["product"]
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            product_image=product.images[0] if product.images else None,
            unit_price=item_info["unit_price"],
            quantity=item_info["quantity"],
            total_price=item_info["total_price"],
            variant_options=item_info["variant_options"]
        )
        db.add(order_item)
        
        # Update product stock and sold count
        if product.track_inventory:
            product.stock_quantity -= item_info["quantity"]
        product.sold_count += item_info["quantity"]
    
    # Clear user's cart
    cart_result = await db.execute(
        select(CartItem).where(CartItem.user_id == current_user.id)
    )
    cart_items = cart_result.scalars().all()
    for cart_item in cart_items:
        await db.delete(cart_item)
    
    await db.commit()
    await db.refresh(order)
    
    # Reload with items
    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one()
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update order status (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update order status"
        )
    
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update status
    order.status = OrderStatus(status_data.status)
    
    if status_data.tracking_number:
        order.tracking_number = status_data.tracking_number
    
    if status_data.admin_notes:
        order.admin_notes = status_data.admin_notes
    
    # Set timestamps based on status
    if order.status == OrderStatus.SHIPPED:
        order.shipped_at = datetime.now(timezone.utc)
    elif order.status == OrderStatus.DELIVERED:
        order.delivered_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(order)
    
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an order (only pending orders)."""
    query = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )
    
    if current_user.role != UserRole.ADMIN:
        query = query.where(Order.user_id == current_user.id)
    
    result = await db.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order in current status"
        )
    
    # Restore stock
    for item in order.items:
        if item.product_id:
            product_result = await db.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = product_result.scalar_one_or_none()
            if product and product.track_inventory:
                product.stock_quantity += item.quantity
                product.sold_count -= item.quantity
    
    order.status = OrderStatus.CANCELLED
    await db.commit()
    await db.refresh(order)
    
    return order
