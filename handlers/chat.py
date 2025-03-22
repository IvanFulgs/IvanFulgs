from aiogram import Router, types
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

router = Router()

@router.chat_member()
async def on_user_join(event: ChatMemberUpdated):
    if event.new_chat_member.status == ChatMemberStatus.MEMBER:
        await event.chat.send_message(f"Добро пожаловать, {event.new_chat_member.user.full_name}!")
