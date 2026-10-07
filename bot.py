import os
import asyncio
import discord
from discord.ext import commands
from google import genai
from aiohttp import web

# 1. Веб-сервер для поддержания активности на Render
async def handle(request):
    return web.Response(text="IMARCH Coordinator is active!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# 2. Инициализация Discord и Gemini
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

gemini_key = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно подключился к Discord Gateway!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            if not gemini_client:
                await message.reply("Ошибка: Не задан GEMINI_API_KEY в переменных окружения Render.")
                return

            try:
                prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
                if not prompt:
                    prompt = "Привет!"

                response = gemini_client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                )
                await message.reply(response.text if response.text else "Получен пустой ответ.")
            except Exception as e:
                print(f"Ошибка Gemini: {e}")
                await message.reply(f"Произошла ошибка: {e}")

    await bot.process_commands(message)

# 3. Точка входа
async def main():
    await start_web_server()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Ошибка: DISCORD_TOKEN не найден!")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
