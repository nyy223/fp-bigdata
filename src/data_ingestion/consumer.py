from kafka import KafkaConsumer
from minio import Minio
import json
import io

def run_kafka_consumer():
    """Consumes data from Kafka and stores it in MinIO bronze bucket."""
    consumer = KafkaConsumer(
        'airbnb-reviews',
        bootstrap_servers='kafka:29092',
        auto_offset_reset='earliest', # Start reading from the beginning of the topic
        group_id='airbnb-review-savers',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    client = Minio(
        "minio:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    bucket_name = "bronze"
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")

    print("Listening for messages from Kafka...")
    for message in consumer:
        review_data = message.value
        review_id = review_data['review_id']
        file_name = f"raw_review_{review_id}.json"
        
        # Convert dict to JSON string, then to bytes
        json_bytes = json.dumps(review_data, indent=4).encode('utf-8')
        
        # Upload to MinIO
        client.put_object(
            bucket_name=bucket_name,
            object_name=file_name,
            data=io.BytesIO(json_bytes),
            length=len(json_bytes),
            content_type='application/json'
        )

if __name__ == "__main__":
    run_kafka_consumer()