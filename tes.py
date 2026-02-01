import os
import discord
from groq import Groq
from dotenv import load_dotenv

# ===== Load ENV =====
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ===== Groq Client =====
groq_client = Groq(api_key=GROQ_API_KEY)

# ===== Discord Setup =====
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot aktif sebagai {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    is_command = message.content.startswith("!ask")
    is_reply = message.reference is not None

    # Abaikan kalau bukan command dan bukan reply
    if not is_command and not is_reply:
        return

    user_prompt = message.content.replace("!ask", "").strip()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Continue the conversation naturally."
        }
    ]

    # ===== Jika reply ke pesan bot =====
    if is_reply:
        replied_msg = await message.channel.fetch_message(
            message.reference.message_id
        )

        if replied_msg.author == client.user:
            messages.append({
                "role": "assistant",
                "content": replied_msg.content
            })

        # Kalau reply TANPA !ask
        if not is_command:
            user_prompt = message.content.strip()

    if not user_prompt:
        return

    messages.append({
        "role": "user",
        "content": user_prompt
    })

    thinking_msg = await message.reply("🤖 Lagi mikir...")

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
        )

        answer = completion.choices[0].message.content

        # Discord max 2000 char
        if len(answer) > 2000:
            answer = answer[:1990] + "..."

        await thinking_msg.edit(content=answer)

    except Exception as e:
        await thinking_msg.edit(content="❌ Error saat memproses permintaan")
        print("Groq Error:", e)

client.run(DISCORD_TOKEN)
