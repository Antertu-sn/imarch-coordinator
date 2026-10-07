import os
import asyncio
import discord
from discord.ext import commands
from google import genai
from aiohttp import web

# Инициализация Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None

# Настройка интентов Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Простой веб-сервер для поддержки активности Render
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

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно подключился к Discord Gateway!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Отвечаем на упоминание или личные сообщения
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            if not client:
                await message.reply("Ошибка: Не задан GEMINI_API_KEY в переменных окружения Render.")
                return

            try:
                prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
                if not prompt:
                    prompt = "Привет!"

                # Вызов Gemini API
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                await message.reply(response.text if response.text else "Получен пустой ответ.")
            except Exception as e:
                print(f"Ошибка при запросе к Gemini: {e}")
                await message.reply(f"Произошла ошибка при обработке запроса: {e}")

    await bot.process_commands(message)

async def main():
    async with bot:
        # Запускаем веб-сервер фоновой задачей
        asyncio.create_task(start_web_server())
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("Ошибка: Токен DISCORD_TOKEN не найден!")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
