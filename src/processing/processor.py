# src/processing/processor.py (VERSI FINAL & BENAR)

import pandas as pd
from minio import Minio
import json
import io
import joblib
import os

# --- KONFIGURASI ---
MINIO_CLIENT = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
BRONZE_BUCKET = "bronze"
GOLD_BUCKET = "gold"
MODELS_BUCKET = "models"
MODEL_NAME = "price_prediction_model.joblib"

# --- FUNGSI UTAMA ---
def main():
    # Muat data dan model terlebih dahulu
    try:
        listings_df = pd.read_csv(os.path.join('data', 'Listings.csv'), low_memory=False, encoding='latin-1')
        # --- PERBAIKAN KUNCI DI SINI ---
        listings_df['listing_id'] = listings_df['listing_id'].astype(str) # Gunakan nama kolom yang benar
        
        model_object = MINIO_CLIENT.get_object(MODELS_BUCKET, MODEL_NAME)
        model_pipeline = joblib.load(io.BytesIO(model_object.read()))
    except Exception as e:
        print(f"FATAL ERROR: Could not load initial data or model. Is model trained? Details: {e}")
        return

    # Buat bucket gold jika belum ada
    if not MINIO_CLIENT.bucket_exists(GOLD_BUCKET):
        MINIO_CLIENT.make_bucket(GOLD_BUCKET)

    # Periksa file baru di bronze
    raw_reviews_objects = list(MINIO_CLIENT.list_objects(BRONZE_BUCKET, recursive=True))
    if not raw_reviews_objects:
        print("Bronze bucket is empty. Nothing to process.")
        return
    
    print(f"Found {len(raw_reviews_objects)} new reviews. Starting processing and retraining cycle.")
    
    batch_data_for_training = []
    
    # --- 1. PROSES SEMUA FILE DARI BRONZE KE GOLD ---
    for review_obj in raw_reviews_objects:
        try:
            review_file = MINIO_CLIENT.get_object(BRONZE_BUCKET, review_obj.object_name)
            review_data = json.load(review_file)
            listing_id = str(review_data['listing_id'])
            
            # --- PERBAIKAN KUNCI DI SINI ---
            listing_info = listings_df[listings_df['listing_id'] == listing_id] # Gunakan nama kolom yang benar
            if listing_info.empty:
                continue

            # Siapkan data untuk prediksi (tanpa menyentuh target)
            prediction_input = listing_info.copy()
            if 'host_response_rate' in prediction_input.columns:
                prediction_input['host_response_rate'] = prediction_input['host_response_rate'].astype(str).str.replace('%', '').astype(float) / 100
            if 'host_is_superhost' in prediction_input.columns:
                prediction_input['host_is_superhost'] = prediction_input['host_is_superhost'].apply(lambda x: 1 if x == 't' else 0)
            
            # Buat prediksi
            features = list(model_pipeline.named_steps['preprocessor'].transformers_[0][2]) + \
                       list(model_pipeline.named_steps['preprocessor'].transformers_[1][2])
            predicted_price = model_pipeline.predict(prediction_input[features])[0]

            # Siapkan data output untuk bucket GOLD
            output_data = {
                "review_info": review_data,
                "listing_info": json.loads(listing_info.iloc[0].to_json()),
                "prediction": {
                    "predicted_price_usd": round(predicted_price, 2),
                    "current_price_str": listing_info.iloc[0]['price']
                }
            }
            
            # Simpan ke Gold
            output_filename = f"enriched_review_{review_data['review_id']}.json"
            json_bytes = json.dumps(output_data, indent=4).encode('utf-8')
            MINIO_CLIENT.put_object(GOLD_BUCKET, output_filename, data=io.BytesIO(json_bytes), length=len(json_bytes), content_type='application/json')
            
            batch_data_for_training.append(prediction_input)
        except Exception as e:
            print(f"Skipping file {review_obj.object_name} due to error: {e}")
            continue

    # --- 2. LATIH ULANG MODEL ---
    if batch_data_for_training:
        print(f"Incrementally training model with {len(batch_data_for_training)} new records...")
        training_df = pd.concat(batch_data_for_training, ignore_index=True)
        
        training_df['price'] = training_df['price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        training_df.dropna(subset=features + ['price'], inplace=True)
        
        if not training_df.empty:
            X_train = training_df[features]
            y_train = training_df['price']
            
            model_pipeline.partial_fit(X_train, y_train)

            updated_model_file = io.BytesIO()
            joblib.dump(model_pipeline, updated_model_file)
            updated_model_file.seek(0)
            MINIO_CLIENT.put_object(
                MODELS_BUCKET, MODEL_NAME, data=updated_model_file,
                length=updated_model_file.getbuffer().nbytes, content_type='application/octet-stream'
            )
            print("Model updated successfully.")

    # --- 3. BERSIHKAN BRONZE BUCKET ---
    print("Cleaning up processed files from bronze bucket...")
    for review_obj in raw_reviews_objects:
        MINIO_CLIENT.remove_object(BRONZE_BUCKET, review_obj.object_name)
    print("Cleanup complete.")

if __name__ == "__main__":
    main()