from math import sin, cos, sqrt, atan2, radians
from model.iot_data import IoTData


def count_distance(data_1: IoTData, data_2: IoTData) -> float:
    R = 6373.0

    lat1 = radians(data_1.latitude)
    lon1 = radians(data_1.longitude)

    lat2 = radians(data_2.latitude)
    lon2 = radians(data_2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c * 1000  # meters

    return distance
