from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: str | None = None


class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CategoryWithProducts(Category):
    products: list["Product"] = []
