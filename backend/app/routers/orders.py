from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_admin
from app.models.user import User
from app.schemas.order import OrderResponse, OrderStatusUpdate
from app.services.order_service import (
    create_order,
    get_all_orders,
    get_order_by_id,
    get_user_orders,
    update_order_status,
)

router = APIRouter(tags=["Orders"])


@router.post(
    "/api/orders",
    response_model=OrderResponse,
    status_code=201,
    summary="Create order",
    description="Create an order from the current cart. Reduces product stock and clears the cart.",
)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_order(db, current_user.id)


@router.get(
    "/api/orders",
    response_model=list[OrderResponse],
    summary="My orders",
    description="Returns order history for the current user.",
)
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_orders(db, current_user.id)


@router.get(
    "/api/orders/{order_id}",
    response_model=OrderResponse,
    summary="Order details",
    description="Returns details of a specific order belonging to the current user.",
)
def order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_order_by_id(db, order_id, current_user.id)


@router.get(
    "/api/admin/orders",
    response_model=list[OrderResponse],
    summary="All orders (admin)",
    description="Returns all orders in the system. Requires admin role.",
)
def admin_all_orders(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return get_all_orders(db)


@router.put(
    "/api/admin/orders/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status (admin)",
    description="Update order status. Valid transitions: pending→confirmed→shipped→delivered, or →cancelled.",
)
def admin_update_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return update_order_status(db, order_id, data.status)
