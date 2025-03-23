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
    print("MAIN: initializing bot")

    # 👇 LÉTREHOZZUK A LOOPOT KÉZZEL
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    tg.init_telegram_credentials()

    # Egyszeri árfolyam logolás
    loop.run_until_complete(price_logger())

    tg.send_telegram("🤖 Forex bot elindult és figyel.")

    # Bot elindítása
    app = ApplicationBuilder().token(tg.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    # Indítás blocking módon (itt már van loop)
    app.run_polling()


if __name__ == "__main__":
    main()
