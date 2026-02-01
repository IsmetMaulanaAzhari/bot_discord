import os
import discord
from discord.ext import commands
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import asyncio

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

async def get_ai_response(user_id, prompt):
    """Get AI response from Groq with conversation history."""
    history = get_user_history(user_id)
    
    messages = [{"role": "system", "content": SYSTEM_PROMPTS[current_persona]}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    
    response = groq_client.chat.completions.with_raw_response.create(
        messages=messages,
        model=MODELS[current_model],
        temperature=0.7,
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
        name="🔧 Commands",
        value=(
            "`!help` - Tampilkan bantuan ini\n"
            "`!model [nama]` - Lihat/ganti model AI\n"
            "`!persona [nama]` - Lihat/ganti persona AI\n"
            "`!clear` - Hapus riwayat percakapan\n"
            "`!history` - Lihat jumlah riwayat chat\n"
            "`!status` - Status bot dan kuota"
        ),
        inline=False
    )
    embed.add_field(
        name="🤖 Models",
        value="\n".join([f"`{k}` - {v}" for k, v in MODELS.items()]),
        inline=False
    )
    embed.add_field(
        name="🎭 Personas",
        value="\n".join([f"`{k}` - {v[:50]}..." for k, v in SYSTEM_PROMPTS.items()]),
        inline=False
    )
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
    embed.add_field(name="👥 Active Users", value=len(conversation_history), inline=True)
    embed.add_field(name="💬 Your History", value=f"{len(get_user_history(str(ctx.author.id)))} messages", inline=True)
    embed.add_field(name="⏰ Uptime", value="Running", inline=True)
    await ctx.send(embed=embed)

# ================= RUN =================
bot.run(DISCORD_TOKEN)