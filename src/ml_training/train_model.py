import pandas as pd
from minio import Minio
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import io
import os

def train_and_save_model():
    """Trains a price prediction model and saves it to MinIO."""
    # --- 1. Load Data ---
    file_path = os.path.join('data', 'Listings.csv')
    try:
        # Fixed: Added encoding='latin-1' to handle UnicodeDecodeError
        df = pd.read_csv(file_path, low_memory=False, encoding='latin-1')
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return
        
    print("Data loaded successfully.")

    # --- 2. Feature Selection & Initial Cleaning ---
    features = [
        'host_response_rate', 'host_is_superhost', 'host_total_listings_count',
        'neighbourhood', 'property_type', 'room_type', 'accommodates',
        'bedrooms', 'review_scores_rating', 'review_scores_cleanliness',
        'review_scores_location'
    ]
    target = 'price'
    
    # Select only the columns we need to work with
    df = df[features + [target]]

    # --- Data Cleaning (Column by Column) ---
    
    # Clean price column (e.g., "$1,500.00" -> 1500.0)
    # Using raw string r'\$' to avoid SyntaxWarning
    df['price'] = df['price'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
    
    # Clean host_response_rate (e.g., "95%" -> 0.95)
    # Fixed: Convert the column to string type first to ensure .str accessor works
    df['host_response_rate'] = df['host_response_rate'].astype(str).str.replace('%', '').astype(float) / 100
    
    # Convert boolean host_is_superhost (handle potential NaNs)
    df['host_is_superhost'] = df['host_is_superhost'].apply(lambda x: 1 if x == 't' else 0)
    
    # Now that cleaning is done, drop any rows with remaining NaNs in our feature/target columns
    df.dropna(subset=features + [target], inplace=True)
    
    print("Data cleaning and feature selection complete.")

    # --- 3. Preprocessing ---
    X = df[features]
    y = df[target]

    categorical_features = ['neighbourhood', 'property_type', 'room_type']
    numerical_features = [col for col in features if col not in categorical_features]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ],
        remainder='passthrough' # Keep other columns if any, good practice
    )

    # --- 4. Model Training ---
    # Create a pipeline that preprocesses the data and then trains the model
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training the model...")
    model_pipeline.fit(X_train, y_train)
    
    score = model_pipeline.score(X_test, y_test)
    print(f"Model training complete. R^2 Score: {score:.2f}")

    # --- 5. Save Model to MinIO ---
    client = Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
    bucket_name = "models"
    
    # Ensure bucket exists
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    
    # Save the entire pipeline (preprocessor + model)
    model_file = io.BytesIO()
    joblib.dump(model_pipeline, model_file)
    model_file.seek(0)
    
    client.put_object(
        bucket_name,
        "price_prediction_model.joblib",
        data=model_file,
        length=model_file.getbuffer().nbytes,
        content_type='application/octet-stream'
    )
    print(f"Model 'price_prediction_model.joblib' saved to MinIO bucket '{bucket_name}'.")

if __name__ == "__main__":
    train_and_save_model()