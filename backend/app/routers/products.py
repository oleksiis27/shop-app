from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.product import (
    PaginatedProducts,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import (
    create_product,
    delete_product,
    get_product_by_id,
    get_products,
    update_product,
)

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get(
    "",
    response_model=PaginatedProducts,
    summary="List products",
    description="Get paginated list of products with optional filters: category, search, price range, sorting.",
)
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: int | None = Query(None, description="Filter by category ID"),
    search: str | None = Query(None, description="Search in name and description"),
    sort_by: str = Query("created_at", description="Sort: created_at, price_asc, price_desc, name"),
    min_price: float | None = Query(None, ge=0, description="Minimum price"),
    max_price: float | None = Query(None, ge=0, description="Maximum price"),
    db: Session = Depends(get_db),
):
    return get_products(db, page, limit, category, search, sort_by, min_price, max_price)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Returns a single product with its category.",
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_by_id(db, product_id)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
    summary="Create product (admin)",
    description="Create a new product. Requires admin role.",
)
def create(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return create_product(db, data)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product (admin)",
    description="Update an existing product. Requires admin role.",
)
def update(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return update_product(db, product_id, data)


@router.delete(
    "/{product_id}",
    status_code=204,
    summary="Delete product (admin)",
    description="Delete a product. Requires admin role.",
)
def delete(
    product_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    delete_product(db, product_id)
