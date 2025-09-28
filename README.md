# 🦐 Shrimpwatch - AI-Powered Shrimp Fry Counter

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Shrimpwatch** adalah aplikasi web berbasis AI untuk deteksi dan penghitungan benur udang secara otomatis menggunakan metode Deep Learning. Aplikasi ini dirancang untuk membantu pembudidaya udang dalam memantau populasi benur dengan lebih akurat dan efisien.

## ✨ Fitur Utama

- 🔍 **Deteksi Otomatis**: Menggunakan model AI untuk deteksi benur udang
- 📊 **Analisis Grid**: Membagi gambar menjadi 9 bagian untuk analisis distribusi
- 📈 **Visualisasi Data**: Grafik dan statistik hasil deteksi
- 💾 **Riwayat Deteksi**: Simpan dan kelola hasil deteksi sebelumnya
- 👤 **Sistem User**: Login/registrasi dengan database PostgreSQL
- 📥 **Export Data**: Ekspor hasil ke format CSV
- 🎨 **Interface Modern**: UI yang user-friendly dengan Streamlit

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- 4GB+ RAM

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/fianpraniza/shrimpwatch.git
cd shrimpwatch
```

2. **Setup Environment**
```bash
# Buat virtual environment
python -m venv shrimpwatch_env

# Aktivasi (Windows)
shrimpwatch_env\Scripts\activate
# Aktivasi (macOS/Linux)
source shrimpwatch_env/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Database**
```bash
# Buat database PostgreSQL
createdb shrimpwatch_db

# Setup environment variables
cp env.example .env
# Edit .env dengan konfigurasi database Anda
```

5. **Run Application**
```bash
streamlit run app.py
```

6. **Access Application**
Buka browser dan kunjungi: `http://localhost:8501`

## 📖 Documentation

- [📋 Installation Guide](INSTALL.md) - Panduan instalasi lengkap
- [🔧 Configuration](env.example) - Template konfigurasi environment
- [🐛 Troubleshooting](INSTALL.md#troubleshooting) - Solusi masalah umum

## 🏗️ Architecture

```
shrimpwatch/
├── app.py              # Main Streamlit application
├── config.py           # Authentication & user management
├── database.py         # Database operations
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
├── env.example        # Environment template
├── INSTALL.md         # Installation guide
├── asset/             # Static assets
│   ├── shrimpwatch.png
│   └── results.png
└── best.pt           # AI model (download separately)
```

## 🔒 Security Features

- ✅ Password hashing dengan salt
- ✅ SQL injection protection
- ✅ Environment variables untuk credentials
- ✅ File upload validation
- ✅ Session management

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: PostgreSQL
- **AI/ML**: YOLO (Ultralytics)
- **Image Processing**: OpenCV
- **Visualization**: Plotly

## 📊 Model Information

- **Architecture**: YOLOv8
- **Input Size**: 640x640 pixels
- **Classes**: 1 (Shrimp Fry)
- **Framework**: PyTorch
- **Performance**: Optimized for shrimp fry detection

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Author

**Muhammad Arfian Praniza**
- Email: fianpraniza@gmail.com
- GitHub: [@fianpraniza](https://github.com/fianpraniza)

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com/) untuk YOLO framework
- [Streamlit](https://streamlit.io/) untuk web framework
- [OpenCV](https://opencv.org/) untuk image processing

## 📞 Support

Jika mengalami masalah atau memiliki pertanyaan:

1. 📋 Periksa [Issues](https://github.com/fianpraniza/shrimpwatch/issues)
2. 📧 Email: fianpraniza@gmail.com
3. 💬 Linkedin: [Contact](https://www.linkedin.com/in/fianpraniza/)

---

**Future of Aquaculture - I Believe in the Future** 🦐

*Dikembangkan dengan ❤️ untuk kemajuan budidaya udang Indonesia*