# src/ml_training/train_model.py (VERSI FIX CARDINALITY - dengan ColumnTransformer)

import pandas as pd
from minio import Minio
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import io
import os
import numpy as np
from math import sqrt

def train_and_save_model():
    """Melatih model yang lebih akurat dan menyimpannya ke MinIO."""
    # --- 1. Load Data ---
    print("Loading data for training...")
    file_path = os.path.join('data', 'Listings.csv')
    try:
        df = pd.read_csv(file_path, low_memory=False, encoding='latin-1', nrows=250000)
    except FileNotFoundError:
        print(f"FATAL ERROR: {file_path} not found. Pastikan file data ada.")
        return
    print("Data loaded.")

    # --- 2. Feature Selection & Cleaning ---
    features = [
        'host_response_rate', 'host_is_superhost', 'host_total_listings_count',
        'neighbourhood', 'property_type', 'room_type', 'accommodates',
        'bedrooms', 'review_scores_rating', 'review_scores_cleanliness',
        'review_scores_location'
    ]
    target = 'price'

    df = df[features + [target]]
    df['price'] = df['price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
    df['host_response_rate'] = df['host_response_rate'].astype(str).str.replace('%', '').astype(float) / 100
    df['host_is_superhost'] = df['host_is_superhost'].apply(lambda x: 1 if x == 't' else 0)
    df.dropna(subset=features + [target], inplace=True)
    print("Data cleaning complete.")

    # --- 3. Preprocessing ---
    X = df[features]
    y = np.log1p(df[target])  # log(price + 1) untuk stabilitas

    onehot_features = ['neighbourhood', 'property_type', 'room_type']
    passthrough_features = [
        'host_response_rate', 'host_is_superhost', 'host_total_listings_count',
        'property_type', 'room_type', 'accommodates', 'bedrooms',
        'review_scores_rating', 'review_scores_cleanliness', 'review_scores_location'
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False), onehot_features)
        ],
        remainder='passthrough'
    )

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', HistGradientBoostingRegressor(random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Training HistGradientBoostingRegressor model with pipeline...")
    pipeline.fit(X_train, y_train)

    # --- 5. Evaluation ---
    y_pred_log = pipeline.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    y_test_original = np.expm1(y_test)

    mae = mean_absolute_error(y_test_original, y_pred)
    rmse = sqrt(mean_squared_error(y_test_original, y_pred))
    r2 = pipeline.score(X_test, y_test)

    print(f"Model Evaluation: R^2={r2:.2f}, MAE={mae:.2f}, RMSE={rmse:.2f}")

    # --- 6. Save Model to MinIO ---
    print("Saving model to MinIO...")
    try:
        client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )
        bucket_name = "models"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)

        model_file = io.BytesIO()
        joblib.dump(pipeline, model_file)
        model_file.seek(0)

        client.put_object(
            bucket_name, "price_prediction_model.joblib", data=model_file,
            length=model_file.getbuffer().nbytes, content_type='application/octet-stream'
        )
        print(f"SUCCESS: Model saved to MinIO bucket '{bucket_name}'.")
    except Exception as e:
        print(f"FATAL ERROR: Could not connect to MinIO or save model. Details: {e}")

if __name__ == "__main__":
    train_and_save_model()