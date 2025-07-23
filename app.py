from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import json
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Load data lokal
with open("data.json") as f:
    data = json.load(f)

# Inisialisasi client OpenAI dengan API Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prompt sistem untuk batasi GPT
system_prompt = """
Kamu adalah customer service ramah dari toko AndezStore.
Hanya jawab seputar produk, harga, pesanan, promo, dan pengiriman.
Jika tidak tahu atau di luar topik, katakan kamu hanya bisa bantu hal terkait layanan toko.
"""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json['message'].lower()

    # Cek produk
    for produk in data['produk']:
        if produk['nama'].lower() in user_message:
            harga = f"Rp{produk['harga']:,}".replace(",", ".")
            return jsonify({"response": f"Harga {produk['nama']} adalah {harga}."})

    # Cek pesanan
    if "pesanan" in user_message or "#" in user_message:
        for p in data["pesanan"]:
            if p["id"] in user_message:
                return jsonify({"response": f"Status pesanan #{p['id']}: {p['status']}."})
        return jsonify({"response": "Maaf, ID pesanan tidak ditemukan."})

    # Lempar ke GPT
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"Terjadi kesalahan saat menghubungi AI: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
