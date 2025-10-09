from google.cloud import pubsub_v1
import json

_publisher = pubsub_v1.PublisherClient()

def publish(topic_name: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    _publisher.publish(topic_name, data=data)