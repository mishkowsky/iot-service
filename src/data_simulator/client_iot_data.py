from datetime import datetime
from pydantic import BaseModel, confloat


class IoTClientData(BaseModel):
    device_id: int
    temperature: float
    humidity: float
    latitude: confloat(ge=-90, le=90)  # Географическая широта в диапазоне от -90 до 90
    longitude: confloat(ge=-180, le=180)  # Географическая долгота в диапазоне от -180 до 180
    timestamp: datetime
