import math

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_products(
    db: Session,
    page: int = 1,
    limit: int = 20,
    category: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    min_price: float | None = None,
    max_price: float | None = None,
) -> dict:
    query = select(Product).options(joinedload(Product.category))
    count_query = select(func.count(Product.id))

    if category:
        query = query.where(Product.category_id == category)
        count_query = count_query.where(Product.category_id == category)

    if search:
        pattern = f"%{search}%"
        query = query.where(Product.name.ilike(pattern) | Product.description.ilike(pattern))
        count_query = count_query.where(Product.name.ilike(pattern) | Product.description.ilike(pattern))

    if min_price is not None:
        query = query.where(Product.price >= min_price)
        count_query = count_query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)
        count_query = count_query.where(Product.price <= max_price)

    allowed_sort = {
        "created_at": Product.created_at.desc(),
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "name": Product.name.asc(),
    }
    query = query.order_by(allowed_sort.get(sort_by, Product.created_at.desc()))

    total = db.execute(count_query).scalar()
    offset = (page - 1) * limit
    items = db.execute(query.offset(offset).limit(limit)).scalars().unique().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if limit > 0 else 0,
    }


def get_product_by_id(db: Session, product_id: int) -> Product:
    product = db.execute(
        select(Product).options(joinedload(Product.category)).where(Product.id == product_id)
    ).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def create_product(db: Session, data: ProductCreate) -> Product:
    category = db.get(Category, data.category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return get_product_by_id(db, product.id)


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if data.category_id is not None:
        category = db.get(Category, data.category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    return get_product_by_id(db, product.id)


def delete_product(db: Session, product_id: int) -> None:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(product)
    db.commit()
