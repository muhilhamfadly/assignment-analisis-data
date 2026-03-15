# Bike Sharing Analysis Dashboard ✨

## 📝 Deskripsi
Proyek ini merupakan hasil analisis data pada dataset "Bike Sharing" untuk mengeksplorasi pola penyewaan sepeda. Fokus utama analisis ini adalah memahami bagaimana faktor **Cuaca** dan **Waktu (Jam)** memengaruhi volume penyewaan, serta melakukan segmentasi suhu menggunakan teknik **Binning**.

## 📊 Fitur Utama Dashboard
- **Metrik Utama:** Total penyewaan, rata-rata pengguna registered, dan casual.
- **Analisis Cuaca:** Visualisasi dampak kondisi cuaca terhadap minat penyewa.
- **Pola Jam Sibuk:** Tren penyewaan berdasarkan jam (00:00 - 23:00) untuk melihat pola komuter.
- **Analisis Suhu:** Pengelompokan penyewaan berdasarkan kategori suhu (Cold, Moderate, Warm, Hot).
- **Filter Interaktif:** Pengguna dapat memilih rentang waktu secara spesifik melalui sidebar.

## 📂 Struktur Proyek
```text
submissions
├── dashboard/
│   ├── dashboard.py        # File utama Streamlit
│   └── main_data.csv       # Dataset yang telah dibersihkan
├── data/                   # Folder Dataset
│   ├── day.csv             # Dataset hari
│   └── hour.csv            # Dataset jam
├── notebook.ipynb          # Analisis Data (Wrangling, EDA, Visualisasi)
├── requirements.txt        # Daftar library (dependencies)
└── README.md
└── url.txt
```
## 🛠️ Setup Environment
```
# 1. Masuk ke folder proyek
cd submissions

# 2. Buat virtual environment
python -m venv .venv

# 3. Aktifkan venv
.\.venv\Scripts\activate

# 4. Instal library
pip install -r requirements.txt
```

## 🚀 Menjalankan Dashboard
```
streamlit run dashboard/dashboard.py
```