from app.repositories import IRepository
from app.models.domain import Category
from app.schemas import CategoryCreate, CategoryUpdate
from app.exceptions import NotFoundException


class CategoryService:
    def __init__(self, category_repository: IRepository[Category, CategoryCreate, CategoryUpdate]):
        self._repository = category_repository

    def get_category_by_id(self, category_id: int) -> Category:
        category = self._repository.get_by_id(category_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    def get_all_categories(self) -> list[Category]:
        return self._repository.get_all()

    def create_category(self, data: CategoryCreate) -> Category:
        return self._repository.create(data)

    def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self._repository.update(category_id, data)
        if not category:
            raise NotFoundException("Category", category_id)
        return category

    def delete_category(self, category_id: int) -> bool:
        deleted = self._repository.delete(category_id)
        if not deleted:
            raise NotFoundException("Category", category_id)
        return True
