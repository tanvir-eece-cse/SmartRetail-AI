"""Category management endpoints."""

from typing import List
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.core.database import get_db
from app.models import Category, Product, User, UserRole
from app.schemas import CategoryCreate, CategoryResponse, CategoryTree, CategoryUpdate

router = APIRouter()


def slugify(text: str) -> str:
    """Generate URL-friendly slug from text."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """List all categories."""
    query = select(Category)
    
    if not include_inactive:
        query = query.where(Category.is_active == True)
    
    query = query.order_by(Category.display_order, Category.name)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    # Get product counts
    response = []
    for category in categories:
        count_result = await db.execute(
            select(func.count(Product.id))
            .where(Product.category_id == category.id, Product.is_active == True)
        )
        product_count = count_result.scalar() or 0
        
        response.append(CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            image_url=category.image_url,
            parent_id=category.parent_id,
            is_active=category.is_active,
            display_order=category.display_order,
            product_count=product_count
        ))
    
    return response


@router.get("/tree", response_model=List[CategoryTree])
async def get_category_tree(db: AsyncSession = Depends(get_db)):
    """Get categories as a nested tree structure."""
    query = (
        select(Category)
        .where(Category.is_active == True, Category.parent_id == None)
        .order_by(Category.display_order, Category.name)
    )
    
    result = await db.execute(query)
    root_categories = result.scalars().all()
    
    async def build_tree(category: Category) -> CategoryTree:
        children_result = await db.execute(
            select(Category)
            .where(Category.parent_id == category.id, Category.is_active == True)
            .order_by(Category.display_order, Category.name)
        )
        children = children_result.scalars().all()
        
        child_trees = [await build_tree(child) for child in children]
        
        return CategoryTree(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            image_url=category.image_url,
            parent_id=category.parent_id,
            is_active=category.is_active,
            display_order=category.display_order,
            product_count=0,
            children=child_trees
        )
    
    return [await build_tree(cat) for cat in root_categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get category by ID."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Get product count
    count_result = await db.execute(
        select(func.count(Product.id))
        .where(Product.category_id == category.id, Product.is_active == True)
    )
    product_count = count_result.scalar() or 0
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        image_url=category.image_url,
        parent_id=category.parent_id,
        is_active=category.is_active,
        display_order=category.display_order,
        product_count=product_count
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new category (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create categories"
        )
    
    # Generate slug
    slug = slugify(category_data.name)
    
    # Ensure unique slug
    result = await db.execute(select(Category).where(Category.slug == slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    category = Category(
        **category_data.model_dump(),
        slug=slug
    )
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        image_url=category.image_url,
        parent_id=category.parent_id,
        is_active=category.is_active,
        display_order=category.display_order,
        product_count=0
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a category (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update categories"
        )
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    update_data = category_data.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        update_data["slug"] = slugify(update_data["name"])
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        image_url=category.image_url,
        parent_id=category.parent_id,
        is_active=category.is_active,
        display_order=category.display_order,
        product_count=0
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a category (admin only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete categories"
        )
    
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category.is_active = False
    await db.commit()
