import psycopg2
from psycopg2 import pool
from datetime import datetime, timezone
import os
import pandas as pd
from dotenv import load_dotenv
from typing import Any, Tuple, Dict, List, Optional

# Load environment variables
load_dotenv()

class Database:
    def __init__(self) -> None:
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv('DB_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT', 5432),
                sslmode=os.getenv('DB_SSLMODE', 'require') # Default to 'require', allow override
            )
            self.initialize_database()
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    def connect(self) -> Any:
        """Mendapatkan koneksi dari pool"""
        return self.connection_pool.getconn()

    def close(self, conn: Any) -> None:
        """Mengembalikan koneksi ke pool"""
        self.connection_pool.putconn(conn)

    def initialize_database(self) -> None:
        """Membuat tabel-tabel yang diperlukan jika belum ada"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                # Tabel Users
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    salt VARCHAR(32) NOT NULL, 
                    email VARCHAR(100) UNIQUE NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
                ''')

                # Tabel Detection History
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS detection_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_count INTEGER,
                    counts_per_part TEXT,
                    file_name VARCHAR(255),
                    average_count REAL,
                    max_count INTEGER,
                    max_part_index INTEGER,
                    min_count INTEGER,
                    min_part_index INTEGER
                )
                ''')

                # Tabel User Settings
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    theme VARCHAR(20) DEFAULT 'light',
                    language VARCHAR(10) DEFAULT 'id',
                    notification_enabled BOOLEAN DEFAULT TRUE
                )
                ''')
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error initializing database: {str(e)}")
            raise
        finally:
            self.close(conn)

    def register_user(self, username: str, password_hash: str, salt: str, email: str, full_name: str) -> Tuple[bool, str]:
        """Mendaftarkan pengguna baru dengan password hash dan salt yang sudah dienkripsi"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                INSERT INTO users (username, password, salt, email, full_name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                ''', (username, password_hash, salt, email, full_name))
                
                user_id = cursor.fetchone()[0]
                
                cursor.execute('''
                INSERT INTO user_settings (user_id)
                VALUES (%s)
                ''', (user_id,))
                
                conn.commit()
                return True, "Registrasi berhasil!"
        except psycopg2.IntegrityError as e:
            conn.rollback()
            if "users_username_key" in str(e).lower(): # Check constraint name for username
                return False, "Username sudah digunakan"
            elif "users_email_key" in str(e).lower(): # Check constraint name for email
                return False, "Email sudah digunakan"
            return False, f"Terjadi kesalahan integritas data saat registrasi: {str(e)}"
        except Exception as e:
            conn.rollback()
            return False, f"Error saat registrasi pengguna: {str(e)}"
        finally:
            self.close(conn)

    def get_user_credentials(self, username: str) -> Optional[Tuple[int, str, str]]:
        """Mengambil id, password hash, dan salt pengguna untuk otentikasi"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT id, password, salt 
                FROM users 
                WHERE username = %s AND is_active = TRUE
                ''', (username,))
                user_credentials = cursor.fetchone()
                if user_credentials:
                    return user_credentials[0], user_credentials[1], user_credentials[2]
                return None
        except Exception as e:
            print(f"Error getting user credentials: {str(e)}")
            return None
        finally:
            self.close(conn)

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Mendapatkan informasi pengguna berdasarkan username"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT id, username, email, full_name, created_at, last_login
                FROM users
                WHERE username = %s
                ''', (username,))
                
                user = cursor.fetchone()
                if user:
                    return {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'full_name': user[3],
                        'created_at': user[4].isoformat() if user[4] else None,
                        'last_login': user[5].isoformat() if user[5] else None
                    }
                return None
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return None
        finally:
            self.close(conn)

    def get_user_info_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Mendapatkan informasi pengguna berdasarkan ID"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT id, username, email, full_name, created_at, last_login
                FROM users
                WHERE id = %s
                ''', (user_id,))
                user = cursor.fetchone()
                if user:
                    return {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'full_name': user[3],
                        'created_at': user[4].isoformat() if user[4] else None,
                        'last_login': user[5].isoformat() if user[5] else None
                    }
                return None
        except Exception as e:
            print(f"Error getting user info by ID: {str(e)}")
            return None
        finally:
            self.close(conn)

    def save_detection(self, user_id: int, detection_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Menyimpan hasil deteksi"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                counts_per_part_list = detection_data.get('counts_per_part', [])
                if isinstance(counts_per_part_list, list):
                    counts_per_part_str = ','.join(map(str, counts_per_part_list))
                else:
                    counts_per_part_str = str(counts_per_part_list)

                provided_timestamp = detection_data.get('timestamp')

                if not isinstance(provided_timestamp, datetime):
                    print("Peringatan: Timestamp tidak valid atau tidak ada dalam detection_data, menggunakan default database.")
                    sql_insert_timestamp_column = ""
                    sql_insert_timestamp_value_placeholder = ""
                    params_timestamp_value = []
                else:
                    utc_timestamp_aware = provided_timestamp.astimezone(timezone.utc)
                    utc_timestamp_naive_to_store = utc_timestamp_aware.replace(tzinfo=None)

                    sql_insert_timestamp_column = ", timestamp"
                    sql_insert_timestamp_value_placeholder = ", %s"
                    params_timestamp_value = [utc_timestamp_naive_to_store]

                sql = f'''
                INSERT INTO detection_history (
                    user_id, total_count, counts_per_part, file_name,
                    average_count, max_count, max_part_index,
                    min_count, min_part_index{sql_insert_timestamp_column}
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s{sql_insert_timestamp_value_placeholder})
                '''

                params = [
                    user_id,
                    detection_data.get('total_count'),
                    counts_per_part_str,
                    detection_data.get('file_name'),
                    detection_data.get('average_count'),
                    detection_data.get('max_count'),
                    detection_data.get('max_part_index'),
                    detection_data.get('min_count'),
                    detection_data.get('min_part_index')
                ]
                params.extend(params_timestamp_value)

                cursor.execute(sql, tuple(params))
                conn.commit()
                return True, "Hasil deteksi berhasil disimpan"
        except Exception as e:
            conn.rollback()
            print(f"Error saat menyimpan deteksi: {str(e)}") # Cetak error untuk debugging
            return False, f"Error saat menyimpan deteksi: {str(e)}"
        finally:
            self.close(conn)

    def get_detection_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Mendapatkan riwayat deteksi pengguna"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT * FROM detection_history
                WHERE user_id = %s
                ORDER BY timestamp DESC
                ''', (user_id,))
                
                columns = [desc[0] for desc in cursor.description]
                detections: List[Dict[str, Any]] = []
                
                for row in cursor.fetchall():
                    detection = dict(zip(columns, row))
                    if detection.get('counts_per_part') and isinstance(detection['counts_per_part'], str):
                        detection['counts_per_part'] = list(map(int, detection['counts_per_part'].split(',')))
                    else:
                        detection['counts_per_part'] = [] # Default to empty list if malformed or missing
                    
                    if isinstance(detection.get('timestamp'), str):
                        detection['timestamp'] = datetime.fromisoformat(detection['timestamp'])
                    elif not isinstance(detection.get('timestamp'), datetime):
                         detection['timestamp'] = datetime.now()

                    detections.append(detection)
                return detections
        except Exception as e:
            print(f"Error getting detection history: {str(e)}")
            return []
        finally:
            self.close(conn)

    def delete_detection(self, detection_id: int, user_id: int) -> Tuple[bool, str]:
        """Menghapus hasil deteksi"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                DELETE FROM detection_history
                WHERE id = %s AND user_id = %s
                ''', (detection_id, user_id))
                conn.commit()
                if cursor.rowcount == 0:
                    return False, "Data deteksi tidak ditemukan atau Anda tidak memiliki izin untuk menghapusnya."
                return True, "Hasil deteksi berhasil dihapus"
        except Exception as e:
            conn.rollback()
            return False, f"Error saat menghapus deteksi: {str(e)}"
        finally:
            self.close(conn)

    def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Mendapatkan pengaturan pengguna"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                SELECT theme, language, notification_enabled
                FROM user_settings
                WHERE user_id = %s
                ''', (user_id,))
                settings = cursor.fetchone()
                if settings:
                    return {
                        'theme': settings[0],
                        'language': settings[1],
                        'notification_enabled': bool(settings[2])
                    }
                return None # Or return default settings
        except Exception as e:
            print(f"Error getting user settings: {str(e)}")
            return None # Or raise
        finally:
            self.close(conn)

    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Memperbarui pengaturan pengguna"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                UPDATE user_settings
                SET theme = %s, language = %s, notification_enabled = %s
                WHERE user_id = %s
                ''', (
                    settings.get('theme', 'light'),
                    settings.get('language', 'id'),
                    settings.get('notification_enabled', True),
                    user_id
                ))
                conn.commit()
                return True, "Pengaturan berhasil diperbarui"
        except Exception as e:
            conn.rollback()
            return False, f"Error saat memperbarui pengaturan: {str(e)}"
        finally:
            self.close(conn)

    def update_last_login(self, user_id: int) -> Tuple[bool, str]:
        """Memperbarui waktu login terakhir pengguna"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = %s
                ''', (user_id,))
                conn.commit()
                return True, "Status login berhasil diperbarui"
        except Exception as e:
            conn.rollback()
            return False, f"Error saat memperbarui status login: {str(e)}"
        finally:
            self.close(conn)

    def clear_last_login(self, user_id: int) -> Tuple[bool, str]:
        """Menghapus status login pengguna (mengatur last_login ke NULL)"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                UPDATE users
                SET last_login = NULL
                WHERE id = %s
                ''', (user_id,))
                conn.commit()
                return True, "Status login berhasil dihapus"
        except Exception as e:
            conn.rollback()
            return False, f"Error saat menghapus status login: {str(e)}"
        finally:
            self.close(conn)

    def delete_all_detections(self, user_id: int) -> Tuple[bool, str]:
        """Menghapus semua riwayat deteksi pengguna"""
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                DELETE FROM detection_history
                WHERE user_id = %s
                ''', (user_id,))
                conn.commit()
                return True, "Semua riwayat deteksi berhasil dihapus"
        except Exception as e:
            conn.rollback()
            return False, f"Error saat menghapus semua deteksi: {str(e)}"
        finally:
            self.close(conn)
