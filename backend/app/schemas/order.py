from datetime import datetime

from pydantic import BaseModel


class OrderItemProduct(BaseModel):
    id: int
    name: str
    image_url: str

    model_config = {"from_attributes": True}


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: OrderItemProduct

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total: float
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str
