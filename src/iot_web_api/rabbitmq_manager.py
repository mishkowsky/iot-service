import os
from threading import Lock

import pika
from bson import json_util
from loguru import logger

class RabbitMQManager:

    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()
        self.channel_lock = Lock()

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get('RABBITMQ_HOSTNAME')))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='iot_data')

    def publsih_data(self, data):
        if self.connection.is_closed:
            logger.warning('RABBITMQ CONNECTION IS DOWN')
            self.connect()
            self.publsih_data(data)
            return

        with self.channel_lock:
            try:
                logger.debug('PUBLISHING TO RABBITMQ')
                self.channel.basic_publish(exchange='', routing_key='iot_data', body=json_util.dumps(data))  # json.dumps(data))
            except Exception as e:
                logger.exception(e)
                self.publsih_data(data)
