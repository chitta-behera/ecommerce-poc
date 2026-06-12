from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class IRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> ModelType | None:
        ...

    @abstractmethod
    def get_all(self) -> List[ModelType]:
        ...

    @abstractmethod
    def create(self, data: CreateSchemaType) -> ModelType:
        ...

    @abstractmethod
    def update(self, id: int, data: UpdateSchemaType) -> ModelType | None:
        ...

    @abstractmethod
    def delete(self, id: int) -> bool:
        ...
