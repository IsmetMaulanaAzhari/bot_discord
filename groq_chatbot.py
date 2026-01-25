import os
import discord
from groq import Groq
from dotenv import load_dotenv

# 1. Load variabel lingkungan
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# 2. Inisialisasi Groq Client
groq_client = Groq(
    api_key=GROQ_API_KEY,
)

# 3. Setup Discord Bot
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot berhasil login sebagai {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    async with message.channel.typing():
        try:
            # 4. Kirim request ke Groq API dengan 'with_raw_response'
            # Kita menggunakan .with_raw_response untuk bisa membaca Header
            response = groq_client.chat.completions.with_raw_response.create(
                messages=[
                    {
                        "role": "user",
                        "content": message.content,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )

            # Ambil data Header (Sisa Token & Request)
            headers = response.headers
            remaining_tokens = headers.get('x-ratelimit-remaining-tokens', 'N/A')
            remaining_requests = headers.get('x-ratelimit-remaining-requests', 'N/A')
            
            # Ambil isi pesan jawaban AI
            completion = response.parse()
            ai_text = completion.choices[0].message.content

            # Format Footer informasi kuota
            footer = f"\n\n__**Stats Kuota:**__\n:ticket: Sisa Token: `{remaining_tokens}`\n:satellite: Sisa Request: `{remaining_requests}`"
            
            # Gabungkan pesan AI dengan Footer
            final_response = ai_text + footer

            # 5. Kirim balasan ke Discord (dengan logika split pesan jika panjang)
            if len(final_response) > 2000:
                # Jika pesan terlalu panjang, kita pecah. 
                # Note: Footer mungkin terpotong di pecahan terakhir, tapi itu wajar untuk pesan panjang.
                for i in range(0, len(final_response), 2000):
                    await message.channel.send(final_response[i:i+2000])
            else:
                await message.channel.send(final_response)

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send(f"Terjadi kesalahan: {e}")

# Jalankan Bot
client.run(DISCORD_TOKEN)