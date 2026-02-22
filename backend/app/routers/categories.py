from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.category import Category
from app.schemas.product import CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="List categories",
    description="Returns all product categories.",
)
def list_categories(db: Session = Depends(get_db)):
    categories = db.execute(select(Category).order_by(Category.name)).scalars().all()
    return categories
