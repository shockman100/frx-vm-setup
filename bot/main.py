import os
import sys
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Modulútvonal beállítása (hogy a 'modules' könyvtár működjön)
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
    """Egyszeri adatgyűjtés az árfolyamról és logolás a LOG_FILE-ba."""
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

    # A titkos adatok beolvasása a secrets fájlból
    tg.init_telegram_credentials()

    # Ellenőrizzük, hogy a token sikeresen beolvasható-e
    if not tg.TELEGRAM_TOKEN:
        print("HIBA: A Telegram token nincs beolvasva a secrets fájlból!")
        return

    # Bot inicializálása
    app = ApplicationBuilder().token(tg.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    # Egyszeri árfolyam lekérés és logolás
    await price_logger()

    print("MAIN: sending Telegram start message...")
    await asyncio.to_thread(tg.send_telegram, "🤖 Forex bot elindult és figyel.")
    print("MAIN: Telegram message sent.")

    # Bot eseménykezelésének indítása (polling)
    await app.run_polling()


if __name__ == "__main__":
    # Az asyncio.run(main()) elindítja az aszinkron fő függvényt, 
    # amelyben a bot és a price_logger feladata lefut.
    asyncio.run(main())
