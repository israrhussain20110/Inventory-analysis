from pydantic import BaseModel, Field, Extra
from typing import Optional
from datetime import datetime

class RetailData(BaseModel):
    Date: datetime
    StoreId: str
    ProductID: str
    Category: Optional[str] = None
    Region: Optional[str] = None
    Inventory: Optional[int] = None
    Sales: Optional[int] = None
    Orders: Optional[int] = None
    Demand: Optional[float] = None
    Price: Optional[float] = None
    Discount: Optional[int] = None
    Weather: Optional[str] = None
    Promotion: Optional[int] = None
    CompetitorPrice: Optional[float] = None
    Seasonality: Optional[str] = None
    cost: Optional[float] = None
    abc_class: Optional[str] = None

    class Config:
        populate_by_name = True
        extra = Extra.allow

class MetricRequest(BaseModel):
    store_id: str = Field(..., alias='Store ID')
    product_id: str = Field(..., alias='Product ID')

    class Config:
        extra = Extra.allow

class DataStatusResponse(BaseModel):
    is_loaded: bool
    record_count: int

    class Config:
        extra = Extra.allow

class MetricRequest(BaseModel):
    store_id: str = Field(..., alias='Store ID')
    product_id: str = Field(..., alias='Product ID')

    class Config:
        extra = Extra.allow

class DataStatusResponse(BaseModel):
    is_loaded: bool
    record_count: int

    class Config:
        extra = Extra.allow