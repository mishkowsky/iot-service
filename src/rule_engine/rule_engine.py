import os
from collections import deque, defaultdict
from datetime import timedelta, datetime
import pika
from bson import json_util
from loguru import logger

from dao.database import get_database
from model.iot_data import IoTData, TEMPERATURE_CRITICAL_VALUE, HUMIDITY_CRITICAL_VALUE, DISTANCE_DELTA_CRITICAL_VALUE
from utils import count_distance


class RuleEngine:
    HISTORY_LEN = 5

    def __init__(self):
        db = get_database()
        self.collection = db['alerts']
        self.received_data_history: defaultdict[int, deque[IoTData]] = defaultdict(
            lambda: deque(maxlen=RuleEngine.HISTORY_LEN))

    def process_next_message(self, ch, method, properties, body):
        json_str = body.decode("utf-8")
        logger.info(f'PROCESSING {json_str}')
        next_data_dict = json_util.loads(json_str)
        next_data = IoTData.model_validate(next_data_dict)

        device_history = self.received_data_history[next_data.device_id]

        # drop all history if last message outdated (more than 5 min)
        if len(device_history) != 0 and datetime.now() - device_history[-1].data_recieve_time > timedelta(minutes=5):
            device_history.clear()

        device_history.append(next_data)

        temp_accum = 0
        humidity_accum = 0
        for data in self.received_data_history[next_data.device_id]:
            if data.temperature > TEMPERATURE_CRITICAL_VALUE:
                temp_accum += 1
            if data.humidity > HUMIDITY_CRITICAL_VALUE:
                humidity_accum += 1

        alert_msgs = []
        triggered_event_ids_list = []

        if temp_accum == RuleEngine.HISTORY_LEN:
            alert_msgs.append('overheat')
            for data in self.received_data_history[next_data.device_id]:
                triggered_event_ids_list.append(data.data_id)
        if humidity_accum == RuleEngine.HISTORY_LEN:
            alert_msgs.append('over-water')
            for data in self.received_data_history[next_data.device_id]:
                triggered_event_ids_list.append(data.data_id)
        if (len(device_history) > 1 and
                count_distance(device_history[-1], device_history[-2]) > DISTANCE_DELTA_CRITICAL_VALUE):
            alert_msgs.append('strange-movement')
            triggered_event_ids_list.append(device_history[-2].data_id)
            triggered_event_ids_list.append(device_history[-1].data_id)

        for alert_msg in alert_msgs:
            logger.info(f'TRIGGERED {alert_msg} WITH EVENT IDS {triggered_event_ids_list}')
            self.collection.insert_one({
                'triggered_event_ids_list': triggered_event_ids_list,
                'alert': alert_msg
            })

    def monitor_rabbit_queue(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get('RABBITMQ_HOSTNAME')))
        channel = connection.channel()

        channel.queue_declare(queue='iot_data')

        channel.basic_consume(queue='iot_data', on_message_callback=self.process_next_message, auto_ack=True)

        logger.debug('Rule engine started. Waiting for messages')
        channel.start_consuming()


if __name__ == '__main__':
    logger.add("logs/rule_engine/logs.log", serialize=True)
    RuleEngine().monitor_rabbit_queue()
