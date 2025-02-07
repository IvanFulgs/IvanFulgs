from aiogram import types
from aiogram.filters import Command
from aiogram.types import ParseMode
from petitions import get_petition_info
from db import save_petition, get_petitions, update_petition_info
from aiogram import Router

router = Router()

# Команда /start
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Я бот для управління петиціями. Використовуй команду /help для отримання списку команд.")

# Команда /help
@router.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
        "Ось доступні команди:\n"
        "/start — Привітання\n"
        "/help — Допомога\n"
        "/gpetition <url> — Додати петицію\n"
        "/lpetition — Переглянути список петицій"
    )

# Команда /gpetition — додавання петиції
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

# Команда /lpetition — перегляд списку петицій
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
