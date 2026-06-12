from app.repositories import IRepository
from app.models.domain import Product, Category
from app.schemas import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate
from app.exceptions import NotFoundException, ValidationException


class ProductService:
    def __init__(
        self,
        product_repository: IRepository[Product, ProductCreate, ProductUpdate],
        category_repository: IRepository[Category, CategoryCreate, CategoryUpdate],
    ):
        self._product_repository = product_repository
        self._category_repository = category_repository

    def get_product_by_id(self, product_id: int) -> Product:
        product = self._product_repository.get_by_id(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        # Eager load category
        category = self._category_repository.get_by_id(product.category_id)
        if not category:
            # This indicates a data integrity issue, but we'll handle it
            raise NotFoundException("Category", product.category_id)
        product.category = category
        return product

    def get_all_products(self) -> list[Product]:
        products = self._product_repository.get_all()
        for product in products:
            category = self._category_repository.get_by_id(product.category_id)
            if category:
                product.category = category
        return products

    def create_product(self, data: ProductCreate) -> Product:
        # Validate that the category exists
        category = self._category_repository.get_by_id(data.category_id)
        if not category:
            raise ValidationException(f"Category with id {data.category_id} not found")

        product = self._product_repository.create(data)
        product.category = category
        return product

    def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        # Validate that the product exists before trying to update
        self.get_product_by_id(product_id)

        # If category_id is being updated, validate it exists
        if data.category_id is not None:
            category = self._category_repository.get_by_id(data.category_id)
            if not category:
                raise ValidationException(
                    f"Category with id {data.category_id} not found"
                )

        updated_product = self._product_repository.update(product_id, data)
        if not updated_product:
            raise NotFoundException("Product", product_id)  # Should be caught by get_product_by_id

        # Eager load the category for the updated product
        if updated_product.category_id:
            category = self._category_repository.get_by_id(updated_product.category_id)
            if category:
                updated_product.category = category

        return updated_product

    def delete_product(self, product_id: int) -> bool:
        deleted = self._product_repository.delete(product_id)
        if not deleted:
            raise NotFoundException("Product", product_id)
        return True
