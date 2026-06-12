from functools import lru_cache
from app.repositories import (
    InMemoryCategoryRepository,
    InMemoryProductRepository,
    InMemoryCustomerRepository,
    InMemoryOrderRepository,
)
from app.services import (
    CategoryService,
    ProductService,
    CustomerService,
    OrderService,
)


@lru_cache(maxsize=1)
def get_category_repository() -> InMemoryCategoryRepository:
    return InMemoryCategoryRepository()


@lru_cache(maxsize=1)
def get_product_repository() -> InMemoryProductRepository:
    return InMemoryProductRepository()


@lru_cache(maxsize=1)
def get_customer_repository() -> InMemoryCustomerRepository:
    return InMemoryCustomerRepository()


@lru_cache(maxsize=1)
def get_order_repository() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()


@lru_cache(maxsize=1)
def get_category_service() -> CategoryService:
    return CategoryService(get_category_repository())


@lru_cache(maxsize=1)
def get_product_service() -> ProductService:
    return ProductService(get_product_repository(), get_category_repository())


@lru_cache(maxsize=1)
def get_customer_service() -> CustomerService:
    return CustomerService(get_customer_repository())


@lru_cache(maxsize=1)
def get_order_service() -> OrderService:
    return OrderService(
        get_order_repository(), get_customer_repository(), get_product_repository()
    )
