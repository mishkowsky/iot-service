from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, confloat
import pydantic
from bson import ObjectId

TEMPERATURE_CRITICAL_VALUE = 60
HUMIDITY_CRITICAL_VALUE = 60

DISTANCE_DELTA_CRITICAL_VALUE = 9.0


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class IoTData(BaseModel):
    device_id: int
    temperature: float
    humidity: float
    latitude: confloat(ge=-90, le=90)  # Географическая широта в диапазоне от -90 до 90
    longitude: confloat(ge=-180, le=180)  # Географическая долгота в диапазоне от -180 до 180
    timestamp: datetime
    data_recieve_time: Optional[datetime] = None
    data_id: Optional[ObjectId] = None
