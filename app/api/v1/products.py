from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services import ProductService
from app.schemas import Product, ProductCreate, ProductUpdate
from app.exceptions import NotFoundException, ValidationException
from app.dependencies import get_product_service

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Product], summary="Get all products")
def read_products(service: ProductService = Depends(get_product_service)):
    """
    Retrieve all products.
    """
    return service.get_all_products()


@router.post(
    "/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
def create_product(
    product: ProductCreate, service: ProductService = Depends(get_product_service)
):
    """
    Create a new product. Requires a valid category_id.
    """
    try:
        return service.create_product(product)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/{product_id}", response_model=Product, summary="Get a product by ID")
def read_product(product_id: int, service: ProductService = Depends(get_product_service)):
    """
    Retrieve a specific product by its ID.
    """
    try:
        return service.get_product_by_id(product_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{product_id}", response_model=Product, summary="Update a product")
def update_product(
    product_id: int,
    product: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    """
    Update a product's details.
    """
    try:
        return service.update_product(product_id, product)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.delete(
    "/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a product"
)
def delete_product(product_id: int, service: ProductService = Depends(get_product_service)):
    """
    Delete a product by its ID.
    """
    try:
        service.delete_product(product_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
