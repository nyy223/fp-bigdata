# src/dashboard/app.py (disederhanakan: hilangkan beberapa fitur dari UI)

import streamlit as st
import pandas as pd
from minio import Minio
import joblib
import io
import os
import requests
import numpy as np

st.set_page_config(layout="wide", page_title="Airbnb Price Predictor")

@st.cache_data(ttl=3600)
def get_model_from_minio():
    st.info("Fetching the latest model from storage...")
    try:
        client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
        model_object = client.get_object("models", "price_prediction_model.joblib")
        model_file = io.BytesIO(model_object.read())
        model = joblib.load(model_file)
        st.success("Latest model loaded successfully!")
        return model
    except Exception as e:
        st.error(f"Fatal Error: Could not load model from MinIO. Details: {e}")
        return None

@st.cache_data
def get_unique_values_from_data():
    try:
        script_dir = os.path.dirname(__file__)
        project_root = os.path.join(script_dir, '..', '..')
        file_path = os.path.join(project_root, 'data', 'Listings.csv')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at the constructed path: {file_path}")
        df = pd.read_csv(file_path, low_memory=False, encoding='latin-1')
        unique_neighbourhoods = sorted(df['neighbourhood'].dropna().unique())
        unique_property_types = sorted(df['property_type'].dropna().unique())
        unique_room_types = sorted(df['room_type'].dropna().unique())
        return unique_neighbourhoods, unique_property_types, unique_room_types
    except FileNotFoundError as e:
        st.error(f"Fatal Error: {e}. Cannot populate dropdown menus.")
        return [], [], []

@st.cache_data(ttl=3600)
def get_usd_to_idr_rate():
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=USD&to=IDR")
        response.raise_for_status()
        data = response.json()
        rate = data['rates']['IDR']
        return rate
    except Exception as e:
        st.warning(f"Could not fetch live exchange rate: {e}. Using a default rate of 15,500.")
        return 15500.0

st.title("🔮 Airbnb Price Predictor")
st.markdown("Enter the details of your listing below to get a predicted daily price.")

model = get_model_from_minio()
unique_neighbourhoods, unique_property_types, unique_room_types = get_unique_values_from_data()
IDR_RATE = get_usd_to_idr_rate()

if model is None or not any(unique_neighbourhoods):
    st.warning("Application cannot start due to fatal errors listed above. Please check your setup.")
else:
    st.success("Model and data loaded successfully. You can now use the predictor.")

    with st.form("prediction_form"):
        st.header("Listing Details")
        col1, col2 = st.columns(2)
        with col1:
            neighbourhood = st.selectbox("Neighbourhood", options=unique_neighbourhoods)
            property_type = st.selectbox("Property Type", options=unique_property_types)
            room_type = st.selectbox("Room Type", options=unique_room_types)
        with col2:
            accommodates = st.number_input("Accommodates (guests)", min_value=1, max_value=20, value=2, step=1)
            bedrooms = st.number_input("Number of Bedrooms", min_value=0, max_value=10, value=1, step=1)
            review_scores_rating = st.slider("Overall Rating Score (out of 100)", min_value=0, max_value=100, value=95)
            host_total_listings_count = st.number_input("Host's Total Listings", min_value=1, max_value=500, value=1, step=1)
        submitted = st.form_submit_button("Predict Price")

    if submitted:
        input_data = {
            'neighbourhood': [neighbourhood],'property_type': [property_type],'room_type': [room_type],
            'accommodates': [accommodates],'bedrooms': [bedrooms],'review_scores_rating': [review_scores_rating],
            'host_total_listings_count': [host_total_listings_count],
            # default values for removed fields
            'host_is_superhost': [0],
            'host_response_rate': [1.0],
            'review_scores_cleanliness': [8.0],
            'review_scores_location': [8.0]
        }
        input_df = pd.DataFrame.from_dict(input_data)
        st.write("---")
        st.subheader("Processing Input...")
        st.write("Cleaned data sent to model:")
        st.dataframe(input_df)

        try:
            predicted_price_log = model.predict(input_df)[0]
            predicted_price_usd = np.expm1(predicted_price_log)
            predicted_price_usd = max(0, predicted_price_usd)
            predicted_price_idr = predicted_price_usd * IDR_RATE

            st.subheader("🥁 Prediction Result")
            st.success(f"**The recommended daily price for your listing is:**")

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric(label="Predicted Price (USD)", value=f"${predicted_price_usd:,.2f}")
            with col_res2:
                st.metric(label="Predicted Price (IDR)", value=f"Rp {predicted_price_idr:,.0f}")

        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")
