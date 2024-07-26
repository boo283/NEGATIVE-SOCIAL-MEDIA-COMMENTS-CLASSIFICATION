import json
import time
from kafka import KafkaConsumer, KafkaProducer
from classification import predict
from utils import create_consumer, create_producer

def consume_comments():
    consumer = create_consumer('StreamComments')
    producer = create_producer()

    for message in consumer:
        comment = message.value
        prediction = predict(comment["text"])
        
        pred = ''
        if prediction == 0:
            pred = "Others"
        elif prediction == 1:
            pred = "Hate speech"
        elif prediction == 2:
            pred = "Personal attack"
        else:
            pred = "Discrimination"

        comment["label"] = pred
        print(f"Comment: {comment['text']} - Prediction: {pred}")
        time.sleep(2)
        producer.send('ClassifiedComments', value=comment)
 
    time.sleep(1)
    producer.flush()
    print("All comments sent!")

if __name__ == "__main__":
    try:
        print('Run ')
        consume_comments()
        print('End')
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
