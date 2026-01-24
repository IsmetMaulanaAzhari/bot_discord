import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai
import os
import socket
import datetime
import asyncio

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
# ================= AI MEMORY (PER USER) =================
user_chats = {}

def get_user_chat(user_id: int):
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat()
    return user_chats[user_id]
# ================= DISCORD BOT =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.AutoShardedBot(
    command_prefix="/",
    intents=intents,
    help_command=None  # Disable default help command
)

# Track bot start time for uptime
start_time = datetime.datetime.now()

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

@bot.command()
async def help(ctx):
    """Menampilkan daftar command yang tersedia."""
    embed = discord.Embed(
        title="📚 Daftar Command",
        description="Berikut adalah command yang tersedia:",
        color=discord.Color.green()
    )
    embed.add_field(
        name="🔧 Basic",
        value="`/ping` - Cek status bot\n`/info` - Info bot\n`/help` - Daftar command\n`/uptime` - Waktu aktif bot",
        inline=False
    )
    embed.add_field(
        name="🤖 AI",
        value="`/ai <prompt>` - Chat dengan Gemini AI",
        inline=False
    )
    embed.add_field(
        name="👤 User",
        value="`/avatar [@user]` - Lihat avatar\n`/userinfo [@user]` - Info user",
        inline=False
    )
    embed.add_field(
        name="🏠 Server",
        value="`/serverinfo` - Info server",
        inline=False
    )
    embed.add_field(
        name="🛡️ Moderation",
        value="`/kick @user [alasan]` - Kick member\n`/warn @user [alasan]` - Warn member\n`/clear <jumlah>` - Hapus pesan",
        inline=False
    )
    embed.set_footer(text="Gunakan prefix / untuk semua command")
    await ctx.send(embed=embed)

@bot.command()
async def uptime(ctx):
    """Menampilkan waktu aktif bot."""
    now = datetime.datetime.now()
    delta = now - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    
    await ctx.send(
        f"⏱️ **Uptime**\n"
        f"🗓️ {days} hari, {hours} jam, {minutes} menit, {seconds} detik"
    )

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Menampilkan avatar user."""
    member = member or ctx.author
    embed = discord.Embed(
        title=f"Avatar {member.display_name}",
        color=discord.Color.purple()
    )
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """Menampilkan informasi user."""
    member = member or ctx.author
    roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
    
    embed = discord.Embed(
        title=f"👤 Info User - {member.display_name}",
        color=member.color
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="Bergabung Server", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Akun Dibuat", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles) if roles else "Tidak ada", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    """Menampilkan informasi server."""
    guild = ctx.guild
    
    embed = discord.Embed(
        title=f"🏠 Info Server - {guild.name}",
        color=discord.Color.gold()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Dibuat", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
    embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
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
        chat = get_user_chat(ctx.author.id)  # ✅ AMBIL CHAT USER
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

@bot.tree.command(name="avatar", description="Lihat avatar user")
async def avatar_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"Avatar {member.display_name}",
        color=discord.Color.purple()
    )
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Lihat info user")
async def userinfo_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    roles = [role.mention for role in member.roles[1:]]
    
    embed = discord.Embed(
        title=f"👤 Info User - {member.display_name}",
        color=member.color
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="Bergabung Server", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Akun Dibuat", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles) if roles else "Tidak ada", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Lihat info server")
async def serverinfo_slash(interaction: discord.Interaction):
    guild = interaction.guild
    
    embed = discord.Embed(
        title=f"🏠 Info Server - {guild.name}",
        color=discord.Color.gold()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Dibuat", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    await interaction.response.send_message(embed=embed)

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

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Hapus sejumlah pesan dari channel."""
    if amount < 1 or amount > 100:
        await ctx.send("❌ Jumlah harus antara 1-100.")
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 untuk hapus command juga
    msg = await ctx.send(f"✅ Berhasil menghapus {len(deleted) - 1} pesan.")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
async def poll(ctx, question: str, *options):
    """Buat polling sederhana. Contoh: /poll "Pertanyaan?" "Opsi 1" "Opsi 2" """
    if len(options) < 2:
        await ctx.send("❌ Minimal 2 opsi diperlukan.")
        return
    if len(options) > 10:
        await ctx.send("❌ Maksimal 10 opsi.")
        return
    
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    description = "\n".join([f"{reactions[i]} {option}" for i, option in enumerate(options)])
    embed = discord.Embed(
        title=f"📊 {question}",
        description=description,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Poll oleh {ctx.author.display_name}")
    
    poll_msg = await ctx.send(embed=embed)
    for i in range(len(options)):
        await poll_msg.add_reaction(reactions[i])

# ================= ERROR HANDLER =================
@kick.error
@warn.error
@clear.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Argumen tidak valid. Cek format command.")

# ================= RUN =================
bot.run(DISCORD_TOKEN)
