from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import List
from tronpy.keys import is_address


class AddressRequest(BaseModel):
    address: str = Field(..., description="Адрес в сети Tron")

    @field_validator("address")
    def validate_tron_address(cls, v):
        if not is_address(v):
            raise ValueError("Введённый адрес не является адресом в сети Tron.")
        return v


class AddressInfo(BaseModel):
    address: str
    balance_trx: float
    bandwidth: int
    energy: int


class AddressQueryResponse(AddressInfo):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAddressQueries(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AddressQueryResponse]
