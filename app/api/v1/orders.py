from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services import OrderService
from app.schemas import Order, OrderCreate, OrderUpdate
from app.exceptions import NotFoundException, ValidationException
from app.dependencies import get_order_service

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Order], summary="Get all orders")
def read_orders(service: OrderService = Depends(get_order_service)):
    """
    Retrieve all orders.
    """
    return service.get_all_orders()


@router.post(
    "/",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
def create_order(order: OrderCreate, service: OrderService = Depends(get_order_service)):
    """
    Create a new order. Requires a valid customer_id and valid product_ids in the items list.
    """
    try:
        return service.create_order(order)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/{order_id}", response_model=Order, summary="Get an order by ID")
def read_order(order_id: int, service: OrderService = Depends(get_order_service)):
    """
    Retrieve a specific order by its ID.
    """
    try:
        return service.get_order_by_id(order_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{order_id}/status", response_model=Order, summary="Update an order's status")
def update_order_status(
    order_id: int,
    status_update: dict[str, str],
    service: OrderService = Depends(get_order_service),
):
    """
    Update the status of an existing order (e.g., "shipped", "delivered").
    Expects a JSON body like: {"status": "shipped"}
    """
    try:
        new_status = status_update.get("status")
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status field is required",
            )
        return service.update_order_status(order_id, new_status)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{order_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an order"
)
def delete_order(order_id: int, service: OrderService = Depends(get_order_service)):
    """
    Delete an order by its ID.
    """
    try:
        service.delete_order(order_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
