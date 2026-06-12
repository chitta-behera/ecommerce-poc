from app.repositories import IRepository
from app.models.domain import Customer
from app.schemas import CustomerCreate, CustomerUpdate
from app.exceptions import NotFoundException


class CustomerService:
    def __init__(self, customer_repository: IRepository[Customer, CustomerCreate, CustomerUpdate]):
        self._repository = customer_repository

    def get_customer_by_id(self, customer_id: int) -> Customer:
        customer = self._repository.get_by_id(customer_id)
        if not customer:
            raise NotFoundException("Customer", customer_id)
        return customer

    def get_all_customers(self) -> list[Customer]:
        return self._repository.get_all()

    def create_customer(self, data: CustomerCreate) -> Customer:
        return self._repository.create(data)

    def update_customer(self, customer_id: int, data: CustomerUpdate) -> Customer:
        customer = self._repository.update(customer_id, data)
        if not customer:
            raise NotFoundException("Customer", customer_id)
        return customer

    def delete_customer(self, customer_id: int) -> bool:
        deleted = self._repository.delete(customer_id)
        if not deleted:
            raise NotFoundException("Customer", customer_id)
        return True
