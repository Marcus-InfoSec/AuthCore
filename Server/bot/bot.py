import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
)
import secrets
from db import SessionLocal, License
from datetime import datetime


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

def generate_key_with_mask(mask: str) -> str:
    return ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') if c == 'X' else c for c in mask)

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE, reply_to=None):
    if update.effective_user.id != ADMIN_ID:
        msg = "⛔ Доступ запрещён."
        if reply_to:
            await reply_to.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
        return

    try:
        minutes = int(context.args[0])
        mask = context.args[1] if len(context.args) > 1 else "XXXXXXXX"
        key = generate_key_with_mask(mask)
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❗ Используй: /gen <время в минутах> <маска>\nПример: `/gen 60 XXXX-XXXX`",
            parse_mode="Markdown"
        )
        return

    db = SessionLocal()
    try:
        license = License(
            license_key=key,
            duration_minutes=minutes,
            expires_at=None,
            hwid=None
        )
        db.add(license)
        db.commit()
        msg = (
            f"✅ Ключ создан:\n"
            f"🔑 `{key}`\n"
            f"⏳ Длительность: {minutes} минут\n"
            f"ℹ️ Ключ активируется при первом использовании"
        )
        if reply_to:
            await reply_to.edit_message_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text(msg, parse_mode="Markdown")
    finally:
        db.close()

async def delete_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    if not context.args:
        await update.message.reply_text("❗ Используй: /del <id1> <id2> ...")
        return

    db = SessionLocal()
    deleted = []
    try:
        for arg in context.args:
            if arg.isdigit():
                license = db.get(License, int(arg))
                if license:
                    db.delete(license)
                    deleted.append(arg)
        db.commit()
        if deleted:
            await update.message.reply_text(f"✅ Удалены ID: {', '.join(deleted)}")
        else:
            await update.message.reply_text("❌ Ничего не найдено для удаления.")
    finally:
        db.close()

async def list_keys(update: Update, context: ContextTypes.DEFAULT_TYPE, reply_to=None):
    if update.effective_user.id != ADMIN_ID:
        msg = "⛔ Доступ запрещён."
        if reply_to:
            await reply_to.edit_message_text(msg)
        else:
            await update.message.reply_text(msg)
        return

    db = SessionLocal()
    try:
        keys = db.query(License).order_by(License.id.desc()).limit(10).all()
        if not keys:
            msg = "❗️Нет ключей в базе."
        else:
            msg = "📋 Последние ключи:\n\n"
            for k in keys:
                expires_str = k.expires_at.strftime("%Y-%m-%d %H:%M:%S") if k.expires_at else "Не активирован"
                msg += (
                    f"🆔 {k.id} | 🔑 `{k.license_key}`\n"
                    f"📅 Создан: {k.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"⏳ Длительность: {k.duration_minutes} минут\n"
                    f"⏰ До: {expires_str}\n\n"
                )
        keyboard = [
            [InlineKeyboardButton("➕ Сгенерировать", callback_data="gen")],
            [InlineKeyboardButton("🧪 Проверить", callback_data="check")],
            [InlineKeyboardButton("❌ Удалить", callback_data="del")]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        if reply_to:
            await reply_to.edit_message_text(msg, reply_markup=markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(msg, reply_markup=markup, parse_mode="Markdown")
    finally:
        db.close()

async def check_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    if not context.args:
        await update.message.reply_text("❗️ Использование: /check <ключ>")
        return

    key_to_check = context.args[0]
    db = SessionLocal()
    try:
        license = db.query(License).filter(License.license_key == key_to_check).first()
        if not license:
            await update.message.reply_text(f"❌ Ключ `{key_to_check}` не найден.", parse_mode="Markdown")
            return

        now = datetime.utcnow()
        if license.expires_at and license.expires_at > now:
            active = True
        else:
            active = False

        expires_str = license.expires_at.strftime("%Y-%m-%d %H:%M:%S") if license.expires_at else "Не активирован"

        msg = (
            f"🔑 Ключ: `{license.license_key}`\n"
            f"📅 Создан: {license.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⏰ Истекает: {expires_str}\n"
            f"⏳ Активен: {'Да' if active else 'Нет'}\n"
        )

        if license.hwid:
            msg += f"🖥 HWID: `{license.hwid}`\n"

        await update.message.reply_text(msg, parse_mode="Markdown")
    finally:
        db.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return

    keyboard = [
        [InlineKeyboardButton("📋 Список ключей", callback_data="list")],
        [InlineKeyboardButton("➕ Сгенерировать", callback_data="gen")],
        [InlineKeyboardButton("🧪 Проверить", callback_data="check")],
        [InlineKeyboardButton("❌ Удалить", callback_data="del")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Привет, админ! Выбери действие:", reply_markup=markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "gen":
        await query.edit_message_text("Используй: /gen <минут> <маска>\nПример: `/gen 60 XXXX-XXXX`", parse_mode="Markdown")
    elif query.data == "list":
        await list_keys(update, context, reply_to=query)
    elif query.data == "check":
        await query.edit_message_text("Используй: /check <ключ>")
    elif query.data == "del":
        await query.edit_message_text("Используй: /del <id1> <id2> ...")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("list", list_keys))
    app.add_handler(CommandHandler("check", check_key))
    app.add_handler(CommandHandler("del", delete_key))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("[+] telegram bot run")
    app.run_polling()
