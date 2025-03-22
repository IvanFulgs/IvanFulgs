from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("info"))
async def bot_info(message: types.Message):
    await message.answer("Этот бот создан разработчиком @YourUsername.")

@router.callback_query(lambda c: c.data == "staff")
async def show_staff(callback: types.CallbackQuery):
    await callback.message.answer("В беседе есть роли: Администратор, Модератор, Участник.")
    await callback.answer()
