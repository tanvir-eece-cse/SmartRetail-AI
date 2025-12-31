"""Analytics endpoints."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models import Order, OrderItem, OrderStatus, Product, User, UserRole
from app.schemas import CustomerAnalytics, ProductAnalytics, SalesAnalytics

router = APIRouter()


@router.get("/sales", response_model=SalesAnalytics)
async def get_sales_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get sales analytics (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view analytics"
        )
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    prev_start_date = start_date - timedelta(days=days)
    
    # Current period totals
    current_result = await db.execute(
        select(
            func.sum(Order.total_amount).label("revenue"),
            func.count(Order.id).label("orders")
        ).where(
            Order.created_at >= start_date,
            Order.status.not_in([OrderStatus.CANCELLED, OrderStatus.REFUNDED])
        )
    )
    current_data = current_result.one()
    
    # Previous period totals for comparison
    prev_result = await db.execute(
        select(
            func.sum(Order.total_amount).label("revenue"),
            func.count(Order.id).label("orders")
        ).where(
            and_(
                Order.created_at >= prev_start_date,
                Order.created_at < start_date
            ),
            Order.status.not_in([OrderStatus.CANCELLED, OrderStatus.REFUNDED])
        )
    )
    prev_data = prev_result.one()
    
    total_revenue = current_data.revenue or Decimal("0")
    total_orders = current_data.orders or 0
    prev_revenue = prev_data.revenue or Decimal("0")
    prev_orders = prev_data.orders or 0
    
    # Calculate changes
    revenue_change = (
        ((float(total_revenue) - float(prev_revenue)) / float(prev_revenue) * 100)
        if prev_revenue > 0 else 0
    )
    orders_change = (
        ((total_orders - prev_orders) / prev_orders * 100)
        if prev_orders > 0 else 0
    )
    
    # Revenue by day
    daily_result = await db.execute(
        select(
            func.date_trunc('day', Order.created_at).label("date"),
            func.sum(Order.total_amount).label("revenue"),
            func.count(Order.id).label("orders")
        )
        .where(
            Order.created_at >= start_date,
            Order.status.not_in([OrderStatus.CANCELLED, OrderStatus.REFUNDED])
        )
        .group_by(func.date_trunc('day', Order.created_at))
        .order_by(func.date_trunc('day', Order.created_at))
    )
    
    revenue_by_day = [
        {
            "date": str(row.date.date()),
            "revenue": float(row.revenue),
            "orders": row.orders
        }
        for row in daily_result.all()
    ]
    
    # Top products
    top_products_result = await db.execute(
        select(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("sold"),
            func.sum(OrderItem.total_price).label("revenue")
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            Order.created_at >= start_date,
            Order.status.not_in([OrderStatus.CANCELLED, OrderStatus.REFUNDED])
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.total_price).desc())
        .limit(10)
    )
    
    top_products = [
        {
            "product_id": row.id,
            "name": row.name,
            "sold": row.sold,
            "revenue": float(row.revenue)
        }
        for row in top_products_result.all()
    ]
    
    # Top categories (simplified)
    top_categories = []
    
    return SalesAnalytics(
        total_revenue=total_revenue,
        total_orders=total_orders,
        average_order_value=total_revenue / total_orders if total_orders > 0 else Decimal("0"),
        revenue_change_percent=round(revenue_change, 2),
        orders_change_percent=round(orders_change, 2),
        revenue_by_day=revenue_by_day,
        top_products=top_products,
        top_categories=top_categories
    )


@router.get("/customers", response_model=CustomerAnalytics)
async def get_customer_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get customer analytics (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view analytics"
        )
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Total customers
    total_result = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.CUSTOMER)
    )
    total_customers = total_result.scalar() or 0
    
    # New customers in period
    new_result = await db.execute(
        select(func.count(User.id)).where(
            User.role == UserRole.CUSTOMER,
            User.created_at >= start_date
        )
    )
    new_customers = new_result.scalar() or 0
    
    # Returning customers (more than 1 order)
    returning_result = await db.execute(
        select(func.count(func.distinct(Order.user_id))).where(
            Order.created_at >= start_date
        )
    )
    returning_customers = returning_result.scalar() or 0
    
    # Average lifetime value
    ltv_result = await db.execute(
        select(func.avg(Order.total_amount))
        .where(Order.status.not_in([OrderStatus.CANCELLED, OrderStatus.REFUNDED]))
    )
    avg_ltv = ltv_result.scalar() or Decimal("0")
    
    return CustomerAnalytics(
        total_customers=total_customers,
        new_customers=new_customers,
        returning_customers=returning_customers,
        customer_segments=[
            {"name": "New", "count": new_customers},
            {"name": "Returning", "count": returning_customers},
            {"name": "Inactive", "count": total_customers - returning_customers}
        ],
        acquisition_by_source=[],
        customer_lifetime_value=avg_ltv
    )


@router.get("/products/{product_id}", response_model=ProductAnalytics)
async def get_product_analytics(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific product (admin/vendor only)."""
    if current_user.role not in [UserRole.ADMIN, UserRole.VENDOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view product analytics"
        )
    
    # Get product
    product_result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = product_result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Sales data
    sales_result = await db.execute(
        select(
            func.sum(OrderItem.quantity).label("purchases"),
            func.sum(OrderItem.total_price).label("revenue")
        )
        .join(Order, OrderItem.order_id == Order.id)
        .where(
            OrderItem.product_id == product_id,
            Order.created_at >= start_date,
            Order.status.not_in([OrderStatus.CANCELLED, OrderStatus.REFUNDED])
        )
    )
    sales_data = sales_result.one()
    
    purchases = sales_data.purchases or 0
    revenue = sales_data.revenue or Decimal("0")
    
    # Calculate conversion rate (simplified - views to purchases)
    conversion_rate = (purchases / product.view_count * 100) if product.view_count > 0 else 0
    
    # Stock status
    if product.stock_quantity <= 0:
        stock_status = "out_of_stock"
    elif product.stock_quantity <= product.low_stock_threshold:
        stock_status = "low_stock"
    else:
        stock_status = "in_stock"
    
    return ProductAnalytics(
        product_id=product.id,
        product_name=product.name,
        views=product.view_count,
        add_to_cart_count=0,  # Would need cart tracking
        purchases=purchases,
        conversion_rate=round(conversion_rate, 2),
        revenue=revenue,
        average_rating=product.average_rating,
        stock_status=stock_status
    )


@router.get("/dashboard")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard summary for admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view dashboard"
        )
    
    today = datetime.now(timezone.utc).date()
    
    # Today's orders
    today_orders_result = await db.execute(
        select(
            func.count(Order.id).label("count"),
            func.sum(Order.total_amount).label("revenue")
        ).where(
            func.date(Order.created_at) == today,
            Order.status.not_in([OrderStatus.CANCELLED, OrderStatus.REFUNDED])
        )
    )
    today_orders = today_orders_result.one()
    
    # Pending orders
    pending_result = await db.execute(
        select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
    )
    pending_orders = pending_result.scalar() or 0
    
    # Low stock products
    low_stock_result = await db.execute(
        select(func.count(Product.id)).where(
            Product.is_active == True,
            Product.track_inventory == True,
            Product.stock_quantity <= Product.low_stock_threshold
        )
    )
    low_stock_count = low_stock_result.scalar() or 0
    
    # Total products
    products_result = await db.execute(
        select(func.count(Product.id)).where(Product.is_active == True)
    )
    total_products = products_result.scalar() or 0
    
    # Total customers
    customers_result = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.CUSTOMER)
    )
    total_customers = customers_result.scalar() or 0
    
    return {
        "today_orders": today_orders.count or 0,
        "today_revenue": float(today_orders.revenue or 0),
        "pending_orders": pending_orders,
        "low_stock_products": low_stock_count,
        "total_products": total_products,
        "total_customers": total_customers
    }
