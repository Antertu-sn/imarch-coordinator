import os
import asyncio
import discord
from discord.ext import commands
from google import genai
from aiohttp import web

# 1. Запуск веб-сервера ДУМАЯ О RENDER (запускаем сразу же!)
async def handle(request):
    return web.Response(text="IMARCH Coordinator is active and alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер успешно запущен на порту {port}")

# 2. Инициализация Discord и Gemini
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

gemini_key = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None

@bot.event
async def on_ready():
    print(f"Успех! Бот {bot.user} вошел в Discord и готов к работе!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            if not gemini_client:
                await message.reply("Ошибка: Ключ GEMINI_API_KEY не настроен в Render.")
                return

            try:
                prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
                if not prompt:
                    prompt = "Привет!"

                response = gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                await message.reply(response.text if response.text else "Получен пустой ответ.")
            except Exception as e:
                print(f"Ошибка Gemini: {e}")
                await message.reply(f"Произошла ошибка: {e}")

    await bot.process_commands(message)

# Основная функция запуска
async def main():
    # Старт веб-сервера строго ДО подключения к Discord Gateway
    await start_web_server()
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Критическая ошибка: Токен DISCORD_TOKEN отсутствует!")
        return
        
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())

