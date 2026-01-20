import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Konfigurasi Gemini
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

print("🤖 Gemini Chatbot (ketik 'exit' untuk keluar)\n")

while True:
    user_input = input("Kamu: ")

    if user_input.lower() == "exit":
        print("Bot: Sampai jumpa 👋")
        break

    response = model.generate_content(user_input)
    print("Bot:", response.text)
