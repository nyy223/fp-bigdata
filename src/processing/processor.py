import pandas as pd
from minio import Minio
import json
import io
import joblib
import os

def process_and_predict():
    """Processes raw data, predicts prices, and stores results in the gold bucket."""
    client = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)

    # --- 1. Load Model from MinIO ---
    print("Loading model from MinIO...")
    try:
        model_object = client.get_object("models", "price_prediction_model.joblib")
        model_file = io.BytesIO(model_object.read())
        model = joblib.load(model_file)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}. Did you run the training script first?")
        return
        
    # --- 2. Load Static Listing Data ---
    # Added encoding='latin-1' to match the training script
    listings_df = pd.read_csv(os.path.join('data', 'Listings.csv'), low_memory=False, encoding='latin-1')
    listings_df['listing_id'] = listings_df['listing_id'].astype(str)
    
    # --- 3. Process each file in Bronze bucket ---
    bronze_bucket = "bronze"
    gold_bucket = "gold"
    if not client.bucket_exists(gold_bucket):
        client.make_bucket(gold_bucket)

    print(f"Checking for new reviews in '{bronze_bucket}' bucket...")
    raw_reviews = client.list_objects(bronze_bucket, recursive=True)
    
    for review_obj in raw_reviews:
        # Get raw review data
        review_file = client.get_object(bronze_bucket, review_obj.object_name)
        review_data = json.load(review_file)
        listing_id = str(review_data['listing_id'])
        
        # Find corresponding listing
        listing_info = listings_df[listings_df['listing_id'] == listing_id]
        
        if listing_info.empty:
            print(f"Listing ID {listing_id} not found. Skipping review {review_data['review_id']}.")
            continue

        # Prepare data for prediction (must match training format)
        prediction_input = listing_info.copy()
        
        # --- START: REPLICATE PRE-PROCESSING FROM TRAINING SCRIPT ---
        # This is crucial! The data for prediction must have the exact same format
        # as the data used for training.
        
        # 1. Clean host_response_rate
        if 'host_response_rate' in prediction_input.columns:
            # Handle potential NaNs before converting to string
            prediction_input['host_response_rate'] = prediction_input['host_response_rate'].fillna('0%').astype(str).str.replace('%', '').astype(float) / 100

        # 2. Convert boolean host_is_superhost
        if 'host_is_superhost' in prediction_input.columns:
            prediction_input['host_is_superhost'] = prediction_input['host_is_superhost'].apply(lambda x: 1 if x == 't' else 0)
        
        # --- END: REPLICATE PRE-PROCESSING ---

        # Predict
        try:
            # Get feature names from the trained pipeline
            # This makes the code robust against column order changes
            feature_columns = [
                'host_response_rate', 'host_is_superhost', 'host_total_listings_count',
                'neighbourhood', 'property_type', 'room_type', 'accommodates',
                'bedrooms', 'review_scores_rating', 'review_scores_cleanliness',
                'review_scores_location'
            ]
            
            # Ensure all feature columns exist and fill NaNs in numeric columns
            for col in feature_columns:
                if col not in prediction_input.columns:
                    # If a column is missing, add it with a default value (e.g., 0 or mean)
                    prediction_input[col] = 0 
            
            prediction_input.fillna(0, inplace=True) # Simple NaN handling for prediction

            predicted_price = model.predict(prediction_input[feature_columns])[0]

            # --- 4. Create enriched output ---
            output_data = {
                "review_info": review_data,
                "listing_info": listing_info.iloc[0].to_dict(),
                "prediction": {
                    "predicted_optimal_price": round(predicted_price, 2),
                    "current_price_str": listing_info.iloc[0]['price']
                }
            }
            
            # --- 5. Save to Gold bucket ---
            output_filename = f"processed_{review_data['review_id']}.json"
            json_bytes = json.dumps(output_data, indent=4, default=str).encode('utf-8')

            client.put_object(
                gold_bucket,
                output_filename,
                data=io.BytesIO(json_bytes),
                length=len(json_bytes),
                content_type='application/json'
            )
            print(f"Processed review for listing {listing_id}. Saved to '{gold_bucket}'. Predicted price: ${predicted_price:.2f}")
            
            # Optional: Delete from bronze after processing
            client.remove_object(bronze_bucket, review_obj.object_name)

        except Exception as e:
            print(f"Prediction failed for listing {listing_id}: {e}")
            continue

if __name__ == "__main__":
    process_and_predict()