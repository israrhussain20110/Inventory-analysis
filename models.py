from pydantic import BaseModel, Field, Extra
from typing import Optional
from datetime import datetime

class InventoryItem(BaseModel):
    Date: datetime
    ProductID: str = Field(..., alias='Product ID')
    InventoryLevel: int = Field(..., alias='Inventory Level')
    UnitsSold: int = Field(..., alias='Units Sold')
    UnitsOrdered: int = Field(..., alias='Units Ordered')
    DemandForecast: float = Field(..., alias='Demand Forecast')
    Price: float
    Discount: int
    WeatherCondition: str = Field(..., alias='Weather Condition')
    HolidayPromotion: int = Field(..., alias='Holiday/Promotion')
    CompetitorPricing: float = Field(..., alias='Competitor Pricing')
    Seasonality: str
    Category: str
    Region: str
    StoreId: str = Field(..., alias='Store ID')

    class Config:
        populate_by_name = True
        extra = Extra.allow

class SalesRecord(BaseModel):
    Date: datetime
    ProductID: str = Field(..., alias='Product ID')
    UnitsSold: int = Field(..., alias='Units Sold')
    Price: float
    StoreId: str = Field(..., alias='Store ID')

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

class ForecastRequest(BaseModel):
    store_id: str = Field(..., alias='Store ID')
    product_id: str = Field(..., alias='Product ID')
    granularity: str = "monthly"
    model_type: str = "linear_regression" # Added this line, with a default

    class Config:
        extra = Extra.allow