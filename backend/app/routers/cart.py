from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemResponse, CartItemUpdate, CartResponse
from app.services.cart_service import (
    add_to_cart,
    clear_cart,
    delete_cart_item,
    get_cart,
    update_cart_item,
)

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get(
    "",
    response_model=CartResponse,
    summary="Get cart",
    description="Returns the current user's shopping cart with all items and total price.",
)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_cart(db, current_user.id)


@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=201,
    summary="Add item to cart",
    description="Add a product to the cart. If already in cart, quantity is increased.",
)
def add_item(
    data: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_to_cart(db, current_user.id, data)


@router.put(
    "/items/{item_id}",
    response_model=CartItemResponse,
    summary="Update cart item quantity",
    description="Update the quantity of a specific item in the cart.",
)
def update_item(
    item_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_cart_item(db, current_user.id, item_id, data)


@router.delete(
    "/items/{item_id}",
    status_code=204,
    summary="Remove item from cart",
    description="Remove a specific item from the cart.",
)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_cart_item(db, current_user.id, item_id)


@router.delete(
    "",
    status_code=204,
    summary="Clear cart",
    description="Remove all items from the cart.",
)
def clear(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clear_cart(db, current_user.id)
