from __future__ import annotations
import datetime as dt
from pydantic import BaseModel, ConfigDict, Field

from .product import Product
from app.models.enums import OrderStatus


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, example=1)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(OrderItemBase):
    product_id: int | None = None
    quantity: int | None = Field(default=None, gt=0)


class OrderItem(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    price: float = Field(description="The price of the product at the time of order.")
    product: Product


class OrderBase(BaseModel):
    customer_id: int


class OrderCreate(OrderBase):
    status: OrderStatus = Field(
        default=OrderStatus.PENDING,
        example=OrderStatus.PENDING,
        description="The initial status of the order.",
    )
    items: list[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: OrderStatus | None = Field(
        default=None, example=OrderStatus.SHIPPED, description="The new status of the order."
    )


class Order(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_date: dt.datetime
    status: OrderStatus
    items: list[OrderItem] = []
