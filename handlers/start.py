from aiogram import Router, types
from aiogram.filters import Command
from keyboards import admin_keyboard

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я чат-менеджер.", reply_markup=admin_keyboard())
