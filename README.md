# Final Project Big Data - Airbnb Price Prediction
Proyek ini mensimulasikan skenario nyata di mana sebuah platform penyewaan properti seperti Airbnb menghadapi tantangan dalam menentukan harga listing secara optimal. Kami mengusulkan solusi berbasis arsitektur Data Lakehouse dengan menggunakan machine learning dan dashboard interaktif untuk merekomendasikan harga listing secara akurat.

## Anggota Kelompok 5

| No | Nama Anggota        | NRP           |
|----|---------------------|---------------|
| 1. | Chelsea Vania H     | 5027231054    |
| 2. | Salsabila Rahmah    | 5027231056    | 
| 3. | Nayla Raissa A      | 5027231054    |
| 4. | Aisha Ayya R        | 5027231056    | 
| 5. | Aisyah Rahmasari    | 5027231072    |


## Latar Belakang Masalah
Industri: E-commerce / Penyewaan Properti
Masalah: Penentuan harga listing secara manual sering kali tidak akurat, menyebabkan:
- Harga terlalu tinggi → calon penyewa tidak tertarik
- Harga terlalu rendah → potensi kerugian bagi pemilik properti
- Tidak adanya standarisasi penilaian harga berdasarkan fitur properti

## Tujuan Projek
- **Membangun Sistem Prediksi Harga Listing Otomatis:**
Mengembangkan model machine learning berbasis big data untuk memprediksi harga listing properti Airbnb secara akurat dan otomatis.

- **Mengimplementasikan Arsitektur Data Lakehouse:**
Menerapkan arsitektur Lakehouse yang terdiri dari Kafka (streaming ingestion), MinIO (object storage sebagai data lake), dan Apache Spark (untuk analisis dan pemodelan).

- **Menyediakan Alur Pemrosesan Data Terintegrasi:**
Mendesain dan membangun pipeline data streaming dan batch yang mengalirkan data dari dataset mentah ke Kafka, menyimpannya di MinIO, dan memprosesnya di Apache Spark untuk keperluan analisis dan training model.

- **Mengintegrasikan Visualisasi Interaktif untuk End User:**
Menyediakan antarmuka berbasis Streamlit agar pengguna (misalnya pemilik properti) dapat mengakses prediksi harga secara langsung melalui dashboard yang informatif dan mudah digunakan.

- **Meningkatkan Efisiensi dan Akurasi Penentuan Harga:**
Mengatasi masalah penetapan harga manual yang tidak akurat dengan solusi berbasis data yang dapat diskalakan, transparan, dan berbasis fitur properti aktual.


## Dataset
- Nama Dataset: [Airbnb Listings Reviews](https://www.kaggle.com/datasets/mysarahmadbhat/airbnb-listings-reviews)
- Ukuran: 414,32 MB
- Format: CSV
- Usability Score: 9.41
- Deskripsi: Data Airbnb untuk lebih dari 250.000 listing di 10 kota besar, mencakup informasi tentang host, harga, lokasi, dan tipe kamar, serta lebih dari 5 juta ulasan historis.


### Alasan Pemilihan Dataset
- Mencakup lebih dari 250.000 listing Airbnb dari 10 kota besar.
- Memuat informasi penting seperti harga, lokasi, jenis kamar, dan ulasan pengguna.
- Tersedia lebih dari 5 juta data ulasan historis untuk analisis perilaku pengguna.
- Cocok untuk membangun model prediksi harga listing berbasis machine learning.
- Ukuran dan kompleksitas dataset sesuai untuk implementasi arsitektur Big Data (Kafka, MinIO, Spark).
- Dataset bersifat publik dan bebas digunakan untuk keperluan analisis dan pengembangan model.


## Workflow
![image](https://github.com/user-attachments/assets/110265cc-0681-4001-884c-750da6afba18)


## Teknologi yang Digunakan

| **Komponen**            | **Teknologi**               | **Deskripsi Singkat**                                                                                                  |
| ------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Penyimpanan Data    | MinIO                   | Object storage berbasis S3-compatible untuk menyimpan dataset mentah (bronze), hasil olahan (gold), dan model ML. |
| Streaming Data      | Apache Kafka            | Platform streaming terdistribusi untuk menangani aliran data review secara real-time (disimulasikan).              |
| Pemrosesan Data     | Pandas                  | Digunakan untuk manipulasi, pembersihan, dan transformasi data dalam format DataFrame.                           |
| Model ML            | Scikit-learn + Joblib   | Scikit-learn untuk pre-processing dan pelatihan model. Joblib untuk menyimpan/memuat model yang telah dilatih.     |
| Dashboard Interaktif | Streamlit               | Framework Python untuk membangun dan menyajikan antarmuka pengguna (UI) prediktor harga berbasis web.              |
| Orkestrasi Layanan  | Docker, Docker Compose  | Mengelola dan menjalankan semua layanan (Kafka, MinIO, Python scripts, Streamlit) dalam container secara terkoordinasi. |

## Struktur Projek
```
.
├── data/
├── minio_data/ 
├── src/ 
│ ├── dashboard/
│ │   └── app.py
│ ├── data_ingestion/ 
│ │   ├── consumer.py 
│ │   └── producer.py 
│ ├── ml_training/
│ │   └── train_model.py
│ └── processing/ 
│     └── processor.py 
├── .gitignore 
├── docker-compose.yml
├── Dockerfile
├── README.md 
└── requirements.txt
```

## Cara Menjalankan Projek

### 1. Jalankan Docker
```
docker-compose up -d
```

### 2. Install library
```
pip install -r requirements.txt
```

### 3. Akses MinIO Console 
a. Buka di browser http://localhost:9001
b. Login 
c. Buat tiga bucket, bronze, gold, dan medal
![image](https://github.com/user-attachments/assets/0ceba1a2-0392-4a22-b9c0-094af7734325)


### 4. Jalankan Kafka
#### a. Jalankan Producer.py
```
python src/data_ingestion/producer.py
```
![image](https://github.com/user-attachments/assets/87da4b51-19e9-45c1-8e26-7a7f20285d0e)

#### b. Jalankan consumer.py
```
python src/data_ingestion/consumer.py
```
![image](https://github.com/user-attachments/assets/747325ae-32fa-4dea-aef4-c958f861de8f)

#### c. Jalankan processor.py
```
python src/processing/processor.py
```
![image](https://github.com/user-attachments/assets/8ae7adf6-13d6-4aad-a683-d93cddf956f3)


### 5. Train Model
```
python src/ml_training/train_model.py
```
cek apakah ada price_prediction_model.joblib di dalam bucket models
![image](https://github.com/user-attachments/assets/2e714201-a225-4c25-9d16-a65a20383742)


### Jalankan Streamlit
```
streamlit run src/dashboard/app.py 
```
![image](https://github.com/user-attachments/assets/c917fd56-0811-44c0-ba4b-daeaf0e95d45)


## Manfaat yang Didapat
- Prediksi harga listing yang lebih adil dan berbasis data
- Dashboard interaktif untuk pemilik properti atau analis harga
- Demonstrasi penggunaan Data Lakehouse dalam implementasi nyata
