import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from modules.telegram_sender import init_telegram_credentials, send_telegram
from modules.secret_reader import read_secret


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Üdv! A bot aktív. Használd a /status parancsot az állapot lekérdezéséhez.")


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 A bot fut és figyel. IB kapcsolódás jelenleg nincs inicializálva.")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Ismeretlen parancs. Próbáld meg: /status")


async def run():
    init_telegram_credentials()

    telegram_token = read_secret("telegram_bot_token")
    if not telegram_token:
        print("❌ Nincs Telegram token")
        return

    send_telegram("🚀 Bot fut és várja a parancsokat...")

    app = ApplicationBuilder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))  # új: ismeretlen parancsok kezelése

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(run())
