# src/ml_training/train_model.py (VERSI FINAL & BENAR)

import pandas as pd
from minio import Minio
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDRegressor # Menggunakan model yang tepat
import joblib
import io
import os

def train_and_save_model():
    """Melatih model awal dan menyimpannya ke MinIO."""
    # --- 1. Load Data ---
    print("Loading data for initial training...")
    file_path = os.path.join('data', 'Listings.csv')
    try:
        # Menggunakan encoding yang benar dan hanya memuat sebagian untuk kecepatan
        df = pd.read_csv(file_path, low_memory=False, encoding='latin-1', nrows=250000)
    except FileNotFoundError:
        print(f"FATAL ERROR: {file_path} not found. Pastikan file data ada.")
        return
    print("Data loaded.")

    # --- 2. Feature Selection & Pembersihan Awal ---
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

    # --- 3. Preprocessing Pipeline ---
    X = df[features]
    y = df[target]
    categorical_features = ['neighbourhood', 'property_type', 'room_type']
    numerical_features = [col for col in features if col not in categorical_features]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ],
        remainder='passthrough'
    )

    # --- 4. Model Training (Menggunakan SGDRegressor) ---
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', SGDRegressor(random_state=42, max_iter=1000, tol=1e-3))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Training the initial SGD model...")
    model_pipeline.fit(X_train, y_train)
    score = model_pipeline.score(X_test, y_test)
    print(f"Initial model training complete. R^2 Score: {score:.2f}")

    # --- 5. Save Model to MinIO ---
    print("Connecting to MinIO to save the model...")
    try:
        # KONEKSI UNTUK EKSEKUSI LOKAL
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
        joblib.dump(model_pipeline, model_file)
        model_file.seek(0)
        
        client.put_object(
            bucket_name, "price_prediction_model.joblib", data=model_file,
            length=model_file.getbuffer().nbytes, content_type='application/octet-stream'
        )
        print(f"SUCCESS: Initial SGD model saved to MinIO bucket '{bucket_name}'.")
    except Exception as e:
        print(f"FATAL ERROR: Could not connect to MinIO or save model. Details: {e}")

if __name__ == "__main__":
    train_and_save_model()