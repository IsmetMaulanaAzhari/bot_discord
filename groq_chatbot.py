import os
import discord
from discord.ext import commands
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import random

# ================= LOAD ENV =================
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# ================= GROQ CONFIG =================
groq_client = Groq(api_key=GROQ_API_KEY)

# Available models
MODELS = {
    "llama": "llama-3.3-70b-versatile",
    "mixtral": "mixtral-8x7b-32768",
    "gemma": "gemma2-9b-it",
    "llama-small": "llama-3.1-8b-instant"
}

# Default settings
current_model = "llama"
conversation_history = {}  # Per-user conversation history
MAX_HISTORY = 20  # Max messages to remember per user
current_temperature = 0.7  # AI creativity level (0.0 - 1.0)

# Language codes for translation
LANGUAGES = {
    "id": "Bahasa Indonesia",
    "en": "English",
    "jp": "Japanese",
    "kr": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "de": "German"
}

# System prompts
SYSTEM_PROMPTS = {
    "default": "Kamu adalah asisten AI yang helpful, ramah, dan berbahasa Indonesia. Jawab dengan jelas dan informatif.",
    "programmer": "Kamu adalah programmer expert yang membantu coding. Berikan contoh kode yang bersih dan penjelasan teknis.",
    "creative": "Kamu adalah penulis kreatif. Bantu dengan ide-ide kreatif, cerita, dan konten yang menarik.",
    "teacher": "Kamu adalah guru yang sabar. Jelaskan konsep dengan cara yang mudah dipahami untuk pemula."
}
current_persona = "default"

# ================= DISCORD BOT =================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= HELPER FUNCTIONS =================
def get_user_history(user_id):
    """Get or create conversation history for a user."""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    return conversation_history[user_id]

def add_to_history(user_id, role, content):
    """Add message to user's conversation history."""
    history = get_user_history(user_id)
    history.append({"role": role, "content": content})
    # Keep only last MAX_HISTORY messages
    if len(history) > MAX_HISTORY:
        conversation_history[user_id] = history[-MAX_HISTORY:]

def clear_history(user_id):
    """Clear conversation history for a user."""
    if user_id in conversation_history:
        conversation_history[user_id] = []

async def get_ai_response(user_id, prompt, system_override=None):
    """Get AI response from Groq with conversation history."""
    history = get_user_history(user_id)
    
    system_prompt = system_override if system_override else SYSTEM_PROMPTS[current_persona]
    messages = [{"role": "system", "content": system_prompt}]
    
    if not system_override:  # Only include history for normal chat
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    
    response = groq_client.chat.completions.with_raw_response.create(
        messages=messages,
        model=MODELS[current_model],
        temperature=current_temperature,
        max_tokens=2048
    )
    
    return response

async def quick_ai_request(prompt, system_prompt):
    """Quick AI request without history."""
    response = groq_client.chat.completions.with_raw_response.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model=MODELS[current_model],
        temperature=current_temperature,
        max_tokens=2048
    )
    return response

# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"""
╔══════════════════════════════════════╗
║  🤖 Groq AI Chatbot Ready!           ║
╠══════════════════════════════════════╣
║  Bot: {bot.user}
║  Model: {MODELS[current_model]}
║  Persona: {current_persona}
║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╚══════════════════════════════════════╝
    """)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # If message starts with command prefix, don't process as chat
    if message.content.startswith("!"):
        return
    
    # AI Chat
    async with message.channel.typing():
        try:
            user_id = str(message.author.id)
            
            # Get AI response
            response = await asyncio.to_thread(
                get_ai_response, user_id, message.content
            )
            
            # Parse response
            headers = response.headers
            remaining_tokens = headers.get('x-ratelimit-remaining-tokens', 'N/A')
            remaining_requests = headers.get('x-ratelimit-remaining-requests', 'N/A')
            
            completion = response.parse()
            ai_text = completion.choices[0].message.content
            
            # Save to history
            add_to_history(user_id, "user", message.content)
            add_to_history(user_id, "assistant", ai_text)
            
            # Format response with embed
            embed = discord.Embed(
                description=ai_text[:4000],
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_footer(
                text=f"🎯 {MODELS[current_model]} | 🎭 {current_persona} | 🎫 {remaining_tokens} tokens | 📡 {remaining_requests} req"
            )
            
            await message.reply(embed=embed, mention_author=False)
            
            # If response is too long, send remaining as follow-up
            if len(ai_text) > 4000:
                await message.channel.send(ai_text[4000:])
                
        except Exception as e:
            print(f"Error: {e}")
            await message.reply(f"❌ Error: {str(e)[:200]}", mention_author=False)

# ================= COMMANDS =================
@bot.command()
async def help(ctx):
    """Menampilkan daftar command."""
    embed = discord.Embed(
        title="📚 Groq AI Chatbot - Help",
        description="Chat langsung tanpa command untuk berbicara dengan AI!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="💬 Chat",
        value="Ketik pesan langsung untuk chat dengan AI",
        inline=False
    )
    embed.add_field(
        name="🔧 Settings",
        value=(
            "`!help` - Tampilkan bantuan\n"
            "`!model [nama]` - Lihat/ganti model AI\n"
            "`!persona [nama]` - Lihat/ganti persona AI\n"
            "`!temp [0.0-1.0]` - Atur kreativitas AI\n"
            "`!clear` - Hapus riwayat\n"
            "`!history` - Lihat riwayat\n"
            "`!status` - Status bot"
        ),
        inline=False
    )
    embed.add_field(
        name="🛠️ Tools",
        value=(
            "`!translate <lang> <teks>` - Terjemahkan teks\n"
            "`!summarize <teks>` - Ringkas teks\n"
            "`!explain <kode>` - Jelaskan kode\n"
            "`!imagine <deskripsi>` - Generate image prompt"
        ),
        inline=False
    )
    embed.add_field(
        name="🎮 Fun",
        value=(
            "`!quiz [topik]` - Quiz random\n"
            "`!roast [@user]` - Roast seseorang\n"
            "`!motivate` - Motivasi harian\n"
            "`!joke` - Random jokes"
        ),
        inline=False
    )
    embed.add_field(
        name="🌐 Languages",
        value="`id` `en` `jp` `kr` `zh` `ar` `es` `fr` `de`",
        inline=False
    )
    embed.set_footer(text="Prefix: ! | Chat langsung tanpa prefix untuk AI")
    await ctx.send(embed=embed)

@bot.command()
async def model(ctx, name: str = None):
    """Lihat atau ganti model AI."""
    global current_model
    
    if name is None:
        models_list = "\n".join([
            f"{'✅' if k == current_model else '⬜'} `{k}` - {v}" 
            for k, v in MODELS.items()
        ])
        embed = discord.Embed(
            title="🤖 Available Models",
            description=models_list,
            color=discord.Color.purple()
        )
        embed.set_footer(text="Gunakan !model <nama> untuk mengganti")
        await ctx.send(embed=embed)
    elif name.lower() in MODELS:
        current_model = name.lower()
        await ctx.send(f"✅ Model berhasil diganti ke **{MODELS[current_model]}**")
    else:
        await ctx.send(f"❌ Model tidak ditemukan. Pilih: {', '.join(MODELS.keys())}")

@bot.command()
async def persona(ctx, name: str = None):
    """Lihat atau ganti persona AI."""
    global current_persona
    
    if name is None:
        personas_list = "\n".join([
            f"{'✅' if k == current_persona else '⬜'} `{k}` - {v[:60]}..." 
            for k, v in SYSTEM_PROMPTS.items()
        ])
        embed = discord.Embed(
            title="🎭 Available Personas",
            description=personas_list,
            color=discord.Color.orange()
        )
        embed.set_footer(text="Gunakan !persona <nama> untuk mengganti")
        await ctx.send(embed=embed)
    elif name.lower() in SYSTEM_PROMPTS:
        current_persona = name.lower()
        await ctx.send(f"✅ Persona berhasil diganti ke **{current_persona}**")
    else:
        await ctx.send(f"❌ Persona tidak ditemukan. Pilih: {', '.join(SYSTEM_PROMPTS.keys())}")

@bot.command()
async def clear(ctx):
    """Hapus riwayat percakapan."""
    user_id = str(ctx.author.id)
    clear_history(user_id)
    await ctx.send("🗑️ Riwayat percakapan telah dihapus!")

@bot.command()
async def history(ctx):
    """Lihat jumlah riwayat chat."""
    user_id = str(ctx.author.id)
    history = get_user_history(user_id)
    count = len(history)
    await ctx.send(f"📝 Kamu memiliki **{count}** pesan dalam riwayat (max: {MAX_HISTORY})")

@bot.command()
async def status(ctx):
    """Status bot dan info."""
    embed = discord.Embed(
        title="📊 Bot Status",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    embed.add_field(name="🤖 Model", value=MODELS[current_model], inline=True)
    embed.add_field(name="🎭 Persona", value=current_persona, inline=True)
    embed.add_field(name="🌡️ Temperature", value=f"{current_temperature}", inline=True)
    embed.add_field(name="👥 Active Users", value=len(conversation_history), inline=True)
    embed.add_field(name="💬 Your History", value=f"{len(get_user_history(str(ctx.author.id)))} messages", inline=True)
    embed.add_field(name="⏰ Uptime", value="Running", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def temp(ctx, value: float = None):
    """Atur temperature/kreativitas AI (0.0 - 1.0)."""
    global current_temperature
    
    if value is None:
        await ctx.send(f"🌡️ Temperature saat ini: **{current_temperature}**\n💡 Gunakan `!temp <0.0-1.0>` untuk mengubah")
        return
    
    if 0.0 <= value <= 1.0:
        current_temperature = value
        creativity = "🧊 Sangat Fokus" if value < 0.3 else "⚖️ Seimbang" if value < 0.7 else "🔥 Sangat Kreatif"
        await ctx.send(f"✅ Temperature diubah ke **{value}** ({creativity})")
    else:
        await ctx.send("❌ Temperature harus antara 0.0 - 1.0")

# ================= UTILITY COMMANDS =================
@bot.command()
async def translate(ctx, lang: str, *, text: str):
    """Terjemahkan teks ke bahasa lain."""
    if lang.lower() not in LANGUAGES:
        langs = ", ".join([f"`{k}`" for k in LANGUAGES.keys()])
        await ctx.send(f"❌ Bahasa tidak valid. Pilih: {langs}")
        return
    
    async with ctx.typing():
        try:
            target_lang = LANGUAGES[lang.lower()]
            system = f"Kamu adalah penerjemah profesional. Terjemahkan teks berikut ke {target_lang}. Hanya berikan hasil terjemahan, tanpa penjelasan."
            
            response = await asyncio.to_thread(
                quick_ai_request, text, system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title=f"🌐 Terjemahan ke {target_lang}",
                color=discord.Color.teal()
            )
            embed.add_field(name="📝 Original", value=text[:1000], inline=False)
            embed.add_field(name="🔄 Terjemahan", value=result[:1000], inline=False)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

@bot.command()
async def summarize(ctx, *, text: str):
    """Ringkas teks panjang."""
    async with ctx.typing():
        try:
            system = "Kamu adalah asisten yang ahli meringkas. Buat ringkasan singkat dan padat dari teks berikut dalam Bahasa Indonesia. Fokus pada poin-poin penting."
            
            response = await asyncio.to_thread(
                quick_ai_request, text, system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title="📋 Ringkasan",
                description=result[:4000],
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Original: {len(text)} chars → Summary: {len(result)} chars")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

@bot.command()
async def explain(ctx, *, code: str):
    """Jelaskan kode programming."""
    async with ctx.typing():
        try:
            system = "Kamu adalah programmer expert. Jelaskan kode berikut dengan bahasa Indonesia yang mudah dipahami. Jelaskan: 1) Apa yang dilakukan kode ini, 2) Bagaimana cara kerjanya, 3) Konsep penting yang digunakan."
            
            response = await asyncio.to_thread(
                quick_ai_request, code, system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title="💻 Penjelasan Kode",
                description=result[:4000],
                color=discord.Color.dark_green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

@bot.command()
async def imagine(ctx, *, description: str):
    """Generate prompt untuk AI image generator."""
    async with ctx.typing():
        try:
            system = """Kamu adalah expert prompt engineer untuk AI image generator seperti Midjourney, DALL-E, dan Stable Diffusion.
Buatkan prompt yang detail dan efektif berdasarkan deskripsi user.
Format output:
1. Prompt utama dalam bahasa Inggris
2. Negative prompt
3. Style recommendations
4. Parameter suggestions (aspect ratio, etc)"""
            
            response = await asyncio.to_thread(
                quick_ai_request, description, system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title="🎨 AI Image Prompt",
                description=result[:4000],
                color=discord.Color.magenta()
            )
            embed.set_footer(text="Copy prompt ini ke Midjourney/DALL-E/Stable Diffusion")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

@bot.command()
async def quiz(ctx, topic: str = "random"):
    """Generate quiz pertanyaan."""
    async with ctx.typing():
        try:
            topics = ["programming", "science", "history", "geography", "technology", "math"]
            if topic == "random":
                topic = random.choice(topics)
            
            system = f"""Buat 1 soal quiz tentang {topic} dalam Bahasa Indonesia.
Format:
📝 **Pertanyaan:** [pertanyaan]

A) [opsi A]
B) [opsi B]
C) [opsi C]
D) [opsi D]

||✅ Jawaban: [huruf jawaban] - [penjelasan singkat]||

Note: Jawaban harus di-spoiler dengan ||"""
            
            response = await asyncio.to_thread(
                quick_ai_request, f"Buat quiz tentang {topic}", system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title=f"🧠 Quiz: {topic.title()}",
                description=result[:4000],
                color=discord.Color.gold()
            )
            embed.set_footer(text="Klik spoiler untuk melihat jawaban!")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    """Roast seseorang dengan humor."""
    member = member or ctx.author
    
    async with ctx.typing():
        try:
            system = "Kamu adalah komedian yang ahli roasting. Buat roast yang lucu dan friendly (tidak kasar/menyinggung SARA) untuk seseorang. Gunakan bahasa Indonesia gaul. Maksimal 3 kalimat."
            
            response = await asyncio.to_thread(
                quick_ai_request, f"Roast seseorang bernama {member.display_name}", system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title=f"🔥 Roast untuk {member.display_name}",
                description=result[:2000],
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

@bot.command()
async def motivate(ctx):
    """Dapatkan motivasi dari AI."""
    async with ctx.typing():
        try:
            system = "Kamu adalah motivator inspiratif. Berikan 1 quote motivasi original (bukan quote terkenal) dalam Bahasa Indonesia yang powerful dan menyentuh. Tambahkan emoji yang relevan."
            
            response = await asyncio.to_thread(
                quick_ai_request, "Berikan motivasi", system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title="✨ Motivasi Hari Ini",
                description=result[:2000],
                color=discord.Color.gold()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

@bot.command()
async def joke(ctx):
    """Dapatkan jokes dari AI."""
    async with ctx.typing():
        try:
            system = "Kamu adalah komedian Indonesia. Ceritakan 1 jokes/lelucon yang lucu dalam Bahasa Indonesia. Bisa berupa pun, wordplay, atau jokes situasional. Pastikan family-friendly."
            
            response = await asyncio.to_thread(
                quick_ai_request, "Ceritakan jokes lucu", system
            )
            
            completion = response.parse()
            result = completion.choices[0].message.content
            
            embed = discord.Embed(
                title="😂 Jokes",
                description=result[:2000],
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)[:200]}")

# ================= RUN =================
bot.run(DISCORD_TOKEN)