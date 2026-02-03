import discord
from discord.ext import commands
from discord import ui, app_commands
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

# ================= INTERACTIVE MENUS =================

# Help Menu Dropdown
class HelpSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🔧 Basic", value="basic", description="Ping, Info, Uptime", emoji="🔧"),
            discord.SelectOption(label="🤖 AI", value="ai", description="Chat dengan Gemini AI", emoji="🤖"),
            discord.SelectOption(label="👤 User", value="user", description="Avatar, User Info", emoji="👤"),
            discord.SelectOption(label="🏠 Server", value="server", description="Server Info", emoji="🏠"),
            discord.SelectOption(label="🛡️ Moderation", value="mod", description="Kick, Warn, Clear", emoji="🛡️"),
            discord.SelectOption(label="📊 Utility", value="utility", description="Poll dan lainnya", emoji="📊"),
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
                    "`/reset_ai` - Reset memory AI\n\n"
                    "💡 **Tips:** AI mengingat percakapan sebelumnya!"
                ),
                color=discord.Color.green()
            ),
            "user": discord.Embed(
                title="👤 User Commands",
                description=(
                    "`/avatar [@user]` - Lihat avatar user\n"
                    "`/userinfo [@user]` - Info lengkap user\n"
                    "`/banner [@user]` - Lihat banner user"
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
                    "`/remind <waktu> <pesan>` - Set reminder\n"
                    "`/calculate <expr>` - Kalkulator"
                ),
                color=discord.Color.teal()
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
        embed.add_field(name="Categories", value="6", inline=True)
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
