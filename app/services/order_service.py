from app.repositories import IRepository
from app.models.domain import Order, Product, Customer
from app.schemas import (
    OrderCreate,
    OrderUpdate,
    ProductCreate,
    ProductUpdate,
    CustomerCreate,
    CustomerUpdate,
)
from app.exceptions import NotFoundException, ValidationException


class OrderService:
    def __init__(
        self,
        order_repository: IRepository[Order, OrderCreate, OrderUpdate],
        customer_repository: IRepository[Customer, CustomerCreate, CustomerUpdate],
        product_repository: IRepository[Product, ProductCreate, ProductUpdate],
    ):
        self._order_repository = order_repository
        self._customer_repository = customer_repository
        self._product_repository = product_repository

    def get_order_by_id(self, order_id: int) -> Order:
        order = self._order_repository.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order", order_id)

        # Eager load related entities
        customer = self._customer_repository.get_by_id(order.customer_id)
        if not customer:
            raise NotFoundException("Customer", order.customer_id)
        order.customer = customer

        for item in order.items:
            product = self._product_repository.get_by_id(item.product_id)
            if not product:
                raise NotFoundException("Product", item.product_id)
            item.product = product

        return order

    def get_all_orders(self) -> list[Order]:
        orders = self._order_repository.get_all()
        for order in orders:
            customer = self._customer_repository.get_by_id(order.customer_id)
            if customer:
                order.customer = customer
            for item in order.items:
                product = self._product_repository.get_by_id(item.product_id)
                if product:
                    item.product = product
        return orders

    def create_order(self, data: OrderCreate) -> Order:
        # Validate customer exists
        customer = self._customer_repository.get_by_id(data.customer_id)
        if not customer:
            raise ValidationException(f"Customer with id {data.customer_id} not found")

        # Validate all products exist
        for item in data.items:
            product = self._product_repository.get_by_id(item.product_id)
            if not product:
                raise ValidationException(
                    f"Product with id {item.product_id} not found"
                )

        order = self._order_repository.create(data)

        # Eager load for the response
        order.customer = customer
        for item in order.items:
            product = self._product_repository.get_by_id(item.product_id)
            if product:
                item.product = product # Should always be found due to validation

        return order

    def update_order_status(self, order_id: int, status: str) -> Order:
        order = self.get_order_by_id(order_id)
        data = OrderUpdate(customer_id=order.customer_id, status=status)
        updated_order = self._order_repository.update(order_id, data)
        if not updated_order:
            raise NotFoundException("Order", order_id)
        return self.get_order_by_id(order_id) # Re-fetch to eager load

    def delete_order(self, order_id: int) -> bool:
        deleted = self._order_repository.delete(order_id)
        if not deleted:
            raise NotFoundException("Order", order_id)
        return True
