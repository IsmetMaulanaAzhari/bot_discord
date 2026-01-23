# 🤖 Discord Bot with Gemini AI

Bot Discord multifungsi yang dibuat menggunakan **Python**, **discord.py**, dan **Google Gemini AI** sebagai media pembelajaran pembuatan bot Discord.

---

## ✨ Fitur

### 🔧 Basic Commands
| Command | Deskripsi |
|---------|-----------|
| `/ping` | Cek status dan latency bot |
| `/info` | Informasi tentang bot |
| `/help` | Menampilkan daftar command |
| `/uptime` | Waktu aktif bot |

### 🤖 AI Commands
| Command | Deskripsi |
|---------|-----------|
| `/ai <prompt>` | Chat dengan Gemini AI |

### 👤 User Commands
| Command | Deskripsi |
|---------|-----------|
| `/avatar [@user]` | Menampilkan avatar user |
| `/userinfo [@user]` | Menampilkan informasi user |

### 🏠 Server Commands
| Command | Deskripsi |
|---------|-----------|
| `/serverinfo` | Menampilkan informasi server |

### 🛡️ Moderation Commands
| Command | Deskripsi |
|---------|-----------|
| `/kick @user [alasan]` | Kick member dari server |
| `/warn @user [alasan]` | Berikan peringatan kepada member |
| `/clear <jumlah>` | Hapus sejumlah pesan (1-100) |

### 📊 Utility Commands
| Command | Deskripsi |
|---------|-----------|
| `/poll "pertanyaan" "opsi1" "opsi2"` | Buat polling sederhana |

### ⚡ Fitur Lainnya
- Auto reply untuk kata tertentu
- Slash commands support
- AutoSharded bot untuk scalability
- Embed messages

---

## 🛠️ Tech Stack
- **Python 3.12**
- **discord.py**
- **python-dotenv**
- **google-generativeai**

---

## 📂 Struktur Project
```
bot-discord/
├── bot.py
├── requirements.txt
├── .env
├── .gitignore
└── venv/
```

---

## 🚀 Cara Menjalankan Bot

### 1️⃣ Clone Repository
```bash
git clone https://github.com/IsmetMaulanaAzhari/bot_discord.git
cd bot_discord
```

### 2️⃣ Aktifkan Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Buat File .env
```env
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

### 5️⃣ Jalankan Bot
```bash
python bot.py
```

---

## 🔑 Mendapatkan API Keys

### Discord Bot Token
1. Buka [Discord Developer Portal](https://discord.com/developers/applications)
2. Buat aplikasi baru
3. Pergi ke menu "Bot"
4. Copy token bot

### Gemini API Key
1. Buka [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Buat API key baru
3. Copy API key

---

## 🔒 Keamanan
- Token dan API key tidak disimpan di repository
- Menggunakan environment variable untuk keamanan
- File `.env` sudah di-ignore oleh git

---

## 📌 Catatan
Project ini dibuat untuk tujuan pembelajaran dan pengembangan skill backend Python.

---

## 📄 License
MIT License

---

**Author:**  
Ismet Maulana Azhary