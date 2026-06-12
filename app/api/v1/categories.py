from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services import CategoryService
from app.schemas import Category, CategoryCreate, CategoryUpdate
from app.exceptions import NotFoundException
from app.dependencies import get_category_service

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Category], summary="Get all categories")
def read_categories(service: CategoryService = Depends(get_category_service)):
    """
    Retrieve all categories.
    """
    return service.get_all_categories()


@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
def create_category(
    category: CategoryCreate, service: CategoryService = Depends(get_category_service)
):
    """
    Create a new category.
    """
    return service.create_category(category)


@router.get(
    "/{category_id}",
    response_model=Category,
    summary="Get a category by ID",
)
def read_category(category_id: int, service: CategoryService = Depends(get_category_service)):
    """
    Retrieve a specific category by its ID.
    """
    try:
        return service.get_category_by_id(category_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{category_id}",
    response_model=Category,
    summary="Update a category",
)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    """
    Update a category's details.
    """
    try:
        return service.update_category(category_id, category)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
)
def delete_category(
    category_id: int, service: CategoryService = Depends(get_category_service)
):
    """
    Delete a category by its ID.
    """
    try:
        service.delete_category(category_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
