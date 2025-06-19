import streamlit as st
import pandas as pd
from minio import Minio
import joblib
import io
import os
import requests  # <-- Tambahan baru

# --- Aturan #1: set_page_config() harus menjadi perintah Streamlit pertama ---
st.set_page_config(layout="wide", page_title="Airbnb Price Predictor")


# --- Konfigurasi dan Fungsi ---

@st.cache_resource
def get_model_from_minio():
    """Connects to MinIO and downloads the trained model."""
    try:
        client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
        model_object = client.get_object("models", "price_prediction_model.joblib")
        model_file = io.BytesIO(model_object.read())
        model = joblib.load(model_file)
        return model
    except Exception as e:
        st.error(f"Fatal Error: Could not load model from MinIO. Details: {e}")
        return None

@st.cache_data
def get_unique_values_from_data():
    """Loads the original dataset to get unique values for dropdowns."""
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

# --- TAMBAHAN BARU: Fungsi untuk mengambil kurs dari API ---
@st.cache_data(ttl=3600)  # Cache hasil selama 1 jam (3600 detik)
def get_usd_to_idr_rate():
    """Fetches the latest USD to IDR exchange rate from a free API."""
    try:
        # Menggunakan API gratis dari Frankfurter.app
        response = requests.get("https://api.frankfurter.app/latest?from=USD&to=IDR")
        response.raise_for_status()  # Akan error jika status code bukan 200
        data = response.json()
        rate = data['rates']['IDR']
        return rate
    except Exception as e:
        st.warning(f"Could not fetch live exchange rate: {e}. Using a default rate of 15,500.")
        return 15500.0 # Fallback jika API gagal


# --- Tampilan Utama Aplikasi ---
st.title("🔮 Airbnb Price Predictor")
st.markdown("Enter the details of your listing below to get a predicted daily price.")

# --- Memuat Model, Data Unik, dan Kurs ---
model = get_model_from_minio()
unique_neighbourhoods, unique_property_types, unique_room_types = get_unique_values_from_data()
IDR_RATE = get_usd_to_idr_rate() # <-- Tambahan baru

if model is None or not any(unique_neighbourhoods):
    st.warning("Application cannot start due to fatal errors listed above. Please check your setup.")
else:
    st.success("Model and data loaded successfully. You can now use the predictor.")
    
    with st.form("prediction_form"):
        # ... (FORM INPUT TIDAK BERUBAH, SAMA SEPERTI SEBELUMNYA) ...
        st.header("Listing Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            neighbourhood = st.selectbox("Neighbourhood", options=unique_neighbourhoods)
            property_type = st.selectbox("Property Type", options=unique_property_types)
            room_type = st.selectbox("Room Type", options=unique_room_types)
        with col2:
            accommodates = st.number_input("Accommodates (guests)", min_value=1, max_value=20, value=2, step=1)
            bedrooms = st.number_input("Number of Bedrooms", min_value=0, max_value=10, value=1, step=1)
            review_scores_rating = st.slider("Overall Rating Score (out of 100)", min_value=0, max_value=100, value=95)
        with col3:
            review_scores_cleanliness = st.slider("Cleanliness Score (out of 10)", min_value=0, max_value=10, value=9)
            review_scores_location = st.slider("Location Score (out of 10)", min_value=0, max_value=10, value=9)
            host_total_listings_count = st.number_input("Host's Total Listings", min_value=1, max_value=500, value=1, step=1)
        st.header("Host Details")
        col_host1, col_host2 = st.columns(2)
        with col_host1:
            host_is_superhost_str = st.radio("Is the Host a Superhost?", ('Yes', 'No'))
        with col_host2:
            host_response_rate_pct = st.slider("Host Response Rate (%)", min_value=0, max_value=100, value=100)
        submitted = st.form_submit_button("Predict Price")

    if submitted:
        # ... (BAGIAN PRE-PROCESSING INPUT TIDAK BERUBAH) ...
        input_data = {
            'neighbourhood': [neighbourhood],'property_type': [property_type],'room_type': [room_type],
            'accommodates': [accommodates],'bedrooms': [bedrooms],'review_scores_rating': [review_scores_rating],
            'review_scores_cleanliness': [review_scores_cleanliness],'review_scores_location': [review_scores_location],
            'host_total_listings_count': [host_total_listings_count],'host_is_superhost': [host_is_superhost_str],
            'host_response_rate': [host_response_rate_pct]
        }
        input_df = pd.DataFrame.from_dict(input_data)
        st.write("---")
        st.subheader("Processing Input...")
        input_df['host_is_superhost'] = input_df['host_is_superhost'].apply(lambda x: 1 if x == 'Yes' else 0)
        input_df['host_response_rate'] = input_df['host_response_rate'] / 100.0
        st.write("Cleaned data sent to model:")
        st.dataframe(input_df)

        try:
            # --- PERUBAHAN DI BAGIAN OUTPUT ---
            predicted_price_usd = model.predict(input_df)[0]
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