# Gunakan base image Python yang ringan
FROM python:3.9-slim

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# --- TAMBAHAN BARU: Install netcat (nc) ---
# Ini diperlukan untuk memeriksa ketersediaan service lain
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Salin file requirements terlebih dahulu untuk caching layer
COPY requirements.txt requirements.txt

# Install semua dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode proyek ke dalam direktori kerja di container
COPY . .

# CMD akan ditentukan di docker-compose.yml