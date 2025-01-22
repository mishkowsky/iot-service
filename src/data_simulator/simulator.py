import random
import time
import multiprocessing
from datetime import datetime, timezone
from multiprocessing import Process

import requests
from loguru import logger

from data_simulator.client_iot_data import IoTClientData

MIN_TEMPERATURE = -10
MAX_TEMPERATURE = 100

MIN_HUNIDITY = 10
MAX_HUNIDITY = 90

COORD_MAX_DELTA = 0.0001

MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0

MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0


class DeviceSimulator:
    def __init__(self, device_id: int, delay: float):
        self.device_id: int = device_id
        self.delay: float = delay
        self.active: bool = False
        self.current_temperature: float = random.uniform(MIN_TEMPERATURE, MAX_TEMPERATURE)
        self.current_hunidity: float = random.uniform(MIN_HUNIDITY, MAX_HUNIDITY)
        self.current_latitude: float = random.uniform(MIN_LATITUDE, MAX_LATITUDE)  # in deegres
        self.current_longitude: float = random.uniform(MIN_LONGITUDE, MAX_LONGITUDE)
        self.process: Process | None = None

    def send_data(self):
        self.current_temperature = self.current_temperature + random.uniform(-10, 10)
        self.current_hunidity = self.current_hunidity + random.uniform(-10, 10)

        lon_delta = random.uniform(-COORD_MAX_DELTA, COORD_MAX_DELTA)
        lat_delta = random.uniform(-COORD_MAX_DELTA, COORD_MAX_DELTA)

        self.current_latitude = max(MIN_LATITUDE, min(MAX_LATITUDE, self.current_latitude + lat_delta))
        self.current_longitude = max(MIN_LONGITUDE, min(MAX_LONGITUDE, self.current_longitude + lon_delta))

        data = IoTClientData(device_id=self.device_id, temperature=self.current_temperature,
                             humidity=self.current_hunidity, latitude=self.current_latitude,
                             longitude=self.current_longitude, timestamp=datetime.now(tz=timezone.utc))

        logger.info(f"{self} SENDING {data.model_dump_json()}")
        try:
            json_obj = data.model_dump(mode='json')
            response = requests.put("http://localhost:5010/data", json=json_obj)
            logger.info(f'{self} REQUEST RESPONSE {response.status_code} ')
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f'{self} JSON: {response.json()}')
        except requests.exceptions.ConnectionError:
            logger.error(f'WEB API IS NOT AVAILABLE FOR DEVICE {self.device_id}')

    def send_loop(self):
        logger.info(f"{self} STARTED SENDING DATA")
        while self.active:
            self.send_data()
            logger.debug(f'{self} SLEEP FOR {self.delay} SEC')
            time.sleep(self.delay)
        logger.info(f"{self} ENDED SENDING DATA")
        self.process = None

    def run(self) -> Process:
        self.active = True
        self.process = None
        proc = multiprocessing.Process(target=self.send_loop, args=())
        proc.start()
        self.process = proc
        return proc

    def __repr__(self):
        return f'Device id={self.device_id}'
