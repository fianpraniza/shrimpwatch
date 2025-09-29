# 🦐 Shrimpwatch - Panduan Instalasi Lokal

## 📋 Persyaratan Sistem

### Minimum Requirements:
- **Python**: 3.8 atau lebih tinggi
- **RAM**: 4GB (8GB direkomendasikan)
- **Storage**: 2GB ruang kosong
- **OS**: Windows 10/11, macOS 10.15+, atau Linux Ubuntu 18.04+

### Recommended Requirements:
- **Python**: 3.9-3.11
- **RAM**: 8GB atau lebih
- **GPU**: NVIDIA GPU dengan CUDA support (opsional, untuk performa lebih baik)
- **Storage**: 5GB ruang kosong

## 🚀 Langkah-langkah Instalasi

### 1. Persiapan Environment

#### a. Clone Repository
```bash
git clone https://github.com/[username]/shrimpwatch.git
cd shrimpwatch
```

#### b. Buat Virtual Environment
```bash
# Menggunakan venv (direkomendasikan)
python -m venv shrimpwatch_env

# Aktivasi virtual environment
# Windows:
shrimpwatch_env\Scripts\activate
# macOS/Linux:
source shrimpwatch_env/bin/activate
```

### 2. Instalasi Dependencies

#### a. Upgrade pip
```bash
python -m pip install --upgrade pip
```

#### b. Install Requirements
```bash
pip install -r requirements.txt
```

**Catatan**: Jika mengalami error dengan PyTorch, install manual:
```bash
# Untuk CPU only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Untuk CUDA (jika memiliki GPU NVIDIA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. Setup Database

#### a. Install PostgreSQL
- **Windows**: Download dari [postgresql.org](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql`
- **Ubuntu**: `sudo apt install postgresql postgresql-contrib`

#### b. Buat Database
```sql
-- Login ke PostgreSQL
psql -U postgres

-- Buat database
CREATE DATABASE shrimpwatch_db;

-- Buat user (opsional)
CREATE USER shrimpwatch_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE shrimpwatch_db TO shrimpwatch_user;
```

#### c. Konfigurasi Environment
Buat file `.env` di root directory:
```env
# Database Configuration
DB_HOST=localhost
DB_NAME=shrimpwatch_db
DB_USER=shrimpwatch_user
DB_PASSWORD=your_password
DB_PORT=5432
DB_SSLMODE=prefer

# Application Settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### 4. Setup Model AI

#### a. Download Model (jika belum ada)
Pastikan file `best.pt` tersedia di direktori root. Jika tidak ada, Anda perlu:
1. Melatih model sendiri, atau
2. Menggunakan model pre-trained yang tersedia

#### b. Verifikasi Model
```python
# Test script untuk memverifikasi model
python -c "from ultralytics import YOLO; model = YOLO('best.pt'); print('Model loaded successfully!')"
```

### 5. Menjalankan Aplikasi

#### a. Start Database (jika belum running)
```bash
# Windows (jika install sebagai service)
net start postgresql

# macOS
brew services start postgresql

# Ubuntu
sudo systemctl start postgresql
```

#### b. Run Application
```bash
streamlit run app.py
```

#### c. Akses Aplikasi
Buka browser dan kunjungi: `http://localhost:8501`

## 🔧 Troubleshooting

### Error: "Module not found"
```bash
# Pastikan virtual environment aktif
# Windows:
shrimpwatch_env\Scripts\activate
# macOS/Linux:
source shrimpwatch_env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "Database connection failed"
1. Pastikan PostgreSQL running
2. Periksa konfigurasi di `.env`
3. Test koneksi:
```bash
psql -h localhost -U shrimpwatch_user -d shrimpwatch_db
```

### Error: "Model not found"
1. Pastikan file `best.pt` ada di direktori root
2. Periksa permission file
3. Download ulang model jika perlu

### Error: "CUDA out of memory"
```bash
# Gunakan CPU only
export CUDA_VISIBLE_DEVICES=""
streamlit run app.py
```

### Performance Issues
1. **Kurangi ukuran gambar**: Resize gambar sebelum upload
2. **Gunakan CPU**: Jika GPU tidak cukup powerful
3. **Tutup aplikasi lain**: Free up RAM

## 📁 Struktur Direktori

```
shrimpwatch/
├── app.py                 # Main application
├── config.py              # Configuration
├── database.py            # Database operations
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (buat sendiri)
├── .gitignore            # Git ignore rules
├── best.pt               # AI model
├── asset/                # Static assets
│   └── shrimpwatch.png
└── README.md             # Documentation
```

### Best Practices:
1. Selalu gunakan virtual environment
3. Gunakan password yang kuat untuk database
4. Backup database secara berkala

## 📞 Support

Jika mengalami masalah:
1. Periksa [Issues](https://github.com/fianpraniza/shrimpwatch/issues)
2. Buat issue baru dengan detail error
3. Hubungi developer: [email](fianpraniza@gmail.com)

## 📄 License

Proyek ini menggunakan [MIT License](LICENSE).

---

**Happy Shrimp Counting! 🦐**
