#!/usr/bin/env python3
"""
Shrimpwatch Setup Script
Script untuk setup otomatis aplikasi Shrimpwatch
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 atau lebih tinggi diperlukan!")
        print(f"   Versi saat ini: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def check_postgresql():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PostgreSQL terdeteksi")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ PostgreSQL tidak ditemukan!")
    print("   Silakan install PostgreSQL terlebih dahulu:")
    print("   - Windows: https://www.postgresql.org/download/windows/")
    print("   - macOS: brew install postgresql")
    print("   - Ubuntu: sudo apt install postgresql postgresql-contrib")
    return False

def create_virtual_environment():
    """Create virtual environment"""
    venv_path = Path("shrimpwatch_env")
    
    if venv_path.exists():
        print("✅ Virtual environment sudah ada")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "shrimpwatch_env"], 
                      check=True)
        print("✅ Virtual environment berhasil dibuat")
        return True
    except subprocess.CalledProcessError:
        print("❌ Gagal membuat virtual environment")
        return False

def get_activation_command():
    """Get the correct activation command based on OS"""
    if platform.system() == "Windows":
        return "shrimpwatch_env\\Scripts\\activate"
    else:
        return "source shrimpwatch_env/bin/activate"

def install_requirements():
    """Install Python requirements"""
    activation_cmd = get_activation_command()
    
    if platform.system() == "Windows":
        pip_cmd = "shrimpwatch_env\\Scripts\\pip"
    else:
        pip_cmd = "shrimpwatch_env/bin/pip"
    
    try:
        print("📦 Installing dependencies...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies berhasil diinstall")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Gagal install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ File .env sudah ada")
        return True
    
    if not env_example.exists():
        print("❌ File env.example tidak ditemukan")
        return False
    
    try:
        # Copy template to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ File .env berhasil dibuat dari template")
        print("   ⚠️  Jangan lupa edit file .env dengan konfigurasi database Anda!")
        return True
    except Exception as e:
        print(f"❌ Gagal membuat file .env: {e}")
        return False

def main():
    """Main setup function"""
    print("🦐 Shrimpwatch Setup Script")
    print("=" * 40)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_postgresql():
        print("\n⚠️  Setup akan dilanjutkan, tapi pastikan PostgreSQL terinstall sebelum menjalankan aplikasi")
    
    # Setup steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_requirements),
        ("Creating environment file", create_env_file),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Setup gagal pada step: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 40)
    print("🎉 Setup berhasil!")
    print("\n📋 Langkah selanjutnya:")
    print("1. Edit file .env dengan konfigurasi database Anda")
    print("2. Setup database PostgreSQL")
    print("3. Download model best.pt (jika belum ada)")
    print("4. Aktifkan virtual environment:")
    print(f"   {get_activation_command()}")
    print("5. Jalankan aplikasi:")
    print("   streamlit run app.py")
    print("\n📖 Lihat INSTALL.md untuk panduan lengkap")

if __name__ == "__main__":
    main()
