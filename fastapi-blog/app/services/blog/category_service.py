from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status

def create_category(db: Session, category_in: CategoryCreate):
    existing = db.query(Category).filter(Category.name == category_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = Category(**category_in.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def get_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

def update_category(db: Session, category_id: int, category_in: CategoryUpdate):
    category = get_category(db, category_id)
    for field, value in category_in.dict().items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}

def list_categories(db: Session):
    return db.query(Category).all()
