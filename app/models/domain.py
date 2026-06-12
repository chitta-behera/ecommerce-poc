from __future__ import annotations
from typing import TYPE_CHECKING, List
import datetime as dt
from dataclasses import dataclass, field

from .enums import OrderStatus

if TYPE_CHECKING:
    from .product import Product
    from .customer import Customer
    from .order import OrderItem


@dataclass
class Category:
    id: int
    name: str
    description: str | None
    products: List[Product] = field(default_factory=list, repr=False)


@dataclass
class Product:
    id: int
    name: str
    price: float
    sku: str
    category_id: int
    description: str | None = None
    category: Category | None = field(default=None, repr=False)


@dataclass
class Customer:
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    orders: List[Order] = field(default_factory=list, repr=False)


@dataclass
class Order:
    id: int
    customer_id: int
    order_date: dt.datetime
    status: OrderStatus
    customer: Customer | None = field(default=None, repr=False)
    items: List[OrderItem] = field(default_factory=list)


@dataclass
class OrderItem:
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    order: Order | None = field(default=None, repr=False)
    product: Product | None = field(default=None, repr=False)
