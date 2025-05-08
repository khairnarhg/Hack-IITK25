import asyncio
import base64
import json
import scapy.all as scapy
from kafka import KafkaConsumer
from utils.packet_processor import process_and_classify
from routers.ws_connections import logs_manager, alerts_manager
import os

LOGS = []
JSON_LOGS_PATH = os.path.join(
    os.path.dirname(__file__), 
    "public", 
    "data", 
    "incoming_logs.json"
)

def run_kafka_consumer(loop):
    consumer = KafkaConsumer(
        'packets',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        group_id='fastapi-consumer-group'
    )
    print("Kafka consumer started...")

    for msg in consumer:
        try:
            print("Received Kafka message")
            encoded_data = msg.value.decode('utf-8')
            raw_bytes = base64.b64decode(encoded_data)
            packet = scapy.Ether(raw_bytes)
            print("Packet reconstructed from Kafka message.")

            batch_log = process_and_classify(packet)
            if batch_log is not None:
                print("50 packets accumulated. Batch log ready:")
                print(batch_log)
                LOGS.insert(0, batch_log)
                with open(JSON_LOGS_PATH, "w", encoding="utf-8") as f:
                    json.dump(LOGS, f, indent=2)
                print(f"Batch log written to {JSON_LOGS_PATH}")

                # Send the batch log (which includes the 50 packets) over the logs websocket.
                loop.create_task(
                    logs_manager.broadcast(json.dumps(batch_log))
                )
                print("Batch log sent over logs WebSocket.")

                # If a threat is detected, also send an alert over the alerts websocket.
                if batch_log["Prediction"] == 1:
                    loop.create_task(
                        alerts_manager.broadcast("Threat detected in aggregated batch!")
                    )
                    print("Alert message sent over alerts WebSocket.")
        except Exception as e:
            print("Error processing Kafka message:", e)

