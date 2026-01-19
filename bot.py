import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Events
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot login sebagai {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "halo bot" in message.content.lower():
        await message.channel.send("Halo juga 👋")

    await bot.process_commands(message)

# Commands
@bot.command()
async def ping(ctx):
    """Cek status bot."""
    await ctx.send("Pong! 🏓")

@bot.command()
async def hello(ctx):
    """Sapa user."""
    await ctx.send(f"Halo {ctx.author.mention} 👋")

@bot.command()
async def info(ctx):
    """Tampilkan informasi bot."""
    embed = discord.Embed(
        title="🤖 Discord Bot",
        description="Bot latihan Discord menggunakan Python",
        color=discord.Color.blue()
    )
    embed.add_field(name="Author", value="Ismet", inline=False)
    embed.add_field(name="Fitur", value="Ping, Hello, Auto Reply, Embed", inline=False)

    await ctx.send(embed=embed)

# Slash Commands
@bot.tree.command(name="ping", description="Cek status bot")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

@bot.tree.command(name="hello", description="Sapa bot")
async def hello_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"Halo {interaction.user.mention} 👋")

# Moderation Commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Tidak ada alasan"):
    """Kick member dari server."""
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} telah di-kick. Alasan: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="Tidak ada alasan"):
    """Berikan peringatan kepada member."""
    await ctx.send(f"⚠️ {member.mention} diperingatkan.\nAlasan: {reason}")

# Error Handlers
@kick.error
@warn.error
async def permission_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Kamu tidak punya izin untuk command ini.")

# Run bot
bot.run(TOKEN)
