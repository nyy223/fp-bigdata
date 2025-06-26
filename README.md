# Final Project Big Data - Airbnb Price Prediction
Proyek ini mensimulasikan skenario nyata di mana sebuah platform penyewaan properti seperti Airbnb menghadapi tantangan dalam menentukan harga listing secara optimal. Kami mengusulkan solusi berbasis arsitektur Data Lakehouse dengan menggunakan machine learning dan dashboard interaktif untuk merekomendasikan harga listing secara akurat.

## Anggota Kelompok 5

| No | Nama Anggota        | NRP           |
|----|---------------------|---------------|
| 1. | Chelsea Vania H.    | 5027231003    |
| 2. | Salsabila Rahmah    | 5027231005    | 
| 3. | Nayla Raissa A      | 5027231054    |
| 4. | Aisha Ayya R.       | 5027231056    | 
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


## Arsitektur
<img width="602" alt="Screenshot 2025-06-19 at 21 38 10" src="https://github.com/user-attachments/assets/7513610a-5e01-47de-a387-25f7ba7d8d8d" />

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

## Workflow
### 1. Training Model
`src/ml_training/train_model.py`
- Input: Listings.csv (250.000 baris pertama)
- Proses:
  - Membersihkan & mempersiapkan data listing
  - Melatih RandomForestRegressor dalam sebuah Pipeline
- Output: price_prediction_model.joblib
- Disimpan di: Bucket models (MinIO)
### 2. Streaming Data **Review**
**a. Producer**
`src/data_ingestion/producer.py`
- Input: Reviews.csv (15.000 ulasan pertama)
- Proses: Mengirim ulasan ke Kafka (airbnb-reviews) secara bertahap
- Output: Aliran pesan Kafka
  
**b. Consumer**
`src/data_ingestion/consumer.py`
- Input: Kafka (airbnb-reviews)
- Proses: Menyimpan setiap pesan ke file JSON
- Output: File JSON
- Disimpan di: Bucket bronze (MinIO)
### 3. Processing & Prediction
`src/processing/processor.py`
- Input:
  - File JSON dari bucket bronze
  - Model dari models
  - Lookup ke Listings.csv
- Proses:
  - Menggabungkan ulasan + data listing
  - Prediksi harga dengan model
- Output: File JSON terstruktur
- Disimpan di: Bucket gold (MinIO)
### 4. Interactive Dashboard
`src/dashboard/app.py`
- Input:
  - Model terlatih (models)
  - Input pengguna (via form web)
- Proses:
  - Prediksi harga berdasarkan input
  - Konversi USD → IDR
- Output: Tampilan harga prediksi di web
  
## Cara Menjalankan Projek
Pastikan **Docker** dan **Docker Compose** sudah terinstal di perangkat Anda.
### 1. Clone Repositori 
```
git clone https://github.com/nyy223/fp-bigdata.git
cd fp-bigdata
```
### 2. Jalankan Docker
```
docker-compose up --build
```
### 3. Akses Dashboard dan MinIO
Setelah semua container aktif:
- Dashboard Prediksi: `http://localhost:8501`
  
  Dashboard ini memungkinkan pengguna memasukkan atribut-atribut properti Airbnb untuk memprediksi harga sewa harian. Input dibagi dalam dua kategori utama:

   **🏠 Bagian 1: Listing Details**
   Fokus pada karakteristik properti yang disewakan.
  | Parameter               | Tipe Input      | Deskripsi                                                                                  |
  |-------------------------|-----------------|---------------------------------------------------------------------------------------------|
  | Neighbourhood           | Dropdown        | Lokasi properti. Harga sangat bergantung pada area. Model belajar pola per lingkungan.     |
  | Property Type           | Dropdown        | Jenis properti (Apartment, House, Barn, dll). Mempengaruhi nilai dan harga sewa.           |
  | Room Type               | Dropdown        | Jenis ruang: Entire place (mahal), Private room, Shared room (murah).                      |
  | Accommodates            | Numeric (±)     | Jumlah maksimal tamu. Semakin banyak kapasitas → harga makin tinggi.                       |
  | Number of Bedrooms      | Numeric (±)     | Jumlah kamar tidur yang tersedia. Menunjukkan ukuran dan kapasitas properti.               |
  | Overall Rating (0–100)  | Slider          | Skor ulasan keseluruhan dari tamu. Skor tinggi → harga bisa premium.                       |
  | Cleanliness Score (0–10)| Slider          | Seberapa bersih properti dinilai oleh tamu. Faktor penting untuk penilaian kualitas.       |
  | Location Score (0–10)   | Slider          | Penilaian lokasi (akses, keamanan, kedekatan wisata). Skor tinggi → harga naik.            |
  | Host’s Total Listings   | Numeric (±)     | Jumlah properti yang dikelola host. Lebih banyak → lebih profesional.                      |

  **👤 Bagian 2: Host Details**
  | Parameter                 | Tipe Input           | Deskripsi                                                                                  |
  |---------------------------|----------------------|---------------------------------------------------------------------------------------------|
  | Is the Host a Superhost?  | Radio Button (Yes/No)| Status Superhost menunjukkan host berkualitas tinggi. Meningkatkan kepercayaan & harga.    |
  | Host Response Rate (%)    | Slider (0–100%)      | Persentase respon terhadap calon tamu. Responsif → diasumsikan lebih profesional.          |

  ![image](https://github.com/user-attachments/assets/c917fd56-0811-44c0-ba4b-daeaf0e95d45)

  **🔘 Tombol Predict Price**

  Setelah semua input dimasukkan, klik tombol ini untuk mengirim data ke model ML dan mendapatkan prediksi harga sewa harian dalam USD dan IDR.
  <img width="1337" alt="Screenshot 2025-06-19 at 20 14 46" src="https://github.com/user-attachments/assets/bc03cba6-e86e-419c-9d68-16bb72880853" />

- MinIO Console: `http://localhost:9001`
> Login: minioadmin / minioadmin

![image](https://github.com/user-attachments/assets/2e714201-a225-4c25-9d16-a65a20383742)

### 4. Hentikan Projek
Tekan Ctrl + C untuk menghentikan proyek. Jika ingin memulai kembali,

`docker-compose up`

Untuk mengehentikan dan menghapus container serta menghapus seluruh data, 

`docker-compose down -v`

## Manfaat yang Didapat
- Prediksi harga listing yang lebih adil dan berbasis data
- Dashboard interaktif untuk pemilik properti atau analis harga
- Demonstrasi penggunaan Data Lakehouse dalam implementasi nyata
