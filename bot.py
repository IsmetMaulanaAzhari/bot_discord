import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot login sebagai {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "halo bot" in message.content.lower():
        await message.channel.send("Halo juga 👋")

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Halo {ctx.author.mention} 👋")

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="🤖 Discord Bot",
        description="Bot latihan Discord menggunakan Python",
        color=discord.Color.blue()
    )
    embed.add_field(name="Author", value="Ismet", inline=False)
    embed.add_field(name="Fitur", value="Ping, Hello, Auto Reply, Embed", inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)
