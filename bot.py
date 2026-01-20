import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
import os
import socket

# ================= LOAD ENV =================
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ================= GEMINI CONFIG =================
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=""" 
    Kamu adalah chatbot Discord berbahasa Indonesia.
    Peran kamu:
    - Menjawab pertanyaan seputar IT, pemrograman, dan teknologi
    - Jawaban singkat, padat, dan mudah dipahami
    - Gunakan bahasa sopan dan ramah
    - Jika tidak tahu, katakan tidak tahu
    """
)

chat = model.start_chat()
# ================= DISCORD BOT =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.AutoShardedBot(
    command_prefix="/",
    intents=intents
)

# ================= EVENTS =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(
        f"Bot login sebagai {bot.user}\n"
        f"Shard Count : {bot.shard_count}\n"
        f"Node        : {socket.gethostname()}"
    )

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Auto reply
    if "halo bot" in message.content.lower():
        await message.channel.send("Halo juga 👋")

    await bot.process_commands(message)

# ================= BASIC COMMANDS =================
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000, 2)
    await ctx.send(
        f"🏓 **Pong!**\n"
        f"🧩 Shard   : {ctx.guild.shard_id if ctx.guild else 'N/A'}\n"
        f"⏱ Latency : {latency} ms"
    )

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="🤖 Discord AI Bot",
        description="Bot Discord dengan Gemini AI",
        color=discord.Color.blue()
    )
    embed.add_field(name="Author", value="Ismet", inline=False)
    embed.add_field(
        name="Teknis",
        value=f"Shard: {ctx.guild.shard_id}\nNode: {socket.gethostname()}",
        inline=False
    )
    await ctx.send(embed=embed)

# ================= GEMINI CHAT COMMAND =================
@bot.command()
async def ai(ctx, *, prompt: str):
    """
    Chat dengan Gemini AI
    Contoh: !ai jelaskan shard discord
    """
    try:
        await ctx.typing()
        response = chat.send_message(prompt)
        await ctx.send(response.text[:2000])
    except Exception as e:
        await ctx.send("❌ Terjadi error saat memproses AI.")

# ================= SLASH COMMAND =================
@bot.tree.command(name="ai", description="Chat dengan Gemini AI")
async def ai_slash(interaction: discord.Interaction, prompt: str):
    try:
        await interaction.response.defer(thinking=True)
        response = chat.send_message(prompt)
        await interaction.followup.send(response.text[:2000])
    except Exception:
        await interaction.followup.send("❌ Terjadi error pada AI.")

# ================= MODERATION =================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Tidak ada alasan"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} telah di-kick.\nAlasan: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Tidak ada alasan"):
    await ctx.send(f"⚠️ {member.mention} diperingatkan.\nAlasan: {reason}")

# ================= ERROR HANDLER =================
@kick.error
@warn.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Kamu tidak punya izin untuk command ini.")

# ================= RUN =================
bot.run(DISCORD_TOKEN)
