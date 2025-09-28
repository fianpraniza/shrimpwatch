import streamlit as st
import os
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, UnidentifiedImageError
import io
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import pandas as pd
import base64
import time
import config as db_config #
from typing import List, Dict, Any, Optional, Tuple #

# --- Constants ---
SESSION_STATE_AUTHENTICATED = 'authenticated'
SESSION_STATE_USERNAME = 'username'
SESSION_STATE_USER_ID = 'user_id'
SESSION_STATE_PAGE = 'page'
SESSION_STATE_DETECTION_HISTORY = 'detection_history'
SESSION_STATE_CURRENT_DETECTION = 'current_detection'

PAGE_HOME = 'home'
PAGE_DETECTION = 'detection'
PAGE_HISTORY = 'history'
PAGE_PROFILE = 'profile'

TIMEZONE_WIB = timezone(timedelta(hours=7)) # Definisi untuk UTC+7

# Valid email domains for registration
VALID_EMAIL_DOMAINS = ['@gmail.com', '@yahoo.com', '@hotmail.com', '@outlook.com', '@edu.ac.id']
# Max file size for upload (in bytes)
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# --- Page Configuration ---
st.set_page_config(
    page_title="Shrimpwatch",
    page_icon="🦐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .css-1d391kg { padding: 1rem 1rem; } /* Might need adjustment based on Streamlit version */
    .stProgress .st-bo { background-color: #4CAF50; } /* For progress bar */
    .login-container { max-width: 400px; margin: 0 auto; padding: 2rem; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
def initialize_session_state():
    if SESSION_STATE_AUTHENTICATED not in st.session_state:
        st.session_state[SESSION_STATE_AUTHENTICATED] = False
    if SESSION_STATE_USERNAME not in st.session_state:
        st.session_state[SESSION_STATE_USERNAME] = None
    if SESSION_STATE_USER_ID not in st.session_state:
        st.session_state[SESSION_STATE_USER_ID] = None
    if SESSION_STATE_PAGE not in st.session_state:
        st.session_state[SESSION_STATE_PAGE] = PAGE_HOME
    if SESSION_STATE_DETECTION_HISTORY not in st.session_state:
        st.session_state[SESSION_STATE_DETECTION_HISTORY] = []
    if SESSION_STATE_CURRENT_DETECTION not in st.session_state:
        st.session_state[SESSION_STATE_CURRENT_DETECTION] = None

initialize_session_state()

# --- Model Loading ---
@st.cache_resource
def load_yolo_model() -> YOLO:
    """Loads the YOLO model using Streamlit's caching for resources."""
    try:
        model = YOLO('best.pt')
        return model
    except Exception as e:
        st.error(f"Gagal memuat model YOLO: {e}. Pastikan file 'best.pt' tersedia.")
        raise

# --- Image Processing Utilities ---
def split_image(image: np.ndarray) -> List[np.ndarray]:
    """Splits the image into a 3x3 grid."""
    height, width = image.shape[:2]
    h_step = height // 3
    w_step = width // 3
    parts = []
    for i in range(3):
        for j in range(3):
            part = image[i*h_step:(i+1)*h_step, j*w_step:(j+1)*w_step]
            parts.append(part)
    return parts

def process_single_image_for_detection(image_array: np.ndarray, model: YOLO) -> Tuple[np.ndarray, int]:
    """Processes a single image part for detection, draws bounding boxes on original image, returns annotated image and count."""
    
    # Salin gambar asli untuk anotasi
    vis_image = image_array.copy()

    # Pastikan image_array dalam format uint8 untuk normalisasi/deteksi
    if image_array.dtype != np.uint8:
        if image_array.max() <= 1.0:
            image_array = (image_array * 255).astype(np.uint8)
        else:
            image_array = image_array.astype(np.uint8)

    # Normalisasi gambar untuk deteksi
    normalized_image = cv2.normalize(image_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    # Lakukan deteksi menggunakan gambar yang sudah dinormalisasi
    results = model(normalized_image, conf=0.23)
    result = results[0]
    count = len(result.boxes)

    # Jika vis_image adalah grayscale, konversi ke BGR untuk bisa menggambar warna
    if len(vis_image.shape) == 2 or (len(vis_image.shape) == 3 and vis_image.shape[2] == 1):
        vis_image = cv2.cvtColor(vis_image, cv2.COLOR_GRAY2BGR)

    # Gambar bounding box pada salinan gambar asli
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 0, 255), 1)  # warna merah

    return vis_image, count

def process_uploaded_image(image_np: np.ndarray, model: YOLO) -> Tuple[List[np.ndarray], List[int], int]:
    """Splits image, processes each part, and aggregates results."""
    # Jika gambar input adalah RGBA, konversi ke RGB
    if image_np.shape[2] == 4:
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        
    split_images_list = split_image(image_np)
    total_count = 0
    processed_images_list = []
    counts_per_part_list = []
    
    for split_img_np in split_images_list:
        result_img, count = process_single_image_for_detection(split_img_np, model)
        total_count += count
        processed_images_list.append(result_img)
        counts_per_part_list.append(count)
    
    return processed_images_list, counts_per_part_list, total_count

# --- Authentication and User Management ---
def validate_registration_inputs(username: str, password: str, email: str, full_name: str) -> List[str]:
    """Validates user registration inputs."""
    errors: List[str] = []
    if not (4 <= len(username) <= 50): errors.append("Username minimal 4 dan maksimal 50 karakter.")
    if not username.isalnum(): errors.append("Username hanya boleh berisi huruf dan angka.")
    if not (8 <= len(password) <= 255): errors.append("Password minimal 8 dan maksimal 255 karakter.")
    if not any(c.isupper() for c in password): errors.append("Password harus mengandung minimal 1 huruf besar.")
    if not any(c.islower() for c in password): errors.append("Password harus mengandung minimal 1 huruf kecil.")
    if not any(c.isdigit() for c in password): errors.append("Password harus mengandung minimal 1 angka.")
    if not any(email.endswith(domain) for domain in VALID_EMAIL_DOMAINS):
        errors.append(f"Email harus menggunakan domain yang valid ({', '.join(VALID_EMAIL_DOMAINS)}).")
    if not (3 <= len(full_name) <= 100): errors.append("Nama lengkap minimal 3 dan maksimal 100 karakter.")
    if not all(c.isalpha() or c.isspace() for c in full_name): errors.append("Nama lengkap hanya boleh berisi huruf dan spasi.")
    return errors

def attempt_login(username: str, password: str) -> None:
    """Handles the login attempt."""
    success, message, user_data = db_config.authenticate_user(username, password) #
    if success and user_data:
        st.session_state[SESSION_STATE_AUTHENTICATED] = True
        st.session_state[SESSION_STATE_USERNAME] = user_data['username']
        st.session_state[SESSION_STATE_USER_ID] = user_data['id']
        st.session_state[SESSION_STATE_PAGE] = PAGE_HOME # Redirect to home on login
        # Load detection history for the logged-in user
        st.session_state[SESSION_STATE_DETECTION_HISTORY] = db_config.get_detection_history(user_data['id']) #
        st.success(message)
        st.rerun()
    else:
        st.error(message)

def attempt_registration(username: str, password: str, email: str, full_name: str) -> None:
    """Handles the registration attempt."""
    validation_errors = validate_registration_inputs(username, password, email, full_name)
    if validation_errors:
        for error in validation_errors:
            st.error(error)
    else:
        success, message = db_config.register_user(username, password, email, full_name) #
        if success:
            st.success(message + " Silakan login.")
        else:
            st.error(message)

def logout() -> None:
    """Logs out the current user."""
    if st.session_state.get(SESSION_STATE_USER_ID): # Check if user_id exists before clearing
        db_config.clear_last_login(st.session_state[SESSION_STATE_USER_ID]) #

    st.session_state[SESSION_STATE_AUTHENTICATED] = False
    st.session_state[SESSION_STATE_USERNAME] = None
    st.session_state[SESSION_STATE_USER_ID] = None
    st.session_state[SESSION_STATE_PAGE] = PAGE_HOME
    st.session_state[SESSION_STATE_DETECTION_HISTORY] = []
    st.session_state[SESSION_STATE_CURRENT_DETECTION] = None
    # Clear any other sensitive session data if necessary
    st.success("Anda telah berhasil logout.")
    st.rerun()

def check_persistent_login() -> None:
    """Checks if a user was recently logged in (e.g., within 24 hours) to auto-login."""
    pass # Auto-login disabled for security/simplicity review.

# Auto-login check (currently disabled, see function above)
if not st.session_state[SESSION_STATE_AUTHENTICATED]:
    check_persistent_login() # This would set session state if a user is found

def convert_to_wib_datetime(timestamp_input: Any) -> Optional[datetime]:
    """
    Mengkonversi berbagai input timestamp (string ISO, objek datetime)
    menjadi objek datetime yang sadar zona waktu WIB (UTC+7).
    Jika input adalah datetime naive, diasumsikan sebagai UTC.
    """
    if timestamp_input is None:
        return None

    dt_obj = None
    if isinstance(timestamp_input, str):
        try:
            dt_obj = datetime.fromisoformat(timestamp_input)
        except ValueError:
            return None
    elif isinstance(timestamp_input, datetime):
        dt_obj = timestamp_input
    else:
        return None
    if dt_obj.tzinfo is None or dt_obj.tzinfo.utcoffset(dt_obj) is None:
        dt_obj = dt_obj.replace(tzinfo=timezone.utc).astimezone(TIMEZONE_WIB)
    else:
        dt_obj = dt_obj.astimezone(TIMEZONE_WIB)
    
    return dt_obj

def format_wib_datetime_str(dt_wib: Optional[datetime], fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Memformat objek datetime WIB menjadi string."""
    if dt_wib is None:
        return "N/A"
    return dt_wib.strftime(fmt)

# --- UI Rendering Functions ---
def display_login_page() -> None:
    """Displays the login and registration forms."""
    st.markdown("""
        <div style='text-align: center; padding: 1rem; margin-bottom: 1rem;'>
            <h1 style='color: #2C3E50; font-size: 2rem; font-weight: 600;'>Shrimpwatch (Versi Beta)</h1>
            <p style='color: #34495E; font-size: 1.3rem; margin-bottom: 0.5rem;'> Sistem Deteksi dan Penghitung Benur Udang Otomatis</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div style='background-color: #F8F9FA; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'><h2 style='color: #2C3E50; margin-bottom: 1.5rem;'>Login</h2></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button("Login", use_container_width=True):
                if login_username and login_password:
                    attempt_login(login_username, login_password)
                else:
                    st.error("Username dan Password tidak boleh kosong.")
    
    with col2:
        st.markdown("<div style='background-color: #F8F9FA; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'><h2 style='color: #2C3E50; margin-bottom: 1.5rem;'>Registrasi</h2></div>", unsafe_allow_html=True)
        with st.form("register_form"):
            reg_username = st.text_input("Username Registrasi", key="reg_username", help="Minimal 4 karakter, hanya huruf dan angka")
            reg_password = st.text_input("Password Registrasi", type="password", key="reg_password", help="Min 8 karakter, huruf besar, huruf kecil, angka")
            reg_email = st.text_input("Email Registrasi", key="reg_email", help=f"Domain: {', '.join(VALID_EMAIL_DOMAINS)}")
            reg_full_name = st.text_input("Nama Lengkap Registrasi", key="reg_full_name", help="Minimal 3 karakter, hanya huruf dan spasi")
            
            with st.expander("📋 Aturan Registrasi"):
                st.markdown("""
                - **Username:** Minimal 4 karakter, hanya huruf dan angka.
                - **Password:** Minimal 8 karakter, mengandung huruf besar, huruf kecil, dan angka.
                - **Email:** Gunakan domain yang valid (@gmail.com, @yahoo.com, dll.).
                - **Nama Lengkap:** Minimal 3 karakter, hanya huruf dan spasi.
                """)
            
            if st.form_submit_button("Daftar", use_container_width=True):
                if reg_username and reg_password and reg_email and reg_full_name:
                    attempt_registration(reg_username, reg_password, reg_email, reg_full_name)
                else:
                    st.error("Semua field registrasi harus diisi.")

def display_sidebar() -> None:
    """Displays the navigation sidebar."""
    with st.sidebar:
        st.image("./asset/shrimpwatch.png", width=300) # Adjust width as needed
        
        if st.session_state[SESSION_STATE_AUTHENTICATED]:
            st.title(f"Selamat Datang, {st.session_state.get(SESSION_STATE_USERNAME, '')}!")
            st.markdown("Jelajahi fitur-fitur utama Shrimpwatch.")
            
            if st.button("🏠 Beranda", use_container_width=True, key="nav_home"): st.session_state[SESSION_STATE_PAGE] = PAGE_HOME
            if st.button("🔍 Deteksi", use_container_width=True, key="nav_detection"): st.session_state[SESSION_STATE_PAGE] = PAGE_DETECTION
            if st.button("📋 Riwayat", use_container_width=True, key="nav_history"): st.session_state[SESSION_STATE_PAGE] = PAGE_HISTORY
            if st.button("👤 Profil", use_container_width=True, key="nav_profile"): st.session_state[SESSION_STATE_PAGE] = PAGE_PROFILE
            
            st.markdown("---")
            st.title("Statistik Deteksi")
            total_benur = sum(item.get('total_count', 0) for item in st.session_state.get(SESSION_STATE_DETECTION_HISTORY, []))
            st.metric(label="Total Benur Terdeteksi (Sesi Ini)", value=total_benur) # Clarified "Sesi Ini" as history is loaded on login
            
            if st.button("🚪 Logout", use_container_width=True):
                logout()
        else:
            st.info("Selamat datang di Shrimpwatch (Versi Beta)! Login atau registrasi untuk menjadi salah satu yang pertama mencoba fitur-fitur terbaru kami dan bantu kami menyempurnakan aplikasi dengan masukan berharga Anda.")

def display_home_page() -> None:
    """Displays the home page content."""
    # HEADER BETA-TESTING
    st.markdown("""
        <div style='text-align: justify; padding: 1rem; margin-bottom: 1rem;'>
            <h1 style='color: #2C3E50; font-size: 2rem; font-weight: 600;'>Selamat Bergabung di Petualangan Beta Shrimpwatch!</h1>
            <p style='color: #34495E; font-size: 1.1rem;'>Terima kasih telah menjadi bagian dari perjalanan awal Shrimpwatch! Aplikasi yang sedang Anda gunakan ini adalah <strong>versi Beta</strong>, yang berarti ini adalah kesempatan spesial bagi Anda untuk merasakan fitur-fitur terbaru kami dan membantu kami menjadikannya lebih baik. Sebagai Beta Tester, peran Anda sangatlah berharga. Kami mengajak Anda untuk menjelajahi setiap sudut Shrimpwatch dengan saksama.</p>
            <strong style='font-size: 1.1rem;'>Untuk memulai petualangan anda, silakan:</strong>
            <ol style='color: #34495E; font-size: 1.1rem; text-align: justify; margin-left: 1.5rem; padding-left: 0.5rem;'>
                <li style='margin-bottom: 0.3rem;'>Pelajari cara penggunaan aplikasi melalui tab <strong>"📚 Panduan Penggunaan"</strong> di bawah ini agar Anda bisa memaksimalkan eksplorasi.</li>
                <li style='margin-bottom: 0.3rem;'>Setelah mencoba berbagai fiturnya, kami sangat mengharapkan masukan Anda melalui tab <strong>"📝 Umpan Balik (Feedback)"</strong>. Sampaikan pengalaman, kendala, ataupun ide-ide cemerlang yang Anda miliki!</li>
            </ol>
            <p style='color: #34495E; font-size: 1.1rem;'>Setiap masukan Anda akan menjadi fondasi penting untuk pengembangan Shrimpwatch ke depan. Selamat mencoba dan berpetualang!"</p>
        </div>
    """, unsafe_allow_html=True) # Shortened for brevity

    # TAB BERANDA VERSI 2
    tab_panduan, tab_feedback = st.tabs(["📚 Panduan Penggunaan", "📝 Umpan Balik (Feedback)"])
    
    with tab_panduan:
        st.markdown("### 📚 Panduan Cepat Deteksi Benur")
        st.markdown("Ikuti langkah mudah ini untuk menggunakan fitur deteksi Shrimpwatch:")
        
        col1_panduan, col2_panduan = st.columns(2)

        with col1_panduan:
            st.markdown("""
            #### 1. Buka Halaman Deteksi
            * Dari menu samping (sidebar), pilih **"🔍 Deteksi"**.
            
            #### 2. Unggah Gambar Benur
            * Klik area unggah atau seret file gambar Anda.
            * **Format:** JPG, JPEG, PNG.
            * **Maks:** 5MB.
            """)

        with col2_panduan:
            st.markdown("""
            #### 3. Mulai Proses Deteksi
            * Klik tombol **"🔍 Deteksi Benur"**.
            * Tunggu beberapa saat hingga hasil muncul.

            #### 4. Analisis & Simpan Hasil
            * Lihat jumlah total & distribusi benur pada grid.
            * Klik **"💾 Simpan Hasil"** untuk mencatat ke riwayat.
            """)
        
        st.markdown("---")
        st.subheader("🔑 Tips Kunci untuk Hasil Terbaik")
        col_tips1, col_tips2, col_tips3 = st.columns(3)
        with col_tips1:
            st.markdown("* **Gambar Jelas & Fokus**")
        with col_tips2:
            st.markdown("* **Cahaya Cukup & Merata**")
        with col_tips3:
            st.markdown("* **Kontras Background Baik**")

        with st.expander("Lihat Detail Kriteria Gambar & Tips Optimalisasi Lainnya"):
            st.markdown("""
            * **Kualitas Gambar Detail:** Selain jelas dan fokus, pastikan gambar tidak pecah atau buram. Semakin baik kualitasnya, semakin akurat deteksinya.
            * **Pencahayaan Detail:** Hindari bayangan gelap yang menutupi benur atau area yang terlalu terang (*overexposed*) sehingga detail benur hilang.
            * **Background Detail:** Warna background yang kontras dengan warna benur (misal, background putih untuk benur gelap) sangat membantu sistem dalam identifikasi.
            * **Kepadatan Benur:** Usahakan benur tidak terlalu padat hingga saling tumpuk masif. Kepadatan ideal memungkinkan sistem melihat benur sebagai individu. Aplikasi dioptimalkan hingga sekitar 1.000 benur per gambar.
            * **Posisi Benur:** Pastikan area yang berisi benur berada dalam frame foto dengan baik.
            """)

        with st.expander("Mengenal Fitur Lainnya (Riwayat & Profil)"):
            st.markdown("""
            * **📋 Riwayat Deteksi:**
                * Akses semua data deteksi yang pernah Anda simpan.
                * Lihat detail dan analisis per sesi deteksi.
                * Ekspor riwayat ke file CSV untuk analisis lanjutan.
                * Hapus data riwayat jika tidak diperlukan.
            * **👤 Profil Pengguna:**
                * Lihat informasi akun Anda.
                * Pantau statistik penggunaan aplikasi Anda.
            """)
        
        with st.expander("Batasan Sistem & Butuh Bantuan?"):
            st.markdown("""
            * **Ukuran File:** Maksimal 5MB per gambar.
            * **Format Didukung:** Hanya JPG, JPEG, PNG.
            * **Kendala atau Pertanyaan?** Jika panduan ini belum menjawab, atau Anda menemukan masalah, sampaikan melalui tab **"📝 Umpan Balik (Feedback)"**. Kami siap membantu!
            """)
            
    with tab_feedback: # NEW TAB for feedback
        st.markdown("""
        ### 📢 Umpan Balik untuk Tahap Beta Testing

        Selamat datang di tahap Beta Testing aplikasi Shrimpwatch! 
        Partisipasi Anda sangat berharga bagi kami untuk menyempurnakan aplikasi ini sebelum rilis penuh. 
        Kami mengundang Anda untuk menjelajahi semua fitur dan memberikan masukan, laporan bug, atau saran perbaikan.

        #### Tahap-tahap Pemberian Feedback:
        1.  **Registrasi dan Login:** Coba proses pembuatan akun baru dan proses login. Apakah berjalan lancar?
        2.  **Navigasi Aplikasi:** Jelajahi setiap halaman (Beranda, Deteksi, Riwayat, Profil). Apakah navigasi mudah dipahami?
        3.  **Fitur Deteksi:**
            * Upload berbagai jenis gambar benur (kualitas baik/buruk, pencahayaan berbeda, kepadatan berbeda).
            * Perhatikan akurasi hasil deteksi dan penghitungan.
            * Coba simpan hasil deteksi.
        4.  **Fitur Riwayat:**
            * Lihat daftar riwayat deteksi Anda.
            * Coba fitur ekspor ke CSV.
            * Coba hapus item riwayat atau reset semua riwayat.
        5.  **Halaman Profil:** Periksa informasi profil Anda dan statistik penggunaan.
        6.  **Catat Temuan Anda:**
            * **Bug/Error:** Jika Anda menemukan error, catat pesan error yang muncul, langkah-langkah yang Anda lakukan sebelum error terjadi, dan jika memungkinkan, sertakan screenshot.
            * **Kenyamanan Pengguna (UX):** Apakah ada alur yang membingungkan? Apakah tampilan ada yang kurang jelas atau sulit digunakan?
            * **Saran Fitur:** Apakah ada fitur tambahan yang menurut Anda akan sangat berguna atau perbaikan pada fitur yang sudah ada?
            * **Kesan Umum:** Bagaimana pendapat Anda secara keseluruhan mengenai kemudahan penggunaan, kecepatan, dan manfaat aplikasi?
        7.  **Isi Formulir Feedback:** Setelah Anda cukup mencoba dan mencatat temuan, mohon sampaikan semua masukan Anda melalui Google Form yang telah kami sediakan di bawah ini.

        Setiap feedback, sekecil apapun, akan sangat membantu kami. Terima kasih atas partisipasi Anda!
        """)

        st.markdown("---") 

        st.markdown("""
        #### 🔗 Isi Formulir Feedback Di Sini:
        Mohon klik tautan di bawah ini untuk mengisi formulir feedback. Pastikan Anda sudah mencoba berbagai fitur sebelum mengisi.
        
        **[Link Google Form Feedback Shrimpwatch Beta](https://forms.gle/UHdpjKP2CCVHr9x96)**
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("""
        #### 📞 Kontak Person:
        Jika ada pertanyaan lebih lanjut, kendala saat pengisian form, atau diskusi yang ingin disampaikan secara langsung, Anda dapat menghubungi:
        - **Nama:** Muhammad Arfian Praniza
        - **Email:** fianpraniza@gmail.com
        
        Sekali lagi, kami ucapkan terima kasih banyak atas kesediaan Anda menjadi bagian dari Beta Tester Shrimpwatch!
        """)

# Halaman Deteksi
def display_detection_page(model: YOLO) -> None:
    """Displays the shrimp detection page."""
    st.title("Deteksi dan Penghitungan Benur")

    # Upload area
    uploaded_file = st.file_uploader(
        "Pilih gambar benur udang (JPG, JPEG, PNG, maks 5MB)",
        type=['jpg', 'jpeg', 'png'],
        key="file_uploader"
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue() # Use getvalue() for BytesIO
        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            st.error(f"Ukuran file terlalu besar ({len(file_bytes)/(1024*1024):.2f}MB). Maksimal {MAX_FILE_SIZE_MB}MB.")
        else:
            try:
                pil_image = Image.open(io.BytesIO(file_bytes))
                
                # Convert PIL image to NumPy array
                # Ensure it's RGB for consistent processing
                if pil_image.mode == 'RGBA':
                    pil_image = pil_image.convert('RGB')
                elif pil_image.mode == 'L': # Grayscale
                    pil_image = pil_image.convert('RGB') # Convert to RGB for color drawing

                image_np = np.array(pil_image)

                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(image_np, caption="Gambar Asli", use_container_width=True)
                with col2:
                    st.info(f"""
                    ### Informasi Gambar
                    - Format: {uploaded_file.type}
                    - Resolusi: {image_np.shape[1]} x {image_np.shape[0]}
                    - Mode: {pil_image.mode}
                    - Ukuran File: {len(file_bytes) / (1024 * 1024):.2f} MB
                    """)

                # Tombol deteksi
                if st.button("🔍 Deteksi Benur", use_container_width=True, key="detect_button"):
                    with st.spinner("Memproses gambar..."):
                        processed_imgs, counts, total_cnt = process_uploaded_image(image_np, model)
                        
                        avg_count = total_cnt / len(counts) if counts else 0
                        max_cnt = max(counts) if counts else 0
                        min_cnt = min(counts) if counts else 0
                        max_idx = counts.index(max_cnt) if total_cnt > 0 and max_cnt in counts else -1
                        min_idx = counts.index(min_cnt) if total_cnt > 0 and min_cnt in counts else -1
                        
                        st.session_state[SESSION_STATE_CURRENT_DETECTION] = {
                            'timestamp': datetime.now(TIMEZONE_WIB),
                            'total_count': total_cnt,
                            'counts_per_part': counts,
                            'average_count': avg_count,
                            'max_count': max_cnt,
                            'max_part_index': max_idx,
                            'min_count': min_cnt,
                            'min_part_index': min_idx,
                            'processed_images_for_display': processed_imgs, # For display only
                            'file_name': uploaded_file.name
                        }
                    st.success(f"✅ Jumlah Total Benur Terdeteksi: {total_cnt}")

            except UnidentifiedImageError:
                st.error("Gagal membaca file gambar. Pastikan format file benar (JPG, JPEG, PNG) dan file tidak rusak.")
            except Exception as e:
                st.error(f"Error saat memproses gambar: {str(e)}")
                st.info("Silakan coba upload gambar lain.")

    # Display current detection results if available
    current_detection = st.session_state.get(SESSION_STATE_CURRENT_DETECTION)
    if current_detection:
        st.markdown("### Hasil Deteksi dan Penghitungan")
        grid_cols = st.columns(3)
        processed_images_to_display = current_detection.get('processed_images_for_display', [])
        counts_to_display = current_detection.get('counts_per_part', [])

        for i in range(3): # Rows
            for j in range(3): # Columns
                idx = i * 3 + j
                if idx < len(processed_images_to_display):
                    with grid_cols[j]: # Fill columns first, then wrap implicitly if more rows needed by design
                         st.image(
                            processed_images_to_display[idx],
                            caption=f"Bagian {idx + 1} ({counts_to_display[idx]} benur)",
                            use_container_width=True
                        )
        
        with st.expander("📊 Informasi Deteksi", expanded=True):
            # Display stats from current_detection
            col1, col2 = st.columns(2)
            with col1:
                st.write("### Statistik Deteksi")
                st.write(f"- Total Objek Terdeteksi: {current_detection['total_count']} benur")
                st.write(f"- Rata-rata Benur per Bagian: {current_detection['average_count']:.2f} benur")
                if current_detection['max_part_index'] != -1:
                    st.write(f"- Bagian Terbanyak: Bagian {current_detection['max_part_index'] + 1} ({current_detection['max_count']} benur)")
                if current_detection['min_part_index'] != -1:
                    st.write(f"- Bagian Tersedikit: Bagian {current_detection['min_part_index'] + 1} ({current_detection['min_count']} benur)")
            with col2:
                fig = go.Figure(data=[go.Bar(x=[f"Bagian {i+1}" for i in range(9)], y=current_detection['counts_per_part'], marker_color='#4CAF50')])
                fig.update_layout(title="Distribusi Benur per Bagian", height=300)
                st.plotly_chart(fig, use_container_width=True)

        if st.button("💾 Simpan Hasil", use_container_width=True, key="save_button"):
            detection_to_save = current_detection.copy()
            detection_to_save['timestamp'] = datetime.now(TIMEZONE_WIB)
            detection_to_save.pop('processed_images_for_display', None)
            
            user_id = st.session_state.get(SESSION_STATE_USER_ID)
            if user_id:
                success, msg = db_config.save_detection(user_id, detection_to_save) #
                if success:
                    st.success("✅ Hasil deteksi berhasil disimpan!")
                    # Reload history
                    st.session_state[SESSION_STATE_DETECTION_HISTORY] = db_config.get_detection_history(user_id) #
                    st.session_state[SESSION_STATE_CURRENT_DETECTION] = None # Clear current
                    st.rerun()
                else:
                    st.error(f"Gagal menyimpan hasil deteksi: {msg}")
            else:
                st.error("Tidak dapat menyimpan, user ID tidak ditemukan. Silakan login ulang.")

# halaman riwayat deteksi
def display_history_page() -> None:
    """Displays the detection history page."""
    st.title("Riwayat Deteksi")
    user_id = st.session_state.get(SESSION_STATE_USER_ID)

    if not user_id:
        st.warning("Silakan login untuk melihat riwayat deteksi.")
        return

    detection_history: List[Dict[str, Any]] = st.session_state.get(SESSION_STATE_DETECTION_HISTORY, [])

    if detection_history:
        processed_history = []
        for item_from_session in detection_history:
            new_item_for_processing = item_from_session.copy()
            timestamp_value_from_item = new_item_for_processing.get('timestamp')

            new_item_for_processing['timestamp_dt_wib'] = convert_to_wib_datetime(timestamp_value_from_item)
            
            processed_history.append(new_item_for_processing)

        # Sort by the datetime object, oldest first (ascending)
        processed_history.sort(key=lambda x: x.get('timestamp_dt_wib') or datetime.min)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            df_export_data = []
            for item_for_csv in processed_history: # Or use original detection_history if preferred for export
                temp_item = item_for_csv.copy()
                if 'timestamp_dt_wib' in temp_item and temp_item['timestamp_dt_wib']:
                    temp_item['timestamp'] = format_wib_datetime_str(temp_item['timestamp_dt_wib'])
                    del temp_item['timestamp_dt_wib'] # Hapus field sementara jika ada
                else: # Fallback jika tidak ada timestamp_dt_wib
                    temp_item['timestamp'] = format_wib_datetime_str(convert_to_wib_datetime(item_for_csv.get('timestamp')))

                df_export_data.append(temp_item)

            df_export = pd.DataFrame(df_export_data) # Use the potentially modified data
            if not df_export.empty:
                if 'timestamp' in df_export.columns:
                     df_export['timestamp'] = pd.to_datetime(df_export['timestamp'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
                
                if 'counts_per_part' in df_export.columns:
                    counts_data = []
                    for cp in df_export['counts_per_part']:
                        if isinstance(cp, list) and len(cp) == 9:
                            counts_data.append(cp)
                        else:
                            counts_data.append([0]*9) # Default if data is malformed

                    counts_df = pd.DataFrame(counts_data,
                                             columns=[f'Bagian_{i+1}' for i in range(9)],
                                             index=df_export.index) # ensure index alignment
                    df_export = pd.concat([df_export.drop('counts_per_part', axis=1), counts_df], axis=1)
                
                csv_data = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Ekspor ke CSV",
                    data=csv_data,
                    file_name=f"riwayat_deteksi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with col2:
            if st.button("🔄 Reset Semua Riwayat", use_container_width=True, key="reset_button", type="primary"):
                success, msg = db_config.delete_all_detections(user_id) #
                if success:
                    st.session_state[SESSION_STATE_DETECTION_HISTORY] = []
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        st.markdown("### Daftar Riwayat Deteksi")
        # Iterate over the sorted history
        for idx, item in enumerate(processed_history): #
            # Use the pre-processed datetime object for display
            ts_display_obj_wib = item.get('timestamp_dt_wib')

            expander_label = f"Deteksi #{idx + 1} - {format_wib_datetime_str(ts_display_obj_wib)}"

            with st.expander(expander_label):
                if 'file_name' in item: st.write(f"**Nama File:** {item['file_name']}")
                col1_exp, col2_exp, col3_exp = st.columns([2, 1, 1]) # Renamed to avoid conflict with outer col1, col2
                with col1_exp:
                    st.write(f"**Total Objek Terdeteksi:** {item.get('total_count', 0)} benur")
                    if 'average_count' in item: st.write(f"**Rata-rata Benur per Bagian:** {item.get('average_count', 0):.2f} benur")
                    if item.get('max_part_index', -1) != -1 : st.write(f"**Bagian Terbanyak:** Bagian {item['max_part_index'] + 1} ({item.get('max_count',0)} benur)")
                    if item.get('min_part_index', -1) != -1 : st.write(f"**Bagian Tersedikit:** Bagian {item['min_part_index'] + 1} ({item.get('min_count',0)} benur)")
                with col2_exp:
                    counts_for_plot = item.get('counts_per_part', [0]*9)
                    if not isinstance(counts_for_plot, list) or len(counts_for_plot) != 9:
                        counts_for_plot = [0]*9 # Default for safety
                    
                    fig = go.Figure(data=[go.Bar(x=[f"Bagian {i+1}" for i in range(9)], y=counts_for_plot, marker_color='#4CAF50')])
                    fig.update_layout(title="Distribusi Benur", height=200, margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig, use_container_width=True, key=f"history_chart_{item.get('id', idx)}")
                with col3_exp:
                    if st.button("🗑️ Hapus", key=f"delete_{item.get('id', idx)}"): #
                        success, msg = db_config.delete_detection(item['id'], user_id) #
                        if success:
                            st.session_state[SESSION_STATE_DETECTION_HISTORY] = db_config.get_detection_history(user_id) #
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        st.info("Belum ada riwayat deteksi yang tersimpan.")

def display_profile_page() -> None:
    """Displays the user profile page."""
    st.title("Profil Pengguna")
    username = st.session_state.get(SESSION_STATE_USERNAME)
    if not username:
        st.warning("Informasi pengguna tidak tersedia. Silakan login ulang.")
        return

    user_info = db_config.get_user_info(username) #
    if user_info:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### Informasi Pengguna")
            st.write(f"**Username:** {user_info.get('username')}")
            st.write(f"**Nama Lengkap:** {user_info.get('full_name')}")
            st.write(f"**Email:** {user_info.get('email')}")
            
            created_at_str = user_info.get('created_at')
            last_login_str = user_info.get('last_login')

            created_at_wib_dt = convert_to_wib_datetime(created_at_str)
            last_login_wib_dt = convert_to_wib_datetime(last_login_str)

            if created_at_wib_dt: 
                st.write(f"**Bergabung:** {format_wib_datetime_str(created_at_wib_dt, '%d %B %Y')}")
            else: 
                st.write(f"**Bergabung:** {created_at_str if created_at_str else 'N/A'}") # Tampilkan raw jika gagal parse

            if last_login_wib_dt: 
                st.write(f"**Login Terakhir:** {format_wib_datetime_str(last_login_wib_dt, '%d %B %Y %H:%M')}")
            else: 
                st.write(f"**Login Terakhir:** {last_login_str if last_login_str else 'N/A'}") # Tampilkan raw jika gagal parse


        with col2:
            st.markdown("### Statistik Penggunaan")
            history = st.session_state.get(SESSION_STATE_DETECTION_HISTORY, [])
            total_detections = len(history)
            total_benur = sum(item.get('total_count', 0) for item in history)
            
            st.metric("Total Sesi Deteksi Tercatat", total_detections)
            st.metric("Total Benur Terdeteksi (dari Riwayat)", total_benur)
            
            if total_detections > 0:
                dates_wib = []
                counts = []
                sorted_history_for_chart = sorted(history, key=lambda x: convert_to_wib_datetime(x.get('timestamp')) or datetime.min)

                for item_hist in sorted_history_for_chart:
                    dt_wib = convert_to_wib_datetime(item_hist.get('timestamp'))
                    if dt_wib:
                        dates_wib.append(dt_wib)
                        counts.append(item_hist.get('total_count',0))

                if dates_wib:
                    fig = go.Figure(data=[go.Scatter(x=dates_wib, y=counts, mode='lines+markers')])
                    fig.update_layout(title="Aktivitas Deteksi (WIB)", xaxis_title="Tanggal", yaxis_title="Jumlah Benur", height=300)
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Gagal memuat informasi profil.")

def display_footer() -> None:
    """Displays the application footer."""
    st.markdown("---")
    _, col2, _ = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='text-align: center'>
            <p>Future of Aquaculture - I Believe in the Future</p>
            <p>Dikembangkan oleh Muhammad Arfian Praniza 2025 ©</p>
        </div>
        """, unsafe_allow_html=True)

# --- Main Application Flow ---
def main():
    display_sidebar()
    
    current_page = st.session_state.get(SESSION_STATE_PAGE, PAGE_HOME)

    if not st.session_state.get(SESSION_STATE_AUTHENTICATED, False):
        display_login_page()
    else:
        # Load model only if authenticated and needed for a page
        model = None
        if current_page == PAGE_DETECTION:
            try:
                model = load_yolo_model()
            except Exception: # Model loading failed, error already shown by load_yolo_model
                 st.error("Mode Deteksi tidak dapat diakses karena model gagal dimuat.")
                 st.session_state[SESSION_STATE_PAGE] = PAGE_HOME # Fallback to home
                 current_page = PAGE_HOME


        if current_page == PAGE_HOME:
            display_home_page()
        elif current_page == PAGE_DETECTION and model: # Check if model loaded
            display_detection_page(model)
        elif current_page == PAGE_HISTORY:
            display_history_page()
        elif current_page == PAGE_PROFILE:
            display_profile_page()
        else:
            display_home_page() 
            if current_page == PAGE_DETECTION and not model:
                st.warning("Kembali ke Beranda karena model deteksi tidak tersedia.")


    display_footer()

if __name__ == "__main__":
    main()
