import json
from kafka import KafkaProducer, KafkaConsumer

def create_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except Exception as e:
        print("Couldn't create the producer")
        producer = None
    return producer

def create_consumer(topic):
    try:
        consumer = KafkaConsumer(
            topic,
            auto_offset_reset='earliest',
            bootstrap_servers=['localhost:9092'],
            enable_auto_commit=True,
            group_id='comment-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
    except Exception as e:
        print("Couldn't create the consumer")
        consumer = None
    return consumer
