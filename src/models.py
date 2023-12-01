from pydantic import BaseModel
from typing import Optional


class ProductInfo(BaseModel):
    user_id: str
    user: str
    username: str
    order_date: str
    loc_id: str
    price: float
    currency_id: str
    quantity: int
    weight: float
    views: int
    rating: int
    product_id: str
    title: str
    description: str
    appraisal_id: Optional[int]
