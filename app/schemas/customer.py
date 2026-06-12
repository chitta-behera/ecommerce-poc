from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class Customer(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CustomerWithOrders(Customer):
    orders: list["Order"] = []
