import os
import sys
from datetime import datetime
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Modulútvonal beállítása
sys.path.append(os.path.dirname(__file__))

import modules.telegram_sender as tg
from modules.fetch import fetch_price

PAIR = "EURUSD"
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "price_log.txt")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running.")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else PAIR
    price = await fetch_price(pair)
    await update.message.reply_text(f"{pair} price: {price}")


async def price_logger():
    price = await fetch_price(PAIR)
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"{timestamp} {PAIR} {price}\n"
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"❌ LOGGING ERROR: {e}")


def main():
    # Inicializálás
    tg.init_telegram_credentials()
    if not tg.TELEGRAM_TOKEN:
        print("❌ Nincs TELEGRAM_TOKEN!")
        return

    # Egyszeri logolás
    try:
        asyncio.run(price_logger())
    except RuntimeError:
        # Ha már fut a loop (pl. systemd alatt), akkor így
        loop = asyncio.get_event_loop()
        loop.create_task(price_logger())

    # Üzenetküldés szinkronban
    tg.send_telegram("🤖 Forex bot elindult és figyel.")

    # Bot létrehozása és indítása
    app = ApplicationBuilder().token(tg.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    # Itt nincs async → nincs hiba!
    app.run_polling()


if __name__ == "__main__":
    main()
