# 🤖 Discord AI Chatbot

Bot Discord multifungsi dengan **Groq AI** & **Gemini AI** untuk chat, games, utilities, dan berbagai fitur menarik lainnya! Dilengkapi dengan **Interactive Menu**, **AI Model Selector**, **Leveling System**, dan **Mini Games**!

---

## ✨ Fitur Utama

### ⭐ Leveling System (NEW!)
Sistem XP dan level otomatis!

| Command | Deskripsi |
|---------|-----------|
| `/rank [@user]` | Lihat level & XP dengan progress bar |
| `/leaderboard` | Top 10 user dengan XP tertinggi |

**Cara Dapat XP:**
- 📝 Kirim pesan: +1-5 XP
- 🧠 Menang trivia: +25 XP
- 🔤 Menang scramble: +20 XP
- 🔢 Counting benar: +2 XP

### 🎲 Mini Games (NEW!)
Game interaktif dengan tombol dan XP rewards!

| Command | Deskripsi |
|---------|-----------|
| `/trivia` | Quiz dengan tombol pilihan jawaban |
| `/scramble` | Susun kata yang diacak |
| `/setcount` | Set counting channel |
| `/count` | Lihat angka saat ini |

### 🎁 Giveaway System (NEW!)
| Command | Deskripsi |
|---------|-----------|
| `/giveaway <waktu> <hadiah>` | Buat giveaway dengan tombol join |
| `/remind <waktu> <pesan>` | Set reminder |

### 🎮 Fun & Games
Mainkan berbagai game seru langsung di Discord:

| Command | Deskripsi |
|---------|-----------|
| `/8ball <pertanyaan>` | Tanya magic 8ball |
| `/coinflip` | Lempar koin |
| `/roll [sisi]` | Lempar dadu (default 6 sisi) |
| `/choose <opsi1> <opsi2>...` | Pilih random dari opsi |
| `/rps <batu/gunting/kertas>` | Main suit dengan bot |

### 📊 Utility Commands
Tools berguna untuk sehari-hari:

| Command | Deskripsi |
|---------|-----------|
| `/timer <waktu>` | Set timer (5s, 10m, 1h) |
| `/remind <waktu> <pesan>` | Set reminder (maks 7 hari) |
| `/math <expr>` | Kalkulator (2+2, 10*5) |
| `/say <pesan>` | Bot kirim pesan |
| `/embed "judul" deskripsi` | Buat embed custom |
| `/afk [alasan]` | Set status AFK |

### 👤 User Commands
| Command | Deskripsi |
|---------|-----------|
| `/whois [@user]` | Info lengkap user + permissions |
| `/banner [@user]` | Lihat banner user |
| `/avatar [@user]` | Lihat avatar user |
| `/userinfo [@user]` | Info user |

### 🏠 Server Commands
| Command | Deskripsi |
|---------|-----------|
| `/membercount` | Statistik member server |
| `/servericon` | Lihat icon server |
| `/serverinfo` | Info lengkap server |

### 🤖 AI Model Selector
Pilih model AI sesuai kebutuhan dengan dropdown interaktif:

| Command | Deskripsi |
|---------|-----------|
| `/aimodel` | Buka menu pilih model AI |
| `/models` | Lihat daftar model tersedia |
| `/reset_ai` | Reset memory AI |

**Available Gemini Models:**
| Model | Nama | Deskripsi |
|-------|------|-----------|
| ⚡ Flash | `gemini-2.0-flash` | Fast & efficient |
| 🪶 Flash-Lite | `gemini-2.0-flash-lite` | Lightweight & quick |
| 💎 Pro | `gemini-1.5-pro` | Most capable |
| 🚀 Flash-8B | `gemini-1.5-flash-8b` | Compact & fast |

### 🎮 Interactive Menus
Bot ini dilengkapi dengan menu interaktif menggunakan Discord UI Components:

| Command | Deskripsi |
|---------|-----------|
| `/menu` | Menu utama dengan tombol interaktif |
| `/helpmenu` | Menu bantuan dengan dropdown (9 kategori!) |
| `/roles` | Role selector dengan dropdown |

**Fitur Menu:**
- 🔘 **Buttons** - Klik untuk aksi cepat
- 📋 **Dropdown/Select Menu** - Pilih dari daftar opsi
- ✅ **Confirm Dialog** - Konfirmasi sebelum aksi penting
- ⏱️ **Auto Timeout** - Menu expire otomatis

### 💬 AI Chat
- Chat langsung dengan AI tanpa command
- Conversation memory per user
- Multiple AI models (switchable!)
- Support Gemini & Groq AI

### 🛠️ Tools Commands (Groq Bot)
| Command | Deskripsi |
|---------|-----------|
| `!translate <lang> <teks>` | Terjemahkan ke bahasa lain |
| `!summarize <teks>` | Ringkas teks panjang |
| `!explain <kode>` | Jelaskan kode programming |
| `!imagine <deskripsi>` | Generate AI image prompt |

### 🎲 Fun Commands (Groq Bot)
| Command | Deskripsi |
|---------|-----------|
| `!quiz [topik]` | Quiz random dengan berbagai topik |
| `!roast [@user]` | Roast seseorang dengan humor |
| `!motivate` | Dapatkan motivasi harian |
| `!joke` | Random jokes lucu |

### 🛡️ Moderation Commands
| Command | Deskripsi |
|---------|-----------|
| `/kick @user [alasan]` | Kick member |
| `/warn @user [alasan]` | Warn member |
| `/clear <jumlah>` | Hapus pesan (1-100) |
| `/poll "?" "A" "B"` | Buat polling |

### 🤖 Available Models

**Gemini AI (bot.py):**
| Model | Deskripsi |
|-------|-----------|
| ⚡ `flash` | Gemini 2.0 Flash - Fast & efficient |
| 🪶 `flash-lite` | Gemini 2.0 Flash Lite - Lightweight |
| 💎 `pro` | Gemini 1.5 Pro - Most capable |
| 🚀 `flash-8b` | Gemini 1.5 Flash 8B - Compact |

**Groq AI (groq_chatbot.py):**
| Model | Deskripsi |
|-------|-----------|
| `llama` | LLaMA 3.3 70B Versatile |
| `mixtral` | Mixtral 8x7B 32K |
| `gemma` | Gemma 2 9B IT |
| `llama-small` | LLaMA 3.1 8B Instant |

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
- **discord.py** (with UI Components)
- **python-dotenv**
- **google-generativeai** (Gemini)
- **groq** (LLaMA, Mixtral)

---

## 📂 Struktur Project
```
bot-discord/
├── bot.py              # Gemini AI Bot (Main)
├── groq_chatbot.py     # Groq AI Bot
├── gemini_chatbot.py   # CLI Gemini Chat
├── tes.py              # Test bot
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
GEMINI_API_KEY=your_gemini_api_key
```

### 5️⃣ Jalankan Bot
```bash
# Untuk Groq AI Bot
python groq_chatbot.py

# Untuk Gemini AI Bot (dengan Interactive Menu)
python bot.py
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

## 📸 Screenshots

### Leveling System
```
/rank
┌─────────────────────────────────┐
│     📊 Rank - Username          │
├─────────────────────────────────┤
│ ⭐ Level: 5     ✨ XP: 2500/3600│
│                                 │
│ 📈 Progress:                    │
│ ████████░░ 69.4%                │
└─────────────────────────────────┘

/leaderboard
┌─────────────────────────────────┐
│     🏆 XP Leaderboard           │
├─────────────────────────────────┤
│ 🥇 User1 - Level 10 (10000 XP)  │
│ 🥈 User2 - Level 8 (6400 XP)    │
│ 🥉 User3 - Level 5 (2500 XP)    │
│ 4. User4 - Level 3 (900 XP)     │
│ 5. User5 - Level 2 (400 XP)     │
└─────────────────────────────────┘
```

### Trivia Game
```
/trivia
┌─────────────────────────────────┐
│     🧠 Trivia                   │
├─────────────────────────────────┤
│ Bahasa pemrograman apa yang     │
│ dibuat oleh Guido van Rossum?   │
│                                 │
│ [Java] [Python] [C++] [Ruby]    │
└─────────────────────────────────┘

[Setelah jawab benar]
✅ **Benar!** +25 XP
```

### Giveaway System
```
/giveaway 1h Nitro Classic
┌─────────────────────────────────┐
│     🎉 GIVEAWAY 🎉              │
├─────────────────────────────────┤
│ Hadiah: Nitro Classic           │
│ Host: @Admin                    │
│ Berakhir: dalam 1 jam           │
│                                 │
│ [🎉 Join Giveaway (15)]         │
└─────────────────────────────────┘

[Setelah berakhir]
🎊 GIVEAWAY ENDED 🎊
🏆 Pemenang: @LuckyUser
Selamat! 🎉
```

### Fun Games
```
/8ball Apakah hari ini hari keberuntungan?
┌─────────────────────────────────┐
│     🎱 Magic 8-Ball             │
├─────────────────────────────────┤
│ ❓ Pertanyaan:                  │
│ Apakah hari ini keberuntungan?  │
│                                 │
│ 🔮 Jawaban:                     │
│ 🟢 Ya, pasti!                   │
└─────────────────────────────────┘

/rps batu
┌─────────────────────────────────┐
│  ✊✌️✋ Batu Gunting Kertas     │
├─────────────────────────────────┤
│ Kamu: 🪨 Batu  │  Bot: ✂️ Gunting │
│                                 │
│ Hasil: 🎉 **Kamu Menang!**      │
└─────────────────────────────────┘
```

### AFK System
```
/afk Makan siang dulu
💤 @User sekarang AFK: **Makan siang dulu**

[Saat user di-mention]
💤 User sedang AFK: **Makan siang dulu**

[Saat user kembali chat]
👋 Welcome back @User! Kamu AFK selama **15 menit**.
```

### AI Model Selector
```
/aimodel
┌─────────────────────────────────┐
│     🤖 AI Model Selector        │
├─────────────────────────────────┤
│ Current: ⚡ gemini-2.0-flash    │
│                                 │
│ [🤖 Pilih model AI...        ▼] │
│  ├ ⚡ FLASH - Fast & efficient  │
│  ├ 🪶 FLASH-LITE - Lightweight  │
│  ├ 💎 PRO - Most capable        │
│  └ 🚀 FLASH-8B - Compact        │
├─────────────────────────────────┤
│ [📊 Model Info] [🗑️ Reset All]  │
└─────────────────────────────────┘
```

### Interactive Menu
```
/menu
┌─────────────────────────────┐
│     🎮 Main Menu            │
├─────────────────────────────┤
│ [📊 Status] [🤖 AI] [👤 Profile] │
│ [🏠 Server] [📚 Help] [❌ Close]  │
└─────────────────────────────┘
```

### Help Menu dengan Dropdown
```
/helpmenu
┌─────────────────────────────┐
│     📚 Help Menu            │
├─────────────────────────────┤
│ [📋 Pilih kategori...    ▼] │
│  ├ 🔧 Basic                 │
│  ├ 🤖 AI                    │
│  ├ 👤 User                  │
│  ├ 🏠 Server                │
│  ├ 🛡️ Moderation           │
│  └ 📊 Utility               │
└─────────────────────────────┘
```

### Chat dengan AI
```
User: /ai Jelaskan tentang Python
Bot: [Embed response dengan penjelasan lengkap]
     Model: gemini-2.0-flash
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