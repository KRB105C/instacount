import os
import logging
from flask import Flask, request, jsonify
import instaloader

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

# Inisialisasi Instaloader
loader = instaloader.Instaloader()

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
    
    except Exception as e:
        logging.error(f"Terjadi kesalahan: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Railway akan menentukan port
    logging.info(f"Menjalankan server di port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
