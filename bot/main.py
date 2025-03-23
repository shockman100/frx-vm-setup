import os
import sys
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Modulútvonal beállítása
sys.path.append(os.path.dirname(__file__))

import modules.telegram_sender as tg
from modules.fetch import fetch_price

PAIR = "EURUSD"
LOG_INTERVAL = 60  # másodperc
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


async def main():
    print("MAIN: launching event loop...")

    tg.init_telegram_credentials()

    app = ApplicationBuilder().token(tg.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    # Indítsd el a price_logger()-t egy külön szálon
    await price_logger()

    # Telegram polling indítása
    print("MAIN: sending Telegram start message...")
    await asyncio.to_thread(tg.send_telegram, "🤖 Forex bot elindult és figyel.")
    print("MAIN: Telegram message sent.")
    await app.run_polling()  # Indítsd el az eseménykezelést

if __name__ == "__main__":
    loop = asyncio.get_event_loop()  # Ha már futó eseményhurok van, akkor ezt használjuk
    loop.run_until_complete(main())  # Futtasd a fő aszinkron funkciót
