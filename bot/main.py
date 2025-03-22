import asyncio
import logging
from datetime import datetime

from telegram import Update
from modules.telegram import send_telegram  

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from modules import telegram
from modules.fetch import fetch_price


send_telegram("🚀 Forex bot elindult és figyel.")

# --- Konstansok ---
PAIR = "EURUSD"
LOG_INTERVAL = 60  # másodperc
LOG_FILE = "/logs/price_log.txt"

# --- Parancskezelők ---
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot működik ✅")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else PAIR
    price = await fetch_price(pair)
    await update.message.reply_text(f"{pair} árfolyam: {price}")

# --- Árfolyamlogoló háttérfolyamat ---
async def price_logger():
    while True:
        price = await fetch_price(PAIR)
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"{timestamp} {PAIR} {price}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        await asyncio.sleep(LOG_INTERVAL)

# --- Főfüggvény ---
async def main():
    app = ApplicationBuilder().token(telegram.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    # Árfolyamlogoló indítása háttérben
    asyncio.create_task(price_logger())

    # Start polling
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())


#
