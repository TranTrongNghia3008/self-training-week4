from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.services.blog import category_service
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[CategoryOut])
def list_all(db: Session = Depends(get_db)):
    return category_service.list_categories(db)

@router.post("/", response_model=CategoryOut)
def create(category_in: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, category_in)

@router.get("/{category_id}", response_model=CategoryOut)
def get(category_id: int, db: Session = Depends(get_db)):
    return category_service.get_category(db, category_id)

@router.put("/{category_id}", response_model=CategoryOut)
def update(category_id: int, category_in: CategoryUpdate, db: Session = Depends(get_db)):
    return category_service.update_category(db, category_id, category_in)

@router.delete("/{category_id}")
def delete(category_id: int, db: Session = Depends(get_db)):
    return category_service.delete_category(db, category_id)
