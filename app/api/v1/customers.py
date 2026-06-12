from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.services import CustomerService
from app.schemas import Customer, CustomerCreate, CustomerUpdate
from app.exceptions import NotFoundException
from app.dependencies import get_customer_service

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Customer], summary="Get all customers")
def read_customers(service: CustomerService = Depends(get_customer_service)):
    """
    Retrieve all customers.
    """
    return service.get_all_customers()


@router.post(
    "/",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
)
def create_customer(
    customer: CustomerCreate, service: CustomerService = Depends(get_customer_service)
):
    """
    Create a new customer.
    """
    return service.create_customer(customer)


@router.get("/{customer_id}", response_model=Customer, summary="Get a customer by ID")
def read_customer(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    """
    Retrieve a specific customer by their ID.
    """
    try:
        return service.get_customer_by_id(customer_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{customer_id}", response_model=Customer, summary="Update a customer")
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
):
    """
    Update a customer's details.
    """
    try:
        return service.update_customer(customer_id, customer)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a customer"
)
def delete_customer(customer_id: int, service: CustomerService = Depends(get_customer_service)):
    """
    Delete a customer by their ID.
    """
    try:
        service.delete_customer(customer_id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
