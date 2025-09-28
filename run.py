#!/usr/bin/env python3
"""
Shrimpwatch Runner Script
Script untuk menjalankan aplikasi Shrimpwatch dengan konfigurasi optimal
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ File .env tidak ditemukan!")
        print("   Silakan copy env.example ke .env dan edit konfigurasinya")
        return False
    
    # Check if model exists
    if not Path("best.pt").exists():
        print("⚠️  Model best.pt tidak ditemukan!")
        print("   Aplikasi mungkin tidak berfungsi tanpa model AI")
        print("   Lihat MODEL_SETUP.md untuk panduan download model")
    
    # Check if virtual environment exists
    venv_path = Path("shrimpwatch_env")
    if not venv_path.exists():
        print("❌ Virtual environment tidak ditemukan!")
        print("   Jalankan setup.py terlebih dahulu")
        return False
    
    print("✅ Environment check passed")
    return True

def get_streamlit_command():
    """Get the correct streamlit command based on OS"""
    if platform.system() == "Windows":
        return "shrimpwatch_env\\Scripts\\streamlit"
    else:
        return "shrimpwatch_env/bin/streamlit"

def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting Shrimpwatch...")
    
    streamlit_cmd = get_streamlit_command()
    
    # Set environment variables for optimal performance
    env = os.environ.copy()
    env['STREAMLIT_SERVER_HEADLESS'] = 'true'
    env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    try:
        # Run streamlit with optimized settings
        subprocess.run([
            streamlit_cmd, "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Shrimpwatch stopped by user")
        return True

def main():
    """Main runner function"""
    print("🦐 Shrimpwatch Runner")
    print("=" * 30)
    
    if not check_environment():
        print("\n❌ Environment check failed!")
        print("   Silakan setup environment terlebih dahulu")
        sys.exit(1)
    
    print("\n🌐 Application akan berjalan di: http://localhost:8501")
    print("   Tekan Ctrl+C untuk menghentikan aplikasi")
    print("=" * 30)
    
    run_application()

if __name__ == "__main__":
    main()
