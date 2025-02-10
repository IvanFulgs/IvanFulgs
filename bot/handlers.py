from telegram import Update
from telegram.ext import CallbackContext
from database.db import SessionLocal
from database.models import User, Purchase

def get_or_create_user(telegram_id, username):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        session.commit()
    session.close()
    return user

async def start(update: Update, context: CallbackContext):
    user = get_or_create_user(update.effective_user.id, update.effective_user.username)
    await update.message.reply_text(f"Привет, {update.effective_user.first_name}! Ваш баланс: {user.balance} репортов.")

async def balance(update: Update, context: CallbackContext):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()
    session.close()

    if user:
        await update.message.reply_text(f"Ваш баланс: {user.balance} репортов.")
    else:
        await update.message.reply_text("Ваш профиль не найден. Введите /start.")

async def myid(update: Update, context: CallbackContext):
    await update.message.reply_text(f"Ваш Telegram ID: {update.effective_user.id}")

async def setrole(update: Update, context: CallbackContext):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()

    if not user:
        await update.message.reply_text("Ваш профиль не найден. Введите /start.")
        return

    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите вашу новую роль. Например: /setrole moderator")
        return

    new_role = " ".join(context.args)
    user.role = new_role
    session.commit()
    session.close()

    await update.message.reply_text(f"Ваша роль обновлена: {new_role}")

async def admins(update: Update, context: CallbackContext):
    session = SessionLocal()
    admins_list = session.query(User).filter(User.role != "user").all()
    session.close()

    admin_names = "\n".join([f"{admin.username} - {admin.role}" for admin in admins_list])
    await update.message.reply_text(f"Список администраторов:\n{admin_names}")

async def buy(update: Update, context: CallbackContext):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=update.effective_user.id).first()

    if not user:
        await update.message.reply_text("Ваш профиль не найден. Введите /start.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Пожалуйста, укажите товар и его цену. Например: /buy item_name 100")
        return

    item_name = " ".join(context.args[:-1])
    try:
        price = int(context.args[-1])
    except ValueError:
        await update.message.reply_text("Неверный формат цены. Введите число.")
        return

    if user.balance < price:
        await update.message.reply_text("Недостаточно средств.")
        return

    user.balance -= price
    purchase = Purchase(user_id=user.id, item_name=item_name, price=price)
    session.add(purchase)
    session.commit()
    session.close()

    await update.message.reply_text(f"Вы успешно купили {item_name} за {price} репортов.")
