# ⚡ Quick Start Guide - Shrimpwatch

## 🚀 Instalasi Cepat (5 Menit)

### 1. Clone Repository
```bash
git clone https://github.com/[username]/shrimpwatch.git
cd shrimpwatch
```

### 2. Setup Otomatis
```bash
# Jalankan setup script
python setup.py

# Atau manual:
python -m venv shrimpwatch_env
# Windows: shrimpwatch_env\Scripts\activate
# macOS/Linux: source shrimpwatch_env/bin/activate
pip install -r requirements.txt
```

### 3. Konfigurasi Database
```bash
# Copy environment template
cp env.example .env

# Edit .env dengan konfigurasi database Anda
# Database: PostgreSQL
# Host: localhost
# Port: 5432
# Database: shrimpwatch_db
# User: your_username
# Password: your_password
```

### 4. Setup Database
```bash
# Jalankan database setup
python database_setup.py
```

### 5. Download Model (jika belum ada)
```bash
# Download model AI (ganti URL dengan link model Anda)
# wget https://your-model-url.com/best.pt
# Atau copy model file ke direktori ini
```

### 6. Jalankan Aplikasi
```bash
# Menggunakan script runner
python run.py

# Atau langsung
streamlit run app.py
```

### 7. Akses Aplikasi
Buka browser: `http://localhost:8501`

## 🔧 Troubleshooting Cepat

### Error: "Module not found"
```bash
# Pastikan virtual environment aktif
source shrimpwatch_env/bin/activate  # macOS/Linux
shrimpwatch_env\Scripts\activate    # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "Database connection failed"
```bash
# Pastikan PostgreSQL running
# Windows: net start postgresql
# macOS: brew services start postgresql
# Ubuntu: sudo systemctl start postgresql

# Test koneksi
psql -h localhost -U your_username -d shrimpwatch_db
```

### Error: "Model not found"
```bash
# Pastikan file best.pt ada
ls -la best.pt

# Download model jika belum ada
# Lihat MODEL_SETUP.md untuk panduan lengkap
```

## 📋 Requirements Minimal

- **Python**: 3.8+
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB
- **Database**: PostgreSQL
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

## 🎯 Fitur Utama

- 🔍 **Deteksi AI**: Otomatis deteksi benur udang
- 📊 **Analisis Grid**: 9 bagian untuk analisis distribusi
- 📈 **Visualisasi**: Grafik dan statistik
- 💾 **Riwayat**: Simpan hasil deteksi
- 👤 **User System**: Login/registrasi
- 📥 **Export**: Download hasil ke CSV

## 🚨 Common Issues

### 1. "CUDA out of memory"
```bash
# Gunakan CPU only
export CUDA_VISIBLE_DEVICES=""
streamlit run app.py
```

### 2. "Permission denied"
```bash
# Fix permission
chmod +x setup.py run.py database_setup.py
```

### 3. "Port already in use"
```bash
# Gunakan port lain
streamlit run app.py --server.port 8502
```

## 📞 Support

- 📧 Email: fianpraniza@gmail.com
- 💬 WhatsApp: [Contact](http://wa.me/+6281259676839)
- 🐛 Issues: [GitHub Issues](https://github.com/[username]/shrimpwatch/issues)

## 📚 Dokumentasi Lengkap

- [📋 Installation Guide](INSTALL.md) - Panduan instalasi detail
- [🤖 Model Setup](MODEL_SETUP.md) - Setup model AI
- [🔒 Security Guide](SECURITY.md) - Keamanan aplikasi
- [🚀 GitHub Setup](github_setup.md) - Setup repository

---

**Happy Shrimp Counting! 🦐**

*Dikembangkan dengan ❤️ untuk kemajuan budidaya udang Indonesia*
