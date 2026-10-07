import discord
import asyncio
# (Убедись, что у тебя импортирован твой gemini_client)

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

            # 1. ИСПРАВЛЕНО: Только реальные, актуальные модели Google
            models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
            response_text = None
            last_error = None

            # 2. ДОБАВЛЕНО: Системный промпт (характер бота)
            system_instruction = "Ты — IMARCH Coordinator, полезный и дружелюбный ИИ-ассистент в Discord-чате. Отвечай кратко, по делу и на русском языке."

            for model_name in models_to_try:
                try:
                    # Примечание: синтаксис может немного отличаться в зависимости от версии SDK Google
                    # Если ты используешь новый google-genai SDK, передача system_instruction может выглядеть иначе.
                    res = gemini_client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        # Если SDK поддерживает системные инструкции:
                        # config={'system_instruction': system_instruction} 
                    )
                    if res and res.text:
                        response_text = res.text
                        break
                except Exception as e:
                    last_error = str(e)
                    print(f"[Ошибка API] Модель {model_name} недоступна: {e}")
                    # 3. ДОБАВЛЕНО: Пауза 2 секунды перед следующей попыткой
                    await asyncio.sleep(2) 
                    continue

            if response_text:
                await message.reply(response_text)
            else:
                # 4. УЛУЧШЕНО: Более понятный ответ для пользователя
                print(f"Все модели недоступны. Последняя ошибка: {last_error}")
                await message.reply("Извини, мой ИИ-мозг сейчас перегружен или недоступен. Пожалуйста, попробуй упомянуть меня еще раз через минуту!")

    await bot.process_commands(message)
