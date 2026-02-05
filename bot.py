import discord
from discord.ext import commands
from discord import ui, app_commands
from dotenv import load_dotenv
import google.generativeai as genai
import os
import socket
import datetime
import asyncio
import random
import re

# ================= LOAD ENV =================
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ================= GEMINI CONFIG =================
genai.configure(api_key=GEMINI_API_KEY)

# Available Gemini Models
GEMINI_MODELS = {
    "flash": {
        "name": "gemini-2.0-flash",
        "description": "Fast & efficient",
        "emoji": "⚡"
    },
    "flash-lite": {
        "name": "gemini-2.0-flash-lite",
        "description": "Lightweight & quick",
        "emoji": "🪶"
    },
    "pro": {
        "name": "gemini-1.5-pro",
        "description": "Most capable",
        "emoji": "💎"
    },
    "flash-8b": {
        "name": "gemini-1.5-flash-8b",
        "description": "Compact & fast",
        "emoji": "🚀"
    }
}

# Current settings
current_gemini_model = "flash"

def create_model(model_key: str):
    """Create a Gemini model with system instruction."""
    return genai.GenerativeModel(
        model_name=GEMINI_MODELS[model_key]["name"],
        system_instruction="""
        Kamu adalah chatbot Discord berbahasa Indonesia.
        Peran kamu:
        - Menjawab pertanyaan seputar IT, pemrograman, dan teknologi
        - Jawaban singkat, padat, dan mudah dipahami
        - Gunakan bahasa sopan dan ramah
        - Jika tidak tahu, katakan tidak tahu
        """
    )

model = create_model(current_gemini_model)
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

# AFK users storage
afk_users = {}

# ================= INTERACTIVE MENUS =================

# Help Menu Dropdown
class HelpSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🔧 Basic", value="basic", description="Ping, Info, Uptime", emoji="🔧"),
            discord.SelectOption(label="🤖 AI", value="ai", description="Chat dengan Gemini AI", emoji="🤖"),
            discord.SelectOption(label="👤 User", value="user", description="Avatar, User Info, Whois", emoji="👤"),
            discord.SelectOption(label="🏠 Server", value="server", description="Server Info, Icon", emoji="🏠"),
            discord.SelectOption(label="🛡️ Moderation", value="mod", description="Kick, Warn, Clear", emoji="🛡️"),
            discord.SelectOption(label="📊 Utility", value="utility", description="Poll, Timer, Remind", emoji="📊"),
            discord.SelectOption(label="🎮 Fun", value="fun", description="8ball, Coinflip, RPS", emoji="🎮"),
            discord.SelectOption(label="🎲 Games", value="games", description="Trivia, Scramble, Count", emoji="🎲"),
            discord.SelectOption(label="⭐ Leveling", value="leveling", description="Rank, Leaderboard, XP", emoji="⭐"),
        ]
        super().__init__(placeholder="📚 Pilih kategori command...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        embeds = {
            "basic": discord.Embed(
                title="🔧 Basic Commands",
                description=(
                    "`/ping` - Cek status dan latency bot\n"
                    "`/info` - Informasi tentang bot\n"
                    "`/help` - Menu bantuan interaktif\n"
                    "`/uptime` - Waktu aktif bot\n"
                    "`/menu` - Buka menu utama"
                ),
                color=discord.Color.blue()
            ),
            "ai": discord.Embed(
                title="🤖 AI Commands",
                description=(
                    "`/ai <prompt>` - Chat dengan Gemini AI\n"
                    "`/aimodel` - Pilih model AI\n"
                    "`/models` - Lihat daftar model\n"
                    "`/reset_ai` - Reset memory AI\n\n"
                    "💡 **Tips:** AI mengingat percakapan sebelumnya!"
                ),
                color=discord.Color.green()
            ),
            "user": discord.Embed(
                title="👤 User Commands",
                description=(
                    "`/avatar [@user]` - Lihat avatar user\n"
                    "`/banner [@user]` - Lihat banner user\n"
                    "`/userinfo [@user]` - Info user\n"
                    "`/whois [@user]` - Info lengkap user\n"
                    "`/afk [alasan]` - Set status AFK"
                ),
                color=discord.Color.purple()
            ),
            "server": discord.Embed(
                title="🏠 Server Commands",
                description=(
                    "`/serverinfo` - Info lengkap server\n"
                    "`/servericon` - Lihat icon server\n"
                    "`/membercount` - Jumlah member"
                ),
                color=discord.Color.gold()
            ),
            "mod": discord.Embed(
                title="🛡️ Moderation Commands",
                description=(
                    "`/kick @user [alasan]` - Kick member\n"
                    "`/warn @user [alasan]` - Warn member\n"
                    "`/clear <jumlah>` - Hapus pesan (1-100)\n\n"
                    "⚠️ Membutuhkan permission yang sesuai!"
                ),
                color=discord.Color.red()
            ),
            "utility": discord.Embed(
                title="📊 Utility Commands",
                description=(
                    "`/poll \"pertanyaan\" \"opsi1\" \"opsi2\"` - Buat poll\n"
                    "`/timer <waktu>` - Set timer (5s, 10m, 1h)\n"
                    "`/remind <waktu> <pesan>` - Set reminder\n"
                    "`/giveaway <waktu> <hadiah>` - Buat giveaway\n"
                    "`/math <expr>` - Kalkulator\n"
                    "`/say <pesan>` - Bot kirim pesan\n"
                    "`/embed \"judul\" deskripsi` - Buat embed"
                ),
                color=discord.Color.teal()
            ),
            "fun": discord.Embed(
                title="🎮 Fun Commands",
                description=(
                    "`/8ball <pertanyaan>` - Tanya magic 8ball\n"
                    "`/coinflip` - Lempar koin\n"
                    "`/roll [sisi]` - Lempar dadu\n"
                    "`/choose <opsi1> <opsi2>...` - Pilih random\n"
                    "`/rps <batu/gunting/kertas>` - Main suit"
                ),
                color=discord.Color.magenta()
            ),
            "games": discord.Embed(
                title="🎲 Games Commands",
                description=(
                    "`/trivia` - Main trivia quiz\n"
                    "`/scramble` - Susun kata acak\n"
                    "`/setcount` - Set counting channel\n"
                    "`/count` - Lihat angka saat ini\n\n"
                    "🎯 Menang game = bonus XP!"
                ),
                color=discord.Color.orange()
            ),
            "leveling": discord.Embed(
                title="⭐ Leveling System",
                description=(
                    "`/rank [@user]` - Lihat level & XP\n"
                    "`/leaderboard` - Top 10 XP\n\n"
                    "📈 **Cara dapat XP:**\n"
                    "• Kirim pesan (+1-5 XP)\n"
                    "• Menang trivia (+25 XP)\n"
                    "• Menang scramble (+20 XP)\n"
                    "• Counting benar (+2 XP)"
                ),
                color=discord.Color.gold()
            )
        }
        embed = embeds.get(self.values[0])
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HelpSelect())
    
    @ui.button(label="🏠 Home", style=discord.ButtonStyle.primary)
    async def home_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="📚 Help Menu",
            description="Pilih kategori dari dropdown di bawah untuk melihat command yang tersedia!",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Prefix", value="`/`", inline=True)
        embed.add_field(name="Categories", value="9", inline=True)
        embed.set_footer(text="Gunakan dropdown untuk navigasi")
        await interaction.response.edit_message(embed=embed)
    
    @ui.button(label="❌ Tutup", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.message.delete()

# Main Menu with Buttons
class MainMenuView(ui.View):
    def __init__(self):
        super().__init__(timeout=180)
    
    @ui.button(label="📊 Status", style=discord.ButtonStyle.primary, row=0)
    async def status_btn(self, interaction: discord.Interaction, button: ui.Button):
        latency = round(interaction.client.latency * 1000, 2)
        uptime = datetime.datetime.now() - start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        
        embed = discord.Embed(title="📊 Bot Status", color=discord.Color.green())
        embed.add_field(name="🏓 Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="⏱️ Uptime", value=f"{days}d {hours}h {minutes}m", inline=True)
        embed.add_field(name="🧩 Shard", value=f"{interaction.guild.shard_id if interaction.guild else 'N/A'}", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="🤖 AI Chat", style=discord.ButtonStyle.success, row=0)
    async def ai_btn(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="🤖 AI Chat",
            description="Gunakan `/ai <prompt>` untuk chat dengan Gemini AI!\n\n💡 AI akan mengingat percakapan sebelumnya.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="👤 Profile", style=discord.ButtonStyle.secondary, row=0)
    async def profile_btn(self, interaction: discord.Interaction, button: ui.Button):
        member = interaction.user
        roles = [role.mention for role in member.roles[1:]]
        
        embed = discord.Embed(title=f"👤 {member.display_name}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles[:5]) if roles else "None", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="🏠 Server", style=discord.ButtonStyle.secondary, row=1)
    async def server_btn(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        embed = discord.Embed(title=f"🏠 {guild.name}", color=discord.Color.gold())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="📚 Help", style=discord.ButtonStyle.primary, row=1)
    async def help_btn(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="📚 Help Menu",
            description="Pilih kategori dari dropdown!",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)
    
    @ui.button(label="❌ Tutup", style=discord.ButtonStyle.danger, row=1)
    async def close_btn(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.message.delete()

# Confirm Action View
class ConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None
    
    @ui.button(label="✅ Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()
    
    @ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()

# Role Select Menu
class RoleSelect(ui.Select):
    def __init__(self, roles: list):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles[:25]  # Discord limit 25 options
        ]
        super().__init__(placeholder="Pilih role...", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)
        if role:
            embed = discord.Embed(
                title=f"🎭 Role: {role.name}",
                color=role.color
            )
            embed.add_field(name="ID", value=role.id, inline=True)
            embed.add_field(name="Members", value=len(role.members), inline=True)
            embed.add_field(name="Color", value=str(role.color), inline=True)
            embed.add_field(name="Position", value=role.position, inline=True)
            embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
            await interaction.response.edit_message(embed=embed)

class RoleView(ui.View):
    def __init__(self, roles: list):
        super().__init__(timeout=60)
        self.add_item(RoleSelect(roles))

# AI Model Select Menu
class AIModelSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=f"{info['emoji']} {key.upper()}",
                value=key,
                description=f"{info['name']} - {info['description']}",
                default=(key == current_gemini_model)
            )
            for key, info in GEMINI_MODELS.items()
        ]
        super().__init__(placeholder="🤖 Pilih model AI...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        global current_gemini_model, model, user_chats
        
        selected = self.values[0]
        current_gemini_model = selected
        model = create_model(selected)
        
        # Clear all user chats when model changes
        user_chats.clear()
        
        info = GEMINI_MODELS[selected]
        embed = discord.Embed(
            title=f"{info['emoji']} Model Changed!",
            description=f"Model AI berhasil diganti ke **{info['name']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Description", value=info['description'], inline=False)
        embed.add_field(name="Note", value="⚠️ Memory AI telah direset untuk semua user.", inline=False)
        await interaction.response.edit_message(embed=embed, view=AIModelView())

class AIModelView(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(AIModelSelect())
    
    @ui.button(label="📊 Model Info", style=discord.ButtonStyle.secondary, row=1)
    async def info_btn(self, interaction: discord.Interaction, button: ui.Button):
        info = GEMINI_MODELS[current_gemini_model]
        embed = discord.Embed(
            title="📊 Current AI Model",
            color=discord.Color.blue()
        )
        embed.add_field(name="Model", value=info['name'], inline=True)
        embed.add_field(name="Type", value=info['description'], inline=True)
        embed.add_field(name="Active Users", value=len(user_chats), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="🗑️ Reset All Memory", style=discord.ButtonStyle.danger, row=1)
    async def reset_btn(self, interaction: discord.Interaction, button: ui.Button):
        user_chats.clear()
        await interaction.response.send_message("✅ Memory AI untuk semua user telah direset!", ephemeral=True)

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

# ================= INTERACTIVE MENU COMMANDS =================
@bot.command()
async def menu(ctx):
    """Buka menu utama interaktif."""
    embed = discord.Embed(
        title="🎮 Main Menu",
        description="Selamat datang! Pilih menu di bawah:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="📊 Status", value="Lihat status bot", inline=True)
    embed.add_field(name="🤖 AI Chat", value="Info AI", inline=True)
    embed.add_field(name="👤 Profile", value="Lihat profile", inline=True)
    embed.add_field(name="🏠 Server", value="Info server", inline=True)
    embed.add_field(name="📚 Help", value="Bantuan", inline=True)
    embed.set_footer(text="Menu akan expire dalam 3 menit")
    await ctx.send(embed=embed, view=MainMenuView())

@bot.command()
async def helpmenu(ctx):
    """Buka menu bantuan dengan dropdown."""
    embed = discord.Embed(
        title="📚 Help Menu",
        description="Pilih kategori dari dropdown di bawah untuk melihat command yang tersedia!",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Prefix", value="`/`", inline=True)
    embed.add_field(name="Categories", value="6", inline=True)
    embed.set_footer(text="Gunakan dropdown untuk navigasi")
    await ctx.send(embed=embed, view=HelpView())

@bot.command()
async def roles(ctx):
    """Lihat info role dengan menu dropdown."""
    guild_roles = [r for r in ctx.guild.roles if r.name != "@everyone"]
    if not guild_roles:
        await ctx.send("❌ Tidak ada role di server ini.")
        return
    
    embed = discord.Embed(
        title="🎭 Role Selector",
        description="Pilih role untuk melihat detailnya:",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=RoleView(guild_roles))

@bot.command()
async def reset_ai(ctx):
    """Reset memory AI untuk user."""
    view = ConfirmView()
    msg = await ctx.send("⚠️ Yakin ingin reset memory AI? Percakapan sebelumnya akan dihapus.", view=view)
    
    await view.wait()
    
    if view.value is True:
        if ctx.author.id in user_chats:
            del user_chats[ctx.author.id]
        await msg.edit(content="✅ Memory AI telah direset!", view=None)
    elif view.value is False:
        await msg.edit(content="❌ Dibatalkan.", view=None)
    else:
        await msg.edit(content="⏰ Timeout.", view=None)

@bot.command()
async def aimodel(ctx):
    """Pilih model AI yang digunakan."""
    info = GEMINI_MODELS[current_gemini_model]
    embed = discord.Embed(
        title="🤖 AI Model Selector",
        description="Pilih model AI dari dropdown di bawah:",
        color=discord.Color.purple()
    )
    embed.add_field(name="Current Model", value=f"{info['emoji']} {info['name']}", inline=True)
    embed.add_field(name="Active Users", value=len(user_chats), inline=True)
    embed.set_footer(text="Mengganti model akan reset memory AI")
    await ctx.send(embed=embed, view=AIModelView())

@bot.command()
async def models(ctx):
    """Lihat daftar model AI yang tersedia."""
    embed = discord.Embed(
        title="🤖 Available AI Models",
        description="Model AI yang tersedia untuk digunakan:",
        color=discord.Color.blue()
    )
    for key, info in GEMINI_MODELS.items():
        status = "✅ Active" if key == current_gemini_model else ""
        embed.add_field(
            name=f"{info['emoji']} {key.upper()} {status}",
            value=f"`{info['name']}`\n{info['description']}",
            inline=True
        )
    embed.set_footer(text="Gunakan /aimodel untuk mengganti model")
    await ctx.send(embed=embed)

# Slash commands for AI model
@bot.tree.command(name="aimodel", description="Pilih model AI")
async def aimodel_slash(interaction: discord.Interaction):
    info = GEMINI_MODELS[current_gemini_model]
    embed = discord.Embed(
        title="🤖 AI Model Selector",
        description="Pilih model AI dari dropdown di bawah:",
        color=discord.Color.purple()
    )
    embed.add_field(name="Current Model", value=f"{info['emoji']} {info['name']}", inline=True)
    embed.add_field(name="Active Users", value=len(user_chats), inline=True)
    embed.set_footer(text="Mengganti model akan reset memory AI")
    await interaction.response.send_message(embed=embed, view=AIModelView())

# Slash command for menu
@bot.tree.command(name="menu", description="Buka menu utama interaktif")
async def menu_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎮 Main Menu",
        description="Selamat datang! Pilih menu di bawah:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="📊 Status", value="Lihat status bot", inline=True)
    embed.add_field(name="🤖 AI Chat", value="Info AI", inline=True)
    embed.add_field(name="👤 Profile", value="Lihat profile", inline=True)
    embed.add_field(name="🏠 Server", value="Info server", inline=True)
    embed.add_field(name="📚 Help", value="Bantuan", inline=True)
    embed.set_footer(text="Menu akan expire dalam 3 menit")
    await interaction.response.send_message(embed=embed, view=MainMenuView())

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

# ================= FUN COMMANDS =================
@bot.command(name="8ball")
async def eightball(ctx, *, question: str):
    """Tanya magic 8ball."""
    responses = [
        # Positif
        "🟢 Ya, pasti!", "🟢 Tentu saja!", "🟢 Tanpa ragu!",
        "🟢 Sepertinya iya", "🟢 Kemungkinan besar iya",
        # Netral
        "🟡 Mungkin...", "🟡 Tanya lagi nanti", "🟡 Tidak bisa dipastikan",
        "🟡 Konsentrasi dan tanya lagi", "🟡 Belum jelas",
        # Negatif
        "🔴 Jangan berharap", "🔴 Tidak", "🔴 Kemungkinan kecil",
        "🔴 Sangat diragukan", "🔴 Jawabannya tidak"
    ]
    embed = discord.Embed(
        title="🎱 Magic 8-Ball",
        color=discord.Color.purple()
    )
    embed.add_field(name="❓ Pertanyaan", value=question, inline=False)
    embed.add_field(name="🔮 Jawaban", value=random.choice(responses), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def coinflip(ctx):
    """Lempar koin."""
    result = random.choice(["🪙 **Heads!**", "🪙 **Tails!**"])
    embed = discord.Embed(
        title="🪙 Coin Flip",
        description=f"Hasil: {result}",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.command()
async def roll(ctx, sides: int = 6):
    """Lempar dadu. Default 6 sisi."""
    if sides < 2 or sides > 100:
        await ctx.send("❌ Sisi dadu harus antara 2-100.")
        return
    result = random.randint(1, sides)
    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"Melempar d{sides}...\n\n🎯 Hasil: **{result}**",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@bot.command()
async def choose(ctx, *choices):
    """Pilih secara random dari opsi yang diberikan."""
    if len(choices) < 2:
        await ctx.send("❌ Berikan minimal 2 pilihan.")
        return
    result = random.choice(choices)
    embed = discord.Embed(
        title="🤔 Random Choice",
        color=discord.Color.blue()
    )
    embed.add_field(name="📋 Pilihan", value="\n".join([f"• {c}" for c in choices]), inline=False)
    embed.add_field(name="✅ Dipilih", value=f"**{result}**", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def rps(ctx, choice: str):
    """Main batu gunting kertas. Pilih: batu/gunting/kertas"""
    choices = {"batu": "🪨", "gunting": "✂️", "kertas": "📄"}
    choice = choice.lower()
    
    if choice not in choices:
        await ctx.send("❌ Pilih: `batu`, `gunting`, atau `kertas`")
        return
    
    bot_choice = random.choice(list(choices.keys()))
    
    # Determine winner
    if choice == bot_choice:
        result = "🤝 **Seri!**"
        color = discord.Color.yellow()
    elif (choice == "batu" and bot_choice == "gunting") or \
         (choice == "gunting" and bot_choice == "kertas") or \
         (choice == "kertas" and bot_choice == "batu"):
        result = "🎉 **Kamu Menang!**"
        color = discord.Color.green()
    else:
        result = "😢 **Kamu Kalah!**"
        color = discord.Color.red()
    
    embed = discord.Embed(title="✊✌️✋ Batu Gunting Kertas", color=color)
    embed.add_field(name="Kamu", value=f"{choices[choice]} {choice.title()}", inline=True)
    embed.add_field(name="Bot", value=f"{choices[bot_choice]} {bot_choice.title()}", inline=True)
    embed.add_field(name="Hasil", value=result, inline=False)
    await ctx.send(embed=embed)

# ================= UTILITY COMMANDS =================
@bot.command()
async def timer(ctx, duration: str):
    """Set timer. Contoh: /timer 5m, /timer 30s, /timer 1h"""
    # Parse duration
    match = re.match(r"(\d+)([smh])", duration.lower())
    if not match:
        await ctx.send("❌ Format: `<angka><s/m/h>` (contoh: 5m, 30s, 1h)")
        return
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    units = {"s": ("detik", 1), "m": ("menit", 60), "h": ("jam", 3600)}
    unit_name, multiplier = units[unit]
    seconds = amount * multiplier
    
    if seconds > 86400:  # Max 24 hours
        await ctx.send("❌ Maksimal 24 jam.")
        return
    
    await ctx.send(f"⏰ Timer set untuk **{amount} {unit_name}**!")
    await asyncio.sleep(seconds)
    await ctx.send(f"🔔 {ctx.author.mention} Timer **{amount} {unit_name}** sudah selesai!")

@bot.command()
async def math(ctx, *, expression: str):
    """Kalkulator sederhana."""
    # Sanitize input - only allow safe characters
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        await ctx.send("❌ Ekspresi tidak valid.")
        return
    
    try:
        result = eval(expression)
        embed = discord.Embed(
            title="🔢 Kalkulator",
            color=discord.Color.blue()
        )
        embed.add_field(name="📝 Ekspresi", value=f"`{expression}`", inline=False)
        embed.add_field(name="✅ Hasil", value=f"**{result}**", inline=False)
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ Tidak dapat menghitung ekspresi.")

@bot.command()
async def say(ctx, *, message: str):
    """Bot mengirim pesan."""
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def embed(ctx, title: str, *, description: str):
    """Buat embed custom. Contoh: /embed "Judul" Deskripsi disini"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.random(),
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text=f"Dibuat oleh {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def afk(ctx, *, reason: str = "AFK"):
    """Set status AFK."""
    afk_users[ctx.author.id] = {
        "reason": reason,
        "time": datetime.datetime.now()
    }
    await ctx.send(f"💤 {ctx.author.mention} sekarang AFK: **{reason}**")

@bot.command()
async def whois(ctx, member: discord.Member = None):
    """Info lengkap tentang user."""
    member = member or ctx.author
    
    # Calculate account age
    account_age = (datetime.datetime.now(datetime.timezone.utc) - member.created_at).days
    server_age = (datetime.datetime.now(datetime.timezone.utc) - member.joined_at).days
    
    # Get permissions
    key_perms = []
    if member.guild_permissions.administrator:
        key_perms.append("Administrator")
    if member.guild_permissions.manage_guild:
        key_perms.append("Manage Server")
    if member.guild_permissions.manage_messages:
        key_perms.append("Manage Messages")
    if member.guild_permissions.kick_members:
        key_perms.append("Kick Members")
    if member.guild_permissions.ban_members:
        key_perms.append("Ban Members")
    
    roles = [role.mention for role in member.roles[1:][:10]]  # Max 10 roles
    
    embed = discord.Embed(
        title=f"👤 {member.display_name}",
        description=f"{member.mention}",
        color=member.color,
        timestamp=datetime.datetime.now()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🏷️ Username", value=str(member), inline=True)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="🤖 Bot?", value="Ya" if member.bot else "Tidak", inline=True)
    embed.add_field(name="📅 Akun Dibuat", value=f"{member.created_at.strftime('%d/%m/%Y')}\n({account_age} hari)", inline=True)
    embed.add_field(name="📥 Bergabung", value=f"{member.joined_at.strftime('%d/%m/%Y')}\n({server_age} hari)", inline=True)
    embed.add_field(name="🎨 Status", value=str(member.status).title(), inline=True)
    embed.add_field(name=f"🎭 Roles [{len(member.roles)-1}]", value=" ".join(roles) if roles else "Tidak ada", inline=False)
    if key_perms:
        embed.add_field(name="🔑 Key Permissions", value=", ".join(key_perms), inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def membercount(ctx):
    """Tampilkan jumlah member server."""
    guild = ctx.guild
    total = guild.member_count
    bots = len([m for m in guild.members if m.bot])
    humans = total - bots
    
    embed = discord.Embed(
        title=f"👥 Member Count - {guild.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Manusia", value=humans, inline=True)
    embed.add_field(name="🤖 Bot", value=bots, inline=True)
    embed.add_field(name="📊 Total", value=total, inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def servericon(ctx):
    """Tampilkan icon server."""
    guild = ctx.guild
    if not guild.icon:
        await ctx.send("❌ Server tidak memiliki icon.")
        return
    
    embed = discord.Embed(
        title=f"🖼️ Icon {guild.name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, member: discord.Member = None):
    """Tampilkan banner user."""
    member = member or ctx.author
    user = await bot.fetch_user(member.id)  # Fetch full user to get banner
    
    if not user.banner:
        await ctx.send(f"❌ {member.display_name} tidak memiliki banner.")
        return
    
    embed = discord.Embed(
        title=f"🖼️ Banner {member.display_name}",
        color=member.color
    )
    embed.set_image(url=user.banner.url)
    await ctx.send(embed=embed)

# ================= LEVELING SYSTEM =================
user_xp = {}

def get_level(xp: int) -> int:
    """Calculate level from XP."""
    return int((xp / 100) ** 0.5)

def xp_for_level(level: int) -> int:
    """Calculate XP needed for a level."""
    return (level ** 2) * 100

@bot.command()
async def rank(ctx, member: discord.Member = None):
    """Lihat level dan XP user."""
    member = member or ctx.author
    xp = user_xp.get(member.id, 0)
    level = get_level(xp)
    next_level_xp = xp_for_level(level + 1)
    progress = (xp - xp_for_level(level)) / (next_level_xp - xp_for_level(level)) * 100
    
    # Create progress bar
    bar_length = 10
    filled = int(progress / 100 * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    embed = discord.Embed(
        title=f"📊 Rank - {member.display_name}",
        color=member.color
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="⭐ Level", value=level, inline=True)
    embed.add_field(name="✨ XP", value=f"{xp}/{next_level_xp}", inline=True)
    embed.add_field(name="📈 Progress", value=f"{bar} {progress:.1f}%", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    """Tampilkan leaderboard XP."""
    if not user_xp:
        await ctx.send("❌ Belum ada data XP.")
        return
    
    sorted_users = sorted(user_xp.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 XP Leaderboard",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    description = ""
    for i, (user_id, xp) in enumerate(sorted_users):
        member = ctx.guild.get_member(user_id)
        if member:
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            level = get_level(xp)
            description += f"{medal} {member.display_name} - Level {level} ({xp} XP)\n"
    
    embed.description = description or "Tidak ada data"
    await ctx.send(embed=embed)

# ================= GIVEAWAY SYSTEM =================
active_giveaways = {}

class GiveawayView(ui.View):
    def __init__(self, prize: str, host_id: int, ends_at: datetime.datetime):
        super().__init__(timeout=None)
        self.prize = prize
        self.host_id = host_id
        self.ends_at = ends_at
        self.participants = set()
    
    @ui.button(label="🎉 Join Giveaway", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id in self.participants:
            await interaction.response.send_message("❌ Kamu sudah bergabung!", ephemeral=True)
            return
        
        self.participants.add(interaction.user.id)
        button.label = f"🎉 Join ({len(self.participants)})"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("✅ Berhasil bergabung giveaway!", ephemeral=True)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def giveaway(ctx, duration: str, *, prize: str):
    """Buat giveaway. Contoh: /giveaway 1h Nitro Classic"""
    match = re.match(r"(\d+)([smh])", duration.lower())
    if not match:
        await ctx.send("❌ Format durasi: `<angka><s/m/h>`")
        return
    
    amount = int(match.group(1))
    unit = match.group(2)
    units = {"s": 1, "m": 60, "h": 3600}
    seconds = amount * units[unit]
    
    if seconds > 604800:  # Max 7 days
        await ctx.send("❌ Maksimal 7 hari.")
        return
    
    ends_at = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    view = GiveawayView(prize, ctx.author.id, ends_at)
    
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Hadiah:** {prize}\n\n"
                    f"**Host:** {ctx.author.mention}\n"
                    f"**Berakhir:** <t:{int(ends_at.timestamp())}:R>\n\n"
                    f"Klik tombol di bawah untuk ikut!",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Giveaway ID: {ctx.message.id}")
    
    msg = await ctx.send(embed=embed, view=view)
    active_giveaways[msg.id] = view
    
    # Wait and end giveaway
    await asyncio.sleep(seconds)
    
    if msg.id in active_giveaways:
        view = active_giveaways.pop(msg.id)
        if not view.participants:
            await ctx.send("😢 Tidak ada peserta giveaway.")
        else:
            winner_id = random.choice(list(view.participants))
            winner = ctx.guild.get_member(winner_id)
            
            embed = discord.Embed(
                title="🎊 GIVEAWAY ENDED 🎊",
                description=f"**Hadiah:** {prize}\n\n"
                            f"🏆 **Pemenang:** {winner.mention}\n"
                            f"Selamat! 🎉",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

# ================= REMINDER SYSTEM =================
@bot.command()
async def remind(ctx, time: str, *, message: str):
    """Set reminder. Contoh: /remind 30m Makan siang"""
    match = re.match(r"(\d+)([smhd])", time.lower())
    if not match:
        await ctx.send("❌ Format: `<angka><s/m/h/d>` (contoh: 30m, 1h, 2d)")
        return
    
    amount = int(match.group(1))
    unit = match.group(2)
    units = {"s": ("detik", 1), "m": ("menit", 60), "h": ("jam", 3600), "d": ("hari", 86400)}
    unit_name, multiplier = units[unit]
    seconds = amount * multiplier
    
    if seconds > 604800:  # Max 7 days
        await ctx.send("❌ Maksimal 7 hari.")
        return
    
    remind_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    
    embed = discord.Embed(
        title="⏰ Reminder Set",
        description=f"Aku akan mengingatkanmu dalam **{amount} {unit_name}**",
        color=discord.Color.blue()
    )
    embed.add_field(name="📝 Pesan", value=message, inline=False)
    embed.add_field(name="🕐 Waktu", value=f"<t:{int(remind_time.timestamp())}:R>", inline=False)
    await ctx.send(embed=embed)
    
    await asyncio.sleep(seconds)
    
    remind_embed = discord.Embed(
        title="🔔 Reminder!",
        description=message,
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now()
    )
    remind_embed.set_footer(text="Reminder yang kamu set")
    await ctx.send(f"{ctx.author.mention}", embed=remind_embed)

# ================= TRIVIA GAME =================
trivia_questions = [
    {"q": "Bahasa pemrograman apa yang dibuat oleh Guido van Rossum?", "a": "python", "opts": ["Java", "Python", "C++", "Ruby"]},
    {"q": "Apa kepanjangan dari HTML?", "a": "hypertext markup language", "opts": ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyper Transfer Markup Language"]},
    {"q": "Siapa pendiri Microsoft?", "a": "bill gates", "opts": ["Steve Jobs", "Bill Gates", "Mark Zuckerberg", "Elon Musk"]},
    {"q": "Tahun berapa Python pertama kali dirilis?", "a": "1991", "opts": ["1989", "1991", "1995", "2000"]},
    {"q": "Apa nama maskot Linux?", "a": "tux", "opts": ["Penguin", "Tux", "Linux", "Linus"]},
    {"q": "Framework web Python yang terkenal adalah?", "a": "django", "opts": ["Spring", "Django", "Laravel", "Express"]},
    {"q": "Siapa pencipta Linux?", "a": "linus torvalds", "opts": ["Bill Gates", "Linus Torvalds", "Dennis Ritchie", "Ken Thompson"]},
    {"q": "Apa kepanjangan dari CPU?", "a": "central processing unit", "opts": ["Central Processing Unit", "Computer Personal Unit", "Central Program Unit", "Control Processing Unit"]},
]

class TriviaView(ui.View):
    def __init__(self, question: dict, user_id: int):
        super().__init__(timeout=30)
        self.question = question
        self.user_id = user_id
        self.answered = False
        
        # Add buttons for each option
        for i, opt in enumerate(question["opts"]):
            button = ui.Button(label=opt, style=discord.ButtonStyle.secondary, custom_id=f"trivia_{i}")
            button.callback = self.create_callback(opt)
            self.add_item(button)
    
    def create_callback(self, option: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Ini bukan trivia kamu!", ephemeral=True)
                return
            
            if self.answered:
                return
            
            self.answered = True
            correct = option.lower() == self.question["a"].lower() or self.question["a"].lower() in option.lower()
            
            # Disable all buttons
            for item in self.children:
                item.disabled = True
                if hasattr(item, 'label'):
                    if item.label == option:
                        item.style = discord.ButtonStyle.success if correct else discord.ButtonStyle.danger
                    elif self.question["a"].lower() in item.label.lower():
                        item.style = discord.ButtonStyle.success
            
            if correct:
                # Give XP
                user_xp[interaction.user.id] = user_xp.get(interaction.user.id, 0) + 25
                result_text = "✅ **Benar!** +25 XP"
                color = discord.Color.green()
            else:
                result_text = f"❌ **Salah!** Jawaban: {self.question['opts'][[o.lower() for o in self.question['opts']].index(self.question['a']) if self.question['a'] in [o.lower() for o in self.question['opts']] else 0]}"
                color = discord.Color.red()
            
            embed = discord.Embed(
                title="🧠 Trivia",
                description=f"**{self.question['q']}**\n\n{result_text}",
                color=color
            )
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()
        
        return callback
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

@bot.command()
async def trivia(ctx):
    """Main trivia quiz!"""
    question = random.choice(trivia_questions)
    random.shuffle(question["opts"])
    
    view = TriviaView(question, ctx.author.id)
    
    embed = discord.Embed(
        title="🧠 Trivia",
        description=f"**{question['q']}**\n\nPilih jawaban dalam 30 detik!",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Dimainkan oleh {ctx.author.display_name}")
    
    await ctx.send(embed=embed, view=view)

# ================= WORD SCRAMBLE GAME =================
scramble_words = ["python", "discord", "programming", "computer", "keyboard", "developer", "software", "internet", "database", "algorithm"]

@bot.command()
async def scramble(ctx):
    """Main word scramble game!"""
    word = random.choice(scramble_words)
    scrambled = ''.join(random.sample(word, len(word)))
    
    # Make sure it's actually scrambled
    while scrambled == word:
        scrambled = ''.join(random.sample(word, len(word)))
    
    embed = discord.Embed(
        title="🔤 Word Scramble",
        description=f"Susun huruf berikut menjadi kata yang benar!\n\n**`{scrambled.upper()}`**\n\nKetik jawabanmu dalam 30 detik!",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
        if msg.content.lower() == word:
            user_xp[ctx.author.id] = user_xp.get(ctx.author.id, 0) + 20
            await ctx.send(f"🎉 **Benar!** Jawabannya adalah `{word}`. +20 XP!")
        else:
            await ctx.send(f"❌ **Salah!** Jawabannya adalah `{word}`.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ **Waktu habis!** Jawabannya adalah `{word}`.")

# ================= COUNTING GAME =================
counting_channels = {}

@bot.command()
@commands.has_permissions(manage_channels=True)
async def setcount(ctx):
    """Set channel ini sebagai counting channel."""
    counting_channels[ctx.channel.id] = 0
    await ctx.send("✅ Channel ini sekarang adalah counting channel! Mulai dari **1**!")

@bot.command()
async def count(ctx):
    """Lihat angka saat ini di counting channel."""
    if ctx.channel.id not in counting_channels:
        await ctx.send("❌ Ini bukan counting channel.")
        return
    await ctx.send(f"📊 Angka saat ini: **{counting_channels[ctx.channel.id]}**")

# ================= AFK CHECK IN ON_MESSAGE =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # XP System - Give XP for messages
    if not message.content.startswith("/"):
        user_xp[message.author.id] = user_xp.get(message.author.id, 0) + random.randint(1, 5)
        
        # Check for level up
        old_level = get_level(user_xp[message.author.id] - 5)
        new_level = get_level(user_xp[message.author.id])
        if new_level > old_level:
            await message.channel.send(f"🎉 {message.author.mention} naik ke **Level {new_level}**!")
    
    # Counting game check
    if message.channel.id in counting_channels:
        try:
            num = int(message.content)
            expected = counting_channels[message.channel.id] + 1
            if num == expected:
                counting_channels[message.channel.id] = num
                await message.add_reaction("✅")
                # Bonus XP for counting
                user_xp[message.author.id] = user_xp.get(message.author.id, 0) + 2
            else:
                await message.add_reaction("❌")
                await message.channel.send(f"❌ {message.author.mention} salah! Angka seharusnya **{expected}**. Mulai ulang dari **1**!")
                counting_channels[message.channel.id] = 0
        except ValueError:
            pass  # Not a number, ignore
    
    # Check if user is back from AFK
    if message.author.id in afk_users:
        afk_data = afk_users.pop(message.author.id)
        afk_time = datetime.datetime.now() - afk_data["time"]
        minutes = int(afk_time.total_seconds() // 60)
        await message.channel.send(f"👋 Welcome back {message.author.mention}! Kamu AFK selama **{minutes} menit**.")
    
    # Check if mentioned user is AFK
    for mentioned in message.mentions:
        if mentioned.id in afk_users:
            afk_data = afk_users[mentioned.id]
            await message.channel.send(f"💤 {mentioned.display_name} sedang AFK: **{afk_data['reason']}**")
    
    # Auto reply halo bot
    if "halo bot" in message.content.lower():
        await message.channel.send("Halo juga 👋")
    
    await bot.process_commands(message)

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
