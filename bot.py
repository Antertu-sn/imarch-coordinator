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
                    model="gemini-1.5/2.0-flash",
                    contents=prompt,
                )
                await message.reply(response.text if response.text else "Получен пустой ответ.")
            except Exception as e:
                print(f"Ошибка Gemini: {e}")
                await message.reply(f"Произошла ошибка: {e}")

    await bot.process_commands(message)
