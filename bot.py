from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import ssl

# Отключение проверки SSL (временное решение)
ssl._create_default_https_context = ssl._create_unverified_context

# Ваш токен от BotFather
TOKEN = '8850233883:AAEHj020JIiU7yLpEoYRQNT27N6KC2i_sbQ'

async def parse_avito(url):
    try:
        response = requests.get(url, verify=False)  # Отключаем проверку SSL
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Парсим данные
        title = soup.find('h1', {'data-marker': 'item-view/title-info'}).text
        price = soup.find('span', {'data-marker': 'item-view/price'}).text
        city = soup.find('span', {'class': '_8360df6eedcf8d52'}).text
        seller = soup.find('span', {'class': ''}).text
        reviews = soup.find('a', {'data-marker': 'rating-caption/rating'}).text
        date = soup.find('span', {'data-marker': 'item-view/item-date'}).text
        
        # Формируем шаблон
        result = f"Название: {title}\n"
        result += f"Цена: {price}\n"
        result += f"Город: {city}\n"
        result += f"Продавец: {seller}\n"
        result += f"Количество отзывов: {reviews}\n"
        result += f"Дата когда выложено: {date}"
        
        return result
    except Exception as e:
        return f"Ошибка парсинга: {str(e)}"

async def handle_message(update: Update, context):
    message = update.message
    text = message.text
    
    if 'avito.ru' in text:
        # Ищем ссылку
        url = text.split('avito.ru')[0] + 'avito.ru'
        parsed_data = await parse_avito(url)
        await message.reply_text(parsed_data)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()
