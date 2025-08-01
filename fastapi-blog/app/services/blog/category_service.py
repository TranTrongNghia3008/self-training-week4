from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status


async def create_category(db: AsyncSession, category_in: CategoryCreate):
    result = await db.execute(select(Category).where(Category.name == category_in.name))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = Category(**category_in.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def get_category(db: AsyncSession, category_id: int):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


async def update_category(db: AsyncSession, category_id: int, category_in: CategoryUpdate):
    category = await get_category(db, category_id)
    for field, value in category_in.dict().items():
        setattr(category, field, value)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int):
    category = await get_category(db, category_id)
    await db.delete(category)
    await db.commit()
    return {"message": "Category deleted"}


async def list_categories(db: AsyncSession):
    result = await db.execute(select(Category))
    return result.scalars().all()
