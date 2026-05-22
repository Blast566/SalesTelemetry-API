from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class SaleModel(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    country = Column(String, index=True)
    state = Column(String)
    product_category = Column(String)
    order_quantity = Column(Integer)
    unit_cost = Column(Float)
    unit_price = Column(Float)
    profit = Column(Float)
    revenue = Column(Float)
