import pandas as pd
from kafka import KafkaProducer
import json
import time
import os

def run_kafka_producer():
    """Reads review data and sends it to a Kafka topic."""
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    file_path = os.path.join('data', 'Reviews.csv')
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Make sure you run from the root directory.")
        return

    print("Starting to send review data to Kafka topic 'airbnb-reviews'...")
    for index, row in df.iterrows():
        message = row.to_dict()
        producer.send('airbnb-reviews', value=message)
        print(f"Sent review ID: {message['review_id']}")
        time.sleep(1) # Simulates a 1-second delay between reviews

    producer.flush()
    print("Finished sending all reviews.")

if __name__ == "__main__":
    run_kafka_producer()