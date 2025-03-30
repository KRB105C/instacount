import os
import time
import logging
import instaloader
from flask import Flask, request, jsonify

# Konfigurasi logging super lengkap
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Simpan log ke file
        logging.StreamHandler()  # Tampilkan log di terminal
    ]
)

app = Flask(__name__)

# Inisialisasi Instaloader dengan User-Agent dan sesi login
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
SESSION_FILE = "session-instagram"
USERNAME = os.environ.get("IG_USERNAME", "meme_nasional_indonesia_")  # Ganti dengan akunmu
PASSWORD = os.environ.get("IG_PASSWORD", "simeone")  # Ganti dengan passwordmu

loader = instaloader.Instaloader(user_agent=USER_AGENT)

# Coba muat sesi lama atau login baru
try:
    loader.load_session_from_file(USERNAME, SESSION_FILE)
    logging.info("Berhasil memuat sesi Instagram.")
except FileNotFoundError:
    logging.info("Sesi tidak ditemukan. Login dengan username & password...")
    try:
        loader.context.log("Login ke Instagram...")
        loader.login(USERNAME, PASSWORD)
        loader.save_session_to_file(SESSION_FILE)
        logging.info("Login berhasil. Sesi disimpan.")
    except instaloader.exceptions.BadCredentialsException:
        logging.error("Login gagal. Pastikan username & password benar.")
        exit(1)
    except instaloader.exceptions.ConnectionException:
        logging.error("Tidak dapat terhubung ke Instagram. Coba lagi nanti.")
        exit(1)

@app.route('/profile', methods=['GET'])
def get_profile():
    username = request.args.get('username')
    if not username:
        logging.warning("Permintaan tanpa parameter 'username'")
        return jsonify({"error": "Parameter 'username' diperlukan"}), 400
    
    try:
        logging.info(f"Mengambil data profil untuk username: {username}")
        profile = instaloader.Profile.from_username(loader.context, username)

        data = {
            "username": username,
            "followers": profile.followers,
            "following": profile.followees
        }

        logging.info(f"Data berhasil diambil: {data}")
        return jsonify(data)
    
    except instaloader.exceptions.ConnectionException as e:
        logging.error(f"Terjadi error koneksi: {e}")
        return jsonify({"error": "Gagal menghubungi Instagram. Coba lagi nanti."}), 503
    
    except instaloader.exceptions.ProfileNotExistsException:
        logging.warning(f"Profil {username} tidak ditemukan")
        return jsonify({"error": "Profil tidak ditemukan"}), 404
    
    except instaloader.exceptions.TooManyRequestsException:
        logging.warning("Terlalu banyak permintaan ke Instagram. Tunggu sebentar sebelum mencoba lagi.")
        time.sleep(5)  # Hindari rate limit
        return jsonify({"error": "Terlalu banyak permintaan. Coba lagi nanti."}), 429
    
    except Exception as e:
        logging.error(f"Terjadi kesalahan: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Railway akan menentukan port
    logging.info(f"Menjalankan server di port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
