from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.services.blog import category_service
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[CategoryOut])
async def list_all(db: AsyncSession = Depends(get_db)):
    return await category_service.list_categories(db)

@router.post("/", response_model=CategoryOut)
async def create(category_in: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await category_service.create_category(db, category_in)

@router.get("/{category_id}", response_model=CategoryOut)
async def get(category_id: int, db: AsyncSession = Depends(get_db)):
    return await category_service.get_category(db, category_id)

@router.put("/{category_id}", response_model=CategoryOut)
async def update(category_id: int, category_in: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    return await category_service.update_category(db, category_id, category_in)

@router.delete("/{category_id}")
async def delete(category_id: int, db: AsyncSession = Depends(get_db)):
    return await category_service.delete_category(db, category_id)
