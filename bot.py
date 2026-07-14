import telebot
import requests
import os
import google.genai as genai
from google.genai.types import Part

# === Настройки из переменных окружения ===
TOKEN = os.getenv('TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TOKEN or not GEMINI_API_KEY:
    print("❌ Ошибка: TOKEN или GEMINI_API_KEY не установлены!")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "Анализирую картинку с помощью ИИ... 🤖")
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        
        img_response = requests.get(file_url, timeout=15)
        img_response.raise_for_status()
        
        print(f"✅ Фото скачано ({len(img_response.content)} байт)")
        
        image_part = Part.from_bytes(
            data=img_response.content,
            mime_type="image/jpeg"
        )
        
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                "Опиши подробно, что ты видишь на этой картинке. Ответь на русском языке, интересно и естественно.",
                image_part
            ]
        )
        
        description = response.text.strip()
        print("✅ Описание успешно получено")
        
    except Exception as e:
        print(f"❌ ОШИБКА: {type(e).__name__}: {e}")
        description = "Не удалось обработать картинку 😔 Попробуй ещё раз."
    
    bot.reply_to(message, description)

print("Бот успешно запущен на Render! ✅")
bot.infinity_polling()