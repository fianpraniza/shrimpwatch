# 🤖 Model AI Setup Guide

## 📋 Informasi Model

Shrimpwatch menggunakan model YOLO (You Only Look Once) yang telah dilatih khusus untuk deteksi benur udang vannamei.

### Spesifikasi Model:
- **Arsitektur**: YOLOv8
- **Input Size**: 640x640 pixels
- **Classes**: 1 (Shrimp Fry)
- **Framework**: PyTorch
- **File Format**: .pt (PyTorch model)

## 🔒 Keamanan Model

### Opsi 1: Model Terbuka (Recommended untuk Open Source)
Jika model Anda dapat dibagikan secara publik:
```bash
# Model akan di-commit ke repository
git add best.pt
git commit -m "Add trained model"
```

### Opsi 2: Model Privat (Untuk Model Proprietary)
Jika model mengandung data sensitif atau proprietary:

1. **Tambahkan ke .gitignore**:
```gitignore
# Model files (uncomment jika model proprietary)
*.pt
*.pth
*.h5
*.pkl
```

2. **Buat script download**:
```python
# download_model.py
import requests
import os

def download_model():
    model_url = "YOUR_MODEL_DOWNLOAD_URL"
    model_path = "best.pt"
    
    if not os.path.exists(model_path):
        print("Downloading model...")
        response = requests.get(model_url)
        with open(model_path, 'wb') as f:
            f.write(response.content)
        print("Model downloaded successfully!")
    else:
        print("Model already exists!")

if __name__ == "__main__":
    download_model()
```

3. **Update INSTALL.md**:
Tambahkan langkah download model di panduan instalasi.

## 🚀 Setup Model

### Langkah 1: Verifikasi Model
```python
# test_model.py
from ultralytics import YOLO
import os

def test_model():
    model_path = "best.pt"
    
    if not os.path.exists(model_path):
        print("❌ Model file tidak ditemukan!")
        print("   Pastikan file best.pt ada di direktori root")
        return False
    
    try:
        model = YOLO(model_path)
        print("✅ Model berhasil dimuat!")
        print(f"   Model info: {model.model}")
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

if __name__ == "__main__":
    test_model()
```

### Langkah 2: Test Model dengan Gambar
```python
# test_detection.py
from ultralytics import YOLO
import cv2
import numpy as np

def test_detection():
    model = YOLO("best.pt")
    
    # Test dengan gambar dummy
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    
    try:
        results = model(dummy_image)
        print("✅ Model detection test berhasil!")
        return True
    except Exception as e:
        print(f"❌ Detection test gagal: {e}")
        return False

if __name__ == "__main__":
    test_detection()
```

## 📊 Model Performance

### Metrik Evaluasi:
- **Precision**: 84.4%
- **Recall**: 71%
- **mAP@0.5**: 80.5%
- **mAP@0.5:0.95**: 50%

### Optimasi Model:
1. **Confidence Threshold**: 0.23 (default)
2. **NMS Threshold**: 0.45
3. **Input Size**: 640x640

## 🔧 Troubleshooting Model

### Error: "Model not found"
```bash
# Pastikan file ada
ls -la best.pt

# Check permission
chmod 644 best.pt
```

### Error: "CUDA out of memory"
```python
# Gunakan CPU only
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

### Error: "Model loading failed"
```python
# Test model integrity
import torch
model = torch.load('best.pt', map_location='cpu')
print("Model structure:", model.keys())
```

## 📁 Model Management

### Backup Model:
```bash
# Backup model
cp best.pt backup/best_$(date +%Y%m%d).pt

# Compress model
tar -czf model_backup.tar.gz best.pt
```

### Model Versioning:
```bash
# Version control untuk model
git tag -a v1.0-model -m "Model version 1.0"
git push origin v1.0-model
```

## 🚀 Production Deployment

### Model Optimization:
```python
# Optimize model untuk production
from ultralytics import YOLO

model = YOLO("best.pt")
model.export(format="onnx")  # Export ke ONNX untuk performa lebih baik
```

### Model Monitoring:
```python
# Monitor model performance
import time

def benchmark_model():
    model = YOLO("best.pt")
    
    # Test inference time
    start_time = time.time()
    results = model("test_image.jpg")
    inference_time = time.time() - start_time
    
    print(f"Inference time: {inference_time:.3f}s")
```

## 📞 Support

Jika mengalami masalah dengan model:
1. Periksa file model ada dan tidak corrupt
2. Test dengan gambar yang berbeda
3. Check system requirements (RAM, GPU)
4. Hubungi developer untuk support

---

**Model AI yang Powerful untuk Deteksi Benur Udang! 🦐**
