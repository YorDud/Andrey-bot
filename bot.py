from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from telegram.request import HTTPXRequest
import httpx
from bs4 import BeautifulSoup
import re

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '8850233883:AAEHj020JIiU7yLpEoYRQNT27N6KC2i_sbQ'
PROXY_URL = 'socks5://127.0.0.1:10808'

async def parse_avito(url):
    try:
        async with httpx.AsyncClient(timeout=10.0, proxy=PROXY_URL) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('h1', {'data-marker': 'item-view/title-info'})
            title = title_tag.text.strip() if title_tag else "Не удалось получить название"

            price_tag = soup.find('span', {'data-marker': 'item-view/price'})
            price = price_tag.text.strip() if price_tag else "Цена не указана"

            return f"Название: {title}\nЦена: {price}"

    except Exception as e:
        return f"Ошибка при запросе: {str(e)}"

async def handle_message(update: Update, context):
    logger.info(f"Получено сообщение: {update.message.text}")
    text = update.message.text
    match = re.search(r'(https?://[^\s]+)', text)
    if match:
        url = match.group(1)
        if 'avito.ru' in url:
            await update.message.reply_text("Начинаю парсинг...")
            result = await parse_avito(url)
            await update.message.reply_text(result)

def main():
    request = HTTPXRequest(proxy=PROXY_URL)
    app = Application.builder().token(TOKEN).request(request).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES, timeout=30)

if __name__ == '__main__':
    main()

