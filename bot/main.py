import os
import sys
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Modulútvonal beállítása
sys.path.append(os.path.dirname(__file__))

import modules.telegram_sender as tg
from modules.fetch import fetch_price

# Alapértelmezett beállítások
PAIR = "EURUSD"
LOG_INTERVAL = 60  # másodperc
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "price_log.txt")

# Logger beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running.")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else PAIR
    price = await fetch_price(pair)
    await update.message.reply_text(f"{pair} price: {price}")

async def price_logger():
    while True:
        try:
            price = await fetch_price(PAIR)
            timestamp = datetime.utcnow().isoformat()
            log_entry = f"{timestamp} {PAIR} {price}\n"
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, "a") as f:
                f.write(log_entry)
            logger.info("Logged price: %s", log_entry.strip())
        except Exception as e:
            logger.exception("❌ LOGGING ERROR: %s", e)
        await asyncio.sleep(LOG_INTERVAL)

async def main():
    logger.info("MAIN: launching event loop...")

    # Inicializáljuk a Telegram adatait; itt pl. a tg.init_telegram_credentials()
    tg.init_telegram_credentials()

    # Ellenőrizzük, hogy van-e token (ha nincs, nem megy tovább)
    token = tg.TELEGRAM_TOKEN
    if not token:
        logger.error("Telegram token not set! Kérlek, add meg a TELEGRAM_TOKEN környezeti változót.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    # Indítsuk el párhuzamosan a price_logger feladatot
    asyncio.create_task(price_logger())
    logger.info("MAIN: starting Telegram bot polling...")
    await app.run_polling()  # Ez elindítja a bot pollingját

if __name__ == "__main__":
    asyncio.run(main())
