from datetime import datetime
from bson import json_util
from flask import Flask, jsonify
from flask_pydantic import validate
from prometheus_flask_exporter import PrometheusMetrics
from loguru import logger
from dao.database import get_database
from iot_web_api.rabbitmq_manager import RabbitMQManager
from model.iot_data import IoTData

app = Flask(__name__)
PrometheusMetrics(app)
endpoints = ("data", )

db = get_database()
collection = db['iot_data']

broker = RabbitMQManager()

logger.add("logs/iot_web_api/logs.log", serialize=True)


@app.route('/data', methods=['PUT'])
@validate()
def receive_data(body: IoTData):
    body.data_recieve_time = datetime.now()
    data = body.model_dump(mode='json')

    logger.info(f'RECEIVED: {data}')

    result = collection.insert_one(data)
    logger.info(f'ADDED TO DB {result}')
    logger.debug(f'DATA AFTER INSERTION {data}')

    data['data_id'] = data['_id']
    del data['_id']
    broker.publsih_data(data)

    return jsonify({"message": "Data received and processed", "data": json_util.dumps(data)}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
