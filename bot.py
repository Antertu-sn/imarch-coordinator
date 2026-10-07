import os
import discord
from discord.ext import commands
import google.generativeai as genai

# Настройка Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# Настройка Discord бота
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Координатор {bot.user} успешно запущен и готов к работе!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Отвечаем, если упомянули бота или в личных сообщениях/определенных каналах
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                # Очищаем текст от упоминания
                prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
                if not prompt:
                    prompt = "Привет!"
                
                response = model.generate_content(prompt)
                await message.reply(response.text)
            except Exception as e:
                await message.reply(f"Ошибка при обработке запроса: {e}")

    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))
