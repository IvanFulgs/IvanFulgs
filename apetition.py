import requests
import json
import logging
import asyncio
import sqlite3
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
import os

# Ваш токен Telegram-бота
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

BASE_URL = "https://petition.president.gov.ua"
TARGET_VOTES = 25000
DB_FILE = "petitions.db"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS petitions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        votes_collected INTEGER,
                        days_remaining INTEGER,
                        url TEXT UNIQUE)''')
    conn.commit()
    conn.close()

# Збереження петиції в БД
def save_petition(petition):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO petitions (title, votes_collected, days_remaining, url)
                      VALUES (?, ?, ?, ?)''',
                   (petition['title'], petition['votes_collected'], petition['days_remaining'], petition['url']))
    conn.commit()
    conn.close()

# Отримання всіх петицій з БД
def get_petitions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, votes_collected, days_remaining, url FROM petitions")
    petitions = cursor.fetchall()
    conn.close()
    return [{"title": row[0], "votes_collected": row[1], "days_remaining": row[2], "url": row[3]} for row in petitions]

# Парсинг інформації про петицію
def get_petition_info(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.select_one("h1").text.strip()
    votes_collected = int(soup.select_one(".petition_votes_txt span").text.strip().replace(" ", ""))
    days_remaining_text = soup.select_one(".votes_progress_label").text.strip()
    days_remaining = int(''.join(filter(str.isdigit, days_remaining_text)))
    
    return {"title": title, "votes_collected": votes_collected, "days_remaining": days_remaining, "url": url}

# Оновлення інформації у базі перед відправкою списку
def update_petition_info():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    petitions = get_petitions()  # Отримуємо всі збережені петиції

    for p in petitions:
        updated_info = get_petition_info(p["url"])  # Отримуємо актуальні дані
        if updated_info:
            cursor.execute('''UPDATE petitions 
                              SET votes_collected = ?, days_remaining = ? 
                              WHERE url = ?''',
                           (updated_info['votes_collected'], updated_info['days_remaining'], p["url"]))
    
    conn.commit()
    conn.close()

# Додавання нової петиції командою /gpetition
@router.message(Command("gpetition"))
async def add_petition(message: types.Message):
    url = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not url:
        await message.answer("Будь ласка, надайте посилання на петицію.")
        return
    
    existing_petitions = get_petitions()
    if any(p['url'] == url for p in existing_petitions):
        await message.answer("❌ Цю петицію вже додано.")
        return
    
    petition_info = get_petition_info(url)
    if petition_info:
        save_petition(petition_info)
        await message.answer(f"✅ Петиція додана!\n\n📑 <a href='{petition_info['url']}'>{petition_info['title']}</a>\n📊 Голосів зібрано: <b>{petition_info['votes_collected']}</b>\n⏳ Залишилось днів: <b>{petition_info['days_remaining']}</b>", parse_mode=ParseMode.HTML)
    else:
        await message.answer("❌ Не вдалося отримати інформацію про петицію.")

# Відображення списку петицій командою /lpetition
@router.message(Command("lpetition"))
async def list_petitions(message: types.Message):
    update_petition_info()  # Оновлюємо інформацію перед виведенням
    petitions = get_petitions()

    if not petitions:
        await message.answer("📝 Наразі немає жодної доданої петиції.")
        return
    
    result = "📑 <b>Список петицій:</b>\n\n"
    for p in petitions:
        result += f"🔹 <a href='{p['url']}'>{p['title']}</a>\n📊 Голосів зібрано: <b>{p['votes_collected']} з 25000</b>\n⏳ Залишилось днів: <b>{p['days_remaining']}</b>\n\n"
    
    await message.answer(result, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# Запуск бота
async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
