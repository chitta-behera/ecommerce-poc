from pydantic import BaseModel, ConfigDict, Field

from .category import Category


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0, description="The price must be greater than zero")
    sku: str


class ProductCreate(ProductBase):
    category_id: int


class ProductUpdate(ProductBase):
    name: str | None = None
    price: float | None = Field(default=None, gt=0, description="The price must be greater than zero")
    sku: str | None = None
    category_id: int | None = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: Category
