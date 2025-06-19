import pandas as pd
from kafka import KafkaProducer
import json
import time
import os

def run_kafka_producer():
    """Reads review data and sends it to a Kafka topic."""
    producer = KafkaProducer(
        bootstrap_servers='kafka:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    file_path = os.path.join('data', 'Reviews.csv')
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Make sure you run from the root directory.")
        return

    print("Starting to send review data to Kafka topic 'airbnb-reviews'...")
    for index, row in df.head(15000).iterrows():
        message = row.to_dict()
        producer.send('airbnb-reviews', value=message)
        time.sleep(0.05) # Simulates a 0.05-second delay between reviews

    producer.flush()
    print("Finished sending all 15,000 reviews.")

if __name__ == "__main__":
    run_kafka_producer()