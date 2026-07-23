from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import httpx
from bs4 import BeautifulSoup
import re
import asyncio

# ВСТАВЬТЕ СЮДА НОВЫЙ ТОКЕН ПОСЛЕ ОТЗЫВА СТАРОГО
TOKEN = '8850233883:AAEHj020JIiU7yLpEoYRQNT27N6KC2i_sbQ'

async def parse_avito(url):
    try:
        # Используем httpx для асинхронности и добавляем заголовки, чтобы не банили сразу
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Попытка найти заголовок (селекторы Avito часто меняются, это пример)
            title_tag = soup.find('h1', {'data-marker': 'item-view/title-info'})
            title = title_tag.text.strip() if title_tag else "Не удалось получить название"
            
            price_tag = soup.find('span', {'data-marker': 'item-view/price'})
            price = price_tag.text.strip() if price_tag else "Цена не указана"
            
            # Город и другие данные парсить сложно из-за динамических классов.
            # Для стабильной работы лучше использовать официальное API Avito, если есть доступ.
            city = "Данные скрыты защитой сайта" 
            
            return f"Название: {title}\nЦена: {price}\nГород: {city}\n(Парсинг Avito нестабилен, сайт блокирует автоматические запросы)"
            
    except Exception as e:
        return f"Ошибка при запросе: {str(e)}"

async def handle_message(update: Update, context):
    text = update.message.text
    
    # Ищем ссылку на avito.ru через регулярное выражение (надежнее, чем split)
    match = re.search(r'(https?://[^\s]+)', text)
    if match:
        url = match.group(1)
        if 'avito.ru' in url:
            await update.message.reply_text("Начинаю парсинг (это может занять время)...")
            result = await parse_avito(url)
            await update.message.reply_text(result)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # run_polling имеет параметр timeout для обработки долгих запросов
    app.run_polling(allowed_updates=Update.ALL_TYPES, timeout=30)

if __name__ == '__main__':
    main()
