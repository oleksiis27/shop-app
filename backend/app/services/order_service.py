from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product


VALID_TRANSITIONS = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["shipped", "cancelled"],
    "shipped": ["delivered"],
    "delivered": [],
    "cancelled": [],
}


def create_order(db: Session, user_id: int) -> Order:
    cart_items = (
        db.execute(
            select(CartItem)
            .options(joinedload(CartItem.product))
            .where(CartItem.user_id == user_id)
        )
        .scalars()
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    # Validate stock
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {item.product.name}",
            )

    # Calculate total and create order
    total = sum(float(item.product.price) * item.quantity for item in cart_items)
    order = Order(user_id=user_id, total=round(total, 2))
    db.add(order)
    db.flush()

    # Create order items and reduce stock
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=float(item.product.price),
        )
        db.add(order_item)
        item.product.stock -= item.quantity

    # Clear cart
    for item in cart_items:
        db.delete(item)

    db.commit()
    return get_order_by_id(db, order.id, user_id)


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    orders = (
        db.execute(
            select(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        .scalars()
        .unique()
        .all()
    )
    return orders


def get_order_by_id(db: Session, order_id: int, user_id: int | None = None) -> Order:
    query = (
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .where(Order.id == order_id)
    )
    if user_id is not None:
        query = query.where(Order.user_id == user_id)

    order = db.execute(query).unique().scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def get_all_orders(db: Session) -> list[Order]:
    orders = (
        db.execute(
            select(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .order_by(Order.created_at.desc())
        )
        .scalars()
        .unique()
        .all()
    )
    return orders


def update_order_status(db: Session, order_id: int, new_status: str) -> Order:
    order = db.execute(
        select(Order).where(Order.id == order_id)
    ).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    allowed = VALID_TRANSITIONS.get(order.status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from '{order.status}' to '{new_status}'",
        )

    order.status = new_status
    db.commit()
    return get_order_by_id(db, order.id)
