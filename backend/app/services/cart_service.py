from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemAdd, CartItemUpdate


def get_cart(db: Session, user_id: int) -> dict:
    items = (
        db.execute(
            select(CartItem)
            .options(joinedload(CartItem.product))
            .where(CartItem.user_id == user_id)
        )
        .scalars()
        .all()
    )
    total = sum(float(item.product.price) * item.quantity for item in items)
    return {"items": items, "total": round(total, 2)}


def add_to_cart(db: Session, user_id: int, data: CartItemAdd) -> CartItem:
    product = db.get(Product, data.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.stock < data.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")

    existing = db.execute(
        select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == data.product_id,
        )
    ).scalar_one_or_none()

    if existing:
        existing.quantity += data.quantity
        if existing.quantity > product.stock:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")
        db.commit()
        db.refresh(existing)
        return existing

    item = CartItem(user_id=user_id, product_id=data.product_id, quantity=data.quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_cart_item(db: Session, user_id: int, item_id: int, data: CartItemUpdate) -> CartItem:
    item = db.execute(
        select(CartItem)
        .options(joinedload(CartItem.product))
        .where(CartItem.id == item_id, CartItem.user_id == user_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    if data.quantity > item.product.stock:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")

    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item


def delete_cart_item(db: Session, user_id: int, item_id: int) -> None:
    item = db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user_id)
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    db.delete(item)
    db.commit()


def clear_cart(db: Session, user_id: int) -> None:
    items = db.execute(
        select(CartItem).where(CartItem.user_id == user_id)
    ).scalars().all()
    for item in items:
        db.delete(item)
    db.commit()
