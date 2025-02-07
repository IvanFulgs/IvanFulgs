import logging
import openai
import asyncio
import sqlite3
import os
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.enums import ParseMode

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Токен для Telegram бота
TOKEN = os.getenv("BOT_TOKEN")
# API ключ OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ініціалізація бази даних для петицій
DB_FILE = "petitions.db"

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

def save_petition(petition):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR IGNORE INTO petitions (title, votes_collected, days_remaining, url)
                      VALUES (?, ?, ?, ?)''',
                   (petition['title'], petition['votes_collected'], petition['days_remaining'], petition['url']))
    conn.commit()
    conn.close()

def get_petitions():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, votes_collected, days_remaining, url FROM petitions")
    petitions = cursor.fetchall()
    conn.close()
    return [{"title": row[0], "votes_collected": row[1], "days_remaining": row[2], "url": row[3]} for row in petitions]

def get_gpt_response(prompt: str, language: str = 'en') -> str:
    if language == 'uk':
        prompt = f"Please respond in Ukrainian: {prompt}"
    elif language == 'de':
        prompt = f"Please respond in German: {prompt}"
    else:
        prompt = f"Please respond in English: {prompt}"

    try:
        # Використовуємо нову модель gpt-3.5-turbo або gpt-4
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Або "gpt-4" якщо хочете
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error fetching GPT response: {e}")
        return "Sorry, there was an error processing your request."

# Команда /start (привітання)
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привіт! Я бот, який може працювати з англійською, українською та німецькою мовами. "
        "Ви також можете додавати петиції через /gpetition і переглядати список петицій через /lpetition."
    )

# Обробка повідомлень (виклик нейронної мережі для генерації відповіді)
@router.message()
async def chat(message: types.Message):
    user_message = message.text
    language = 'en'

    if any(c.isalpha() for c in user_message):
        if "український" in user_message or "українська" in user_message:
            language = 'uk'
        elif "німецький" in user_message or "німецька" in user_message:
            language = 'de'
        else:
            language = 'en'

    # Отримуємо відповідь від GPT
    response = await get_gpt_response(user_message, language)
    await message.answer(response)

# Команда /gpetition для додавання петиції
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

# Команда /lpetition для перегляду петицій
@router.message(Command("lpetition"))
async def list_petitions(message: types.Message):
    petitions = get_petitions()
    if not petitions:
        await message.answer("📝 Наразі немає жодної доданої петиції.")
        return
    
    result = "📑 <b>Список петицій:</b>\n\n"
    for p in petitions:
        result += f"🔹 <a href='{p['url']}'>{p['title']}</a>\n📊 Голосів зібрано: <b>{p['votes_collected']} з 25000</b>\n⏳ Залишилось днів: <b>{p['days_remaining']}</b>\n\n"
    
    await message.answer(result, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# Отримання інформації про петицію
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

# Запуск бота
async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
