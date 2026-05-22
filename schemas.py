from pydantic import BaseModel
from datetime import date


class SaleResponse(BaseModel):
    id: int
    date: date
    country: str
    state: str
    product_category: str
    order_quantity: int
    unit_cost: float
    unit_price: float
    profit: float
    revenue: float

    class Config:
        from_attributes = True


class KPIResponse(BaseModel):
    total_revenue: float
    total_profit: float
    total_cost: float
    number_of_purchases: int
    profit_margin: float


class UploadResponse(BaseModel):
    rows_loaded: int
    filename: str
