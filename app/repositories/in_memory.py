import threading
import datetime as dt
from typing import Dict, List
from app.models.domain import Category, Product, Customer, Order, OrderItem
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
    CustomerCreate,
    CustomerUpdate,
    OrderCreate,
    OrderUpdate,
)
from .base import IRepository


class InMemoryStorage:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(InMemoryStorage, cls).__new__(cls)
                cls._instance.categories: Dict[int, Category] = {}
                cls._instance.products: Dict[int, Product] = {}
                cls._instance.customers: Dict[int, Customer] = {}
                cls._instance.orders: Dict[int, Order] = {}
                cls._instance.order_items: Dict[int, OrderItem] = {}
                cls._instance._id_counters = {
                    "categories": 0,
                    "products": 0,
                    "customers": 0,
                    "orders": 0,
                    "order_items": 0,
                }
        return cls._instance

    def get_next_id(self, name: str) -> int:
        with self._lock:
            self._id_counters[name] += 1
            return self._id_counters[name]

    def clear(self):
        with self._lock:
            self.categories.clear()
            self.products.clear()
            self.customers.clear()
            self.orders.clear()
            self.order_items.clear()
            self._id_counters = {
                "categories": 0,
                "products": 0,
                "customers": 0,
                "orders": 0,
                "order_items": 0,
            }


storage = InMemoryStorage()


class InMemoryCategoryRepository(IRepository[Category, CategoryCreate, CategoryUpdate]):
    def get_by_id(self, id: int) -> Category | None:
        return storage.categories.get(id)

    def get_all(self) -> List[Category]:
        return list(storage.categories.values())

    def create(self, data: CategoryCreate) -> Category:
        category_id = storage.get_next_id("categories")
        category = Category(
            id=category_id, name=data.name, description=data.description
        )
        storage.categories[category_id] = category
        return category

    def update(self, id: int, data: CategoryUpdate) -> Category | None:
        category = self.get_by_id(id)
        if category:
            if data.name is not None:
                category.name = data.name
            if data.description is not None:
                category.description = data.description
        return category

    def delete(self, id: int) -> bool:
        if id in storage.categories:
            del storage.categories[id]
            return True
        return False


class InMemoryProductRepository(IRepository[Product, ProductCreate, ProductUpdate]):
    def get_by_id(self, id: int) -> Product | None:
        return storage.products.get(id)

    def get_all(self) -> List[Product]:
        return list(storage.products.values())

    def create(self, data: ProductCreate) -> Product:
        product_id = storage.get_next_id("products")
        product = Product(
            id=product_id,
            name=data.name,
            description=data.description,
            price=data.price,
            sku=data.sku,
            category_id=data.category_id,
        )
        storage.products[product_id] = product
        return product

    def update(self, id: int, data: ProductUpdate) -> Product | None:
        product = self.get_by_id(id)
        if product:
            if data.name is not None:
                product.name = data.name
            if data.description is not None:
                product.description = data.description
            if data.price is not None:
                product.price = data.price
            if data.sku is not None:
                product.sku = data.sku
            if data.category_id is not None:
                product.category_id = data.category_id
        return product

    def delete(self, id: int) -> bool:
        if id in storage.products:
            del storage.products[id]
            return True
        return False


class InMemoryCustomerRepository(IRepository[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_id(self, id: int) -> Customer | None:
        return storage.customers.get(id)

    def get_all(self) -> List[Customer]:
        return list(storage.customers.values())

    def create(self, data: CustomerCreate) -> Customer:
        customer_id = storage.get_next_id("customers")
        customer = Customer(
            id=customer_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
        )
        storage.customers[customer_id] = customer
        return customer

    def update(self, id: int, data: CustomerUpdate) -> Customer | None:
        customer = self.get_by_id(id)
        if customer:
            if data.first_name is not None:
                customer.first_name = data.first_name
            if data.last_name is not None:
                customer.last_name = data.last_name
            if data.email is not None:
                customer.email = data.email
            if data.phone is not None:
                customer.phone = data.phone
        return customer

    def delete(self, id: int) -> bool:
        if id in storage.customers:
            del storage.customers[id]
            return True
        return False


class InMemoryOrderRepository(IRepository[Order, OrderCreate, OrderUpdate]):
    def get_by_id(self, id: int) -> Order | None:
        order = storage.orders.get(id)
        if order:
            order.items = [
                item
                for item in storage.order_items.values()
                if item.order_id == order.id
            ]
        return order

    def get_all(self) -> List[Order]:
        orders = list(storage.orders.values())
        for order in orders:
            order.items = [
                item
                for item in storage.order_items.values()
                if item.order_id == order.id
            ]
        return orders

    def create(self, data: OrderCreate) -> Order:
        order_id = storage.get_next_id("orders")
        order = Order(
            id=order_id,
            customer_id=data.customer_id,
            order_date=dt.datetime.now(dt.timezone.utc),
            status=data.status,
        )
        storage.orders[order_id] = order

        created_items = []
        for item_data in data.items:
            item_id = storage.get_next_id("order_items")
            product = storage.products.get(item_data.product_id)
            if not product:
                raise ValueError(f"Product with id {item_data.product_id} not found")
            item = OrderItem(
                id=item_id,
                order_id=order_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price=product.price,
            )
            storage.order_items[item_id] = item
            created_items.append(item)
        order.items = created_items
        return order

    def update(self, id: int, data: OrderUpdate) -> Order | None:
        order = self.get_by_id(id)
        if order:
            if data.status is not None:
                order.status = data.status
        return order

    def delete(self, id: int) -> bool:
        if id in storage.orders:
            del storage.orders[id]
            # Also delete associated order items
            items_to_delete = [
                item_id
                for item_id, item in storage.order_items.items()
                if item.order_id == id
            ]
            for item_id in items_to_delete:
                del storage.order_items[item_id]
            return True
        return False


def init_dummy_data():
    if storage.categories:
        return

    category_repo = InMemoryCategoryRepository()
    product_repo = InMemoryProductRepository()
    customer_repo = InMemoryCustomerRepository()
    order_repo = InMemoryOrderRepository()

    # Categories
    c1 = category_repo.create(
        CategoryCreate(name="Electronics", description="Gadgets and devices")
    )
    c2 = category_repo.create(
        CategoryCreate(name="Books", description="Paperback and hardcovers")
    )

    # Products
    p1 = product_repo.create(
        ProductCreate(
            name="Smartphone",
            description="Latest model",
            price=699.99,
            sku="PHN-123",
            category_id=c1.id,
        )
    )
    p2 = product_repo.create(
        ProductCreate(
            name="Laptop",
            description="Powerful and lightweight",
            price=1299.99,
            sku="LPT-456",
            category_id=c1.id,
        )
    )
    p3 = product_repo.create(
        ProductCreate(
            name="Python Programming",
            description="A comprehensive guide",
            price=49.99,
            sku="BOK-789",
            category_id=c2.id,
        )
    )

    # Customers
    cust1 = customer_repo.create(
        CustomerCreate(
            first_name="John", last_name="Doe", email="john.doe@example.com"
        )
    )
    cust2 = customer_repo.create(
        CustomerCreate(
            first_name="Jane", last_name="Smith", email="jane.smith@example.com"
        )
    )

    # Orders
    order_repo.create(
        OrderCreate(
            customer_id=cust1.id,
            items=[
                {"product_id": p1.id, "quantity": 1},
                {"product_id": p3.id, "quantity": 2},
            ],
        )
    )
    order_repo.create(
        OrderCreate(customer_id=cust2.id, items=[{"product_id": p2.id, "quantity": 1}])
    )
