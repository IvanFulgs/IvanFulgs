import os
import asyncio
from telegram.ext import Application, CommandHandler
from bot.handlers import start, balance, myid, setrole, admins, buy
from database.db import init_db
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


async def main():
    init_db()
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("myid", myid))
    application.add_handler(CommandHandler("setrole", setrole))
    application.add_handler(CommandHandler("admins", admins))
    application.add_handler(CommandHandler("buy", buy))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
