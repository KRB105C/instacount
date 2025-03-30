import os
import logging
import instaloader
from flask import Flask, request, jsonify

# Konfigurasi logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

app = Flask(__name__)

# User-Agent agar tidak terdeteksi sebagai bot
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Ambil sessionid dari environment variable
SESSION_ID = os.environ.get("IG_SESSIONID")

if not SESSION_ID:
    logging.error("SESSION_ID Instagram tidak ditemukan! Tambahkan di environment variables.")
    exit(1)

# Inisialisasi Instaloader dengan User-Agent
loader = instaloader.Instaloader(user_agent=USER_AGENT)

# Set cookie session agar tidak perlu login manual
loader.context._session.cookies.set("sessionid", SESSION_ID)

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
        return jsonify({"error": "Terlalu banyak permintaan. Coba lagi nanti."}), 429

    except Exception as e:
        logging.error(f"Terjadi kesalahan: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Menjalankan server di port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
