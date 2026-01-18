# 🤖 Discord Bot with Python

Bot Discord sederhana yang dibuat menggunakan **Python** dan **discord.py** sebagai media pembelajaran pembuatan bot Discord.

## ✨ Fitur
- `!ping` → cek status bot
- `!hello` → menyapa user
- Auto reply kata tertentu
- Embed message
- Menggunakan environment variable untuk keamanan token

## 🛠️ Tech Stack
- Python 3.12
- discord.py
- python-dotenv

## 📂 Struktur Project
bot-discord/
├── bot.py
├── requirements.txt
├── .env
├── .gitignore
└── venv/


## 🚀 Cara Menjalankan Bot

### 1️⃣ Clone Repository
```bash
git clone https://github.com/USERNAME/discord-bot.git
cd discord-bot
2️⃣ Aktifkan Virtual Environment
python -m venv venv
venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Buat File .env
DISCORD_TOKEN=your_bot_token_here
5️⃣ Jalankan Bot
python bot.py

🔒 Keamanan
Token bot tidak disimpan di repository, menggunakan environment variable.

📌 Catatan
Project ini dibuat untuk tujuan pembelajaran dan pengembangan skill backend Python.

Author:
Ismet Maulana Azhary