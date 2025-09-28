import hashlib
import secrets
from database import Database #
from typing import Tuple, Optional, Dict, Any, List

try:
    db = Database() #
except Exception as e:
    print(f"CRITICAL: Failed to initialize Database in config.py: {e}")
    raise

def hash_password(password: str) -> Tuple[str, str]:
    """Hash password menggunakan SHA-256 dengan salt."""
    salt = secrets.token_hex(16) # Menghasilkan salt 32 karakter hex
    hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed_password, salt

def verify_password(stored_password_hash: str, stored_salt: str, provided_password: str) -> bool:
    """Verifikasi password yang diinput dengan password hash dan salt yang tersimpan."""
    hashed_provided_password = hashlib.sha256((provided_password + stored_salt).encode('utf-8')).hexdigest()
    return hashed_provided_password == stored_password_hash

def register_user(username: str, password: str, email: str, full_name: str) -> Tuple[bool, str]:
    """Mendaftarkan pengguna baru."""
    hashed_pw, salt = hash_password(password)
    return db.register_user(username, hashed_pw, salt, email, full_name) #

def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Mengautentikasi pengguna. Mengembalikan (status, pesan, user_info_dict)."""
    user_credentials = db.get_user_credentials(username) #
    if user_credentials:
        user_id, stored_hash, stored_salt = user_credentials
        if verify_password(stored_hash, stored_salt, password):
            db.update_last_login(user_id) #
            user_info = db.get_user_info_by_id(user_id) #
            return True, "Login berhasil!", user_info
        else:
            return False, "Username atau password salah", None
    return False, "Username atau password salah", None

def get_user_info(username: str) -> Optional[Dict[str, Any]]:
    """Mendapatkan informasi pengguna."""
    return db.get_user_info(username) #

def save_detection(user_id: int, detection_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Menyimpan hasil deteksi."""
    return db.save_detection(user_id, detection_data) #

def get_detection_history(user_id: int) -> List[Dict[str, Any]]:
    """Mendapatkan riwayat deteksi pengguna."""
    return db.get_detection_history(user_id) #

def delete_detection(detection_id: int, user_id: int) -> Tuple[bool, str]:
    """Menghapus hasil deteksi."""
    return db.delete_detection(detection_id, user_id) #

def get_user_settings(user_id: int) -> Optional[Dict[str, Any]]:
    """Mendapatkan pengaturan pengguna."""
    return db.get_user_settings(user_id) #

def update_user_settings(user_id: int, settings: Dict[str, Any]) -> Tuple[bool, str]:
    """Memperbarui pengaturan pengguna."""
    return db.update_user_settings(user_id, settings) #

def update_last_login(user_id: int) -> Tuple[bool, str]:
    """Memperbarui waktu login terakhir pengguna."""
    return db.update_last_login(user_id) #

def clear_last_login(user_id: int) -> Tuple[bool, str]:
    """Menghapus status login pengguna."""
    return db.clear_last_login(user_id) #

def delete_all_detections(user_id: int) -> Tuple[bool, str]:
    """Menghapus semua riwayat deteksi pengguna."""
    return db.delete_all_detections(user_id) #
