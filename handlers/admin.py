from aiogram import Router, Bot, types
from aiogram.filters import Command
from aiogram.types import ChatPermissions

router = Router()

@router.message(Command("kick"))
async def kick_user(message: types.Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя, которого хотите кикнуть.")
    user_id = message.reply_to_message.from_user.id
    await bot.kick_chat_member(message.chat.id, user_id)
    await message.reply("Пользователь исключен.")

@router.callback_query(lambda c: c.data == "ban")
async def ban_user(callback: types.CallbackQuery, bot: Bot):
    if callback.message.reply_to_message:
        user_id = callback.message.reply_to_message.from_user.id
        await bot.restrict_chat_member(callback.message.chat.id, user_id, ChatPermissions(can_send_messages=False))
        await callback.answer("Пользователь заблокирован.")

@router.callback_query(lambda c: c.data == "unban")
async def unban_user(callback: types.CallbackQuery, bot: Bot):
    if callback.message.reply_to_message:
        user_id = callback.message.reply_to_message.from_user.id
        await bot.restrict_chat_member(callback.message.chat.id, user_id, ChatPermissions(can_send_messages=True))
        await callback.answer("Пользователь разблокирован.")
