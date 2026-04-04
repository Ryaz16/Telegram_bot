import asyncio
import os
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

histories = defaultdict(list)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply("Hi! I am your bot 🤖")

@dp.message(Command("clear"))
async def clear(message: types.Message):
    user_id = message.from_user.id
    histories[user_id] = []
    await message.reply("Context cleared ✅")

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id

    histories[user_id].append({"role": "user", "content": message.text})

    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Give short, accurate and to the point answers. Do not add unnecessary information or filler text."},
        *histories[user_id]
    ],
    max_tokens=200,
    temperature=0.2  # 👈 add this (lower = more accurate)
    )

    reply = response.choices[0].message.content
    histories[user_id].append({"role": "assistant", "content": reply})

    await message.reply(reply)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())