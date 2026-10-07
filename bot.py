
import os
import discord
from discord.ext import commands
from google import genai
from aiohttp import web

# Инициализация Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Настройка интентов Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Фейковый веб-сервер для Render
async def handle(request):
    return web.Response(text="IMARCH Coordinator is running!")

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
    await start_web_server()
    print(f"Координатор {bot.user} успешно запущен и готов к работе!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
                if not prompt:
                    prompt = "Привет!"

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                await message.reply(response.text)
            except Exception as e:
                print(f"Ошибка Gemini: {e}")
                await message.reply(f"Ошибка при обработке запроса: {e}")

    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))
