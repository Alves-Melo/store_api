from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0)
    description: Optional[str] = None

    @field_validator("price")
    @classmethod
    def price_two_decimals(cls, v: float) -> float:
        return round(float(v), 2)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    price: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = None

class ProductRead(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
