# 📦 ETL Pipeline: Submission Ferdinanta

Proyek ini adalah implementasi ETL (Extract, Transform, Load) pipeline menggunakan Python untuk submission tugas. Pipeline ini mengambil data produk (melalui scraping), membersihkan dan mentransformasinya, lalu menyimpan hasilnya ke beberapa target: file CSV, database PostgreSQL, dan Google Sheets.

---

## 🚀 Fitur Utama

- ✅ Ekstraksi data otomatis (`extract.py`)
- 🔁 Transformasi & pembersihan data (`transform.py`)
- 💾 Penyimpanan multi-target:
  - File CSV (`output.csv`, `products.csv`)
  - Database PostgreSQL
  - Google Sheets (menggunakan Google API Service Account)
- 🧪 Unit testing lengkap dengan `pytest`
- 📊 Laporan coverage test menggunakan `pytest-cov`
- 📈 Notebook analisis singkat data (`analisis_data_scraping.ipynb`)

---

## 🛠️ Instalasi

1. **Clone repository:**
   ```bash
   git clone https://github.com/ferdinann/Data_Pipeline.git
   cd submission-ferdinan

2. **Buat virtual environment & aktifkan:**
   ```bash
   python -m venv .env
   source .env/bin/activate  # Linux/macOS
   .\.env\Scripts\activate   # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧾 Konfigurasi Database PostgreSQL

### 1. Buat Database dan User (via terminal `psql`):

```sql
-- Masuk sebagai user postgres
psql -U postgres

-- Buat database
CREATE DATABASE etl_db;

-- Buat user khusus ETL
CREATE USER etl_user WITH PASSWORD '12345678';

-- Beri akses penuh ke database
GRANT ALL PRIVILEGES ON DATABASE etl_db TO etl_user;

-- Beri hak CREATE di schema public
\c etl_db
GRANT USAGE, CREATE ON SCHEMA public TO etl_user;

--  Beri hak default untuk SELECT, INSERT, dll
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO etl_user;
```

### 2. Tambahkan URL koneksi di `.env`:

```env
POSTGRES_URL=postgresql://etl_user:12345678@localhost:5432/etl_db
```

---

## 🧭 Google Sheets Setup

1. Buat service account dari [Google Cloud Console](https://console.cloud.google.com/)
2. Unduh file credential JSON dan simpan sebagai `google-sheets-api.json`
3. Share spreadsheet ke email service account
4. Tambahkan ke `.env`:

```env
GOOGLE_SHEET_ID=your_spreadsheet_id
GOOGLE_SHEET_JSON_KEY=google-sheets-api.json
```

---

## ▶️ Menjalankan ETL Pipeline

```bash
python main.py
```

---

## 🧪 Menjalankan Test

```bash
pytest -v
```

### Dengan Coverage:
```bash
pytest --cov=utils --cov-report=term-missing tests/
```


## 🧱 Struktur Proyek

```
submission-ferdinan/
├── utils/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── analis_data_scraping.ipynb       
├── main.py                          
├── products.csv                      
├── output.csv                        
├── google-sheets-apijson           
├── requirements.txt
├── submission.txt
├── scraper.log                     
├── README.md
```
