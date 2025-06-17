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


## Workflow
![image](https://github.com/user-attachments/assets/110265cc-0681-4001-884c-750da6afba18)



## Teknologi yang Digunakan

| Komponen           | Teknologi               |
|--------------------|-------------------------|
| Penyimpanan Data   | MinIO                   |
| Pemrosesan Data    | Pandas, Scikit-learn    |
| Dashboard          | Streamlit               |
| Orkestrasi         | Docker Compose          |
| Model ML           | Scikit-learn + Joblib   |

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
