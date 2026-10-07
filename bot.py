@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            if not gemini_client:
                await message.reply("Ошибка: Не задан GEMINI_API_KEY.")
                return

            prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
            if not prompt:
                prompt = "Привет!"

            # Список моделей по приоритету
            models_to_try = ["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
            response_text = None

            for model_name in models_to_try:
                try:
                    res = gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if res and res.text:
                        response_text = res.text
                        break
                except Exception as e:
                    print(f"Модель {model_name} недоступна: {e}")
                    continue

            if response_text:
                await message.reply(response_text)
            else:
                await message.reply("Серверы Gemini сейчас перегружены. Попробуйте повторить запрос через минуту.")

    await bot.process_commands(message)
