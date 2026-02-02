# 🤖 Discord AI Chatbot

Bot Discord multifungsi dengan **Groq AI** (LLaMA, Mixtral, Gemma) untuk chat, translate, code explain, dan berbagai fitur menarik lainnya!

---

## ✨ Fitur Utama

### 💬 AI Chat
- Chat langsung dengan AI tanpa command
- Conversation memory per user
- Multiple AI models & personas
- Adjustable creativity (temperature)

### 🛠️ Tools Commands
| Command | Deskripsi |
|---------|-----------|
| `!translate <lang> <teks>` | Terjemahkan ke bahasa lain |
| `!summarize <teks>` | Ringkas teks panjang |
| `!explain <kode>` | Jelaskan kode programming |
| `!imagine <deskripsi>` | Generate AI image prompt |

### 🎮 Fun Commands
| Command | Deskripsi |
|---------|-----------|
| `!quiz [topik]` | Quiz random dengan berbagai topik |
| `!roast [@user]` | Roast seseorang dengan humor |
| `!motivate` | Dapatkan motivasi harian |
| `!joke` | Random jokes lucu |

### ⚙️ Settings Commands
| Command | Deskripsi |
|---------|-----------|
| `!help` | Tampilkan semua command |
| `!model [nama]` | Lihat/ganti model AI |
| `!persona [nama]` | Lihat/ganti persona AI |
| `!temp [0.0-1.0]` | Atur kreativitas AI |
| `!clear` | Hapus riwayat chat |
| `!history` | Lihat jumlah riwayat |
| `!status` | Status bot dan info |

### 🤖 Available Models
- `llama` - LLaMA 3.3 70B Versatile
- `mixtral` - Mixtral 8x7B 32K
- `gemma` - Gemma 2 9B IT
- `llama-small` - LLaMA 3.1 8B Instant

### 🎭 Available Personas
- `default` - Asisten umum
- `programmer` - Expert coding
- `creative` - Penulis kreatif
- `teacher` - Guru sabar

### 🌐 Supported Languages
`id` Indonesian | `en` English | `jp` Japanese | `kr` Korean | `zh` Chinese | `ar` Arabic | `es` Spanish | `fr` French | `de` German

---

## 🛠️ Tech Stack
- **Python 3.12**
- **discord.py**
- **python-dotenv**
- **groq**

---

## 📂 Struktur Project
```
bot-discord/
├── groq_chatbot.py
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
GROQ_API_KEY=your_groq_api_key
```

### 5️⃣ Jalankan Bot
```bash
python groq_chatbot.py
```

---

## 🔑 Mendapatkan API Keys

### Discord Bot Token
1. Buka [Discord Developer Portal](https://discord.com/developers/applications)
2. Buat aplikasi baru
3. Pergi ke menu "Bot"
4. Copy token bot

### Groq API Key
1. Buka [Groq Console](https://console.groq.com/keys)
2. Buat API key baru
3. Copy API key

---

## 🔒 Keamanan
- Token dan API key tidak disimpan di repository
- Menggunakan environment variable untuk keamanan
- File `.env` sudah di-ignore oleh git

---

## 📸 Screenshots

### Chat dengan AI
```
User: Jelaskan tentang Python
Bot: [Embed response dengan penjelasan lengkap]
```

### Quiz
```
!quiz programming
Bot: [Quiz tentang programming dengan 4 opsi jawaban]
```

---

## 📌 Catatan
Project ini dibuat untuk tujuan pembelajaran dan pengembangan skill backend Python.

---

## 📄 License
MIT License

---

**Author:**  
Ismet Maulana Azhary