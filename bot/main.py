import os
import sys
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Modulútvonal beállítása (hogy a 'modules' könyvtár működjön)
sys.path.append(os.path.dirname(__file__))

import modules.telegram_sender as tg  # Helyes modul importálás
from modules.fetch import fetch_price

PAIR = "EURUSD"
LOG_INTERVAL = 60  # másodperc
LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "price_log.txt")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Válasz a /status parancsra, hogy jelezze a bot állapotát."""
    await update.message.reply_text("✅ Bot is running.")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Válasz a /ask parancsra, hogy lekérje az árfolyamot."""
    pair = context.args[0].upper() if context.args else PAIR
    price = await fetch_price(pair)
    await update.message.reply_text(f"{pair} price: {price}")


async def price_logger():
    """Folyamatosan logolja az árfolyamokat egy fájlba."""
    while True:
        price = await fetch_price(PAIR)
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"{timestamp} {PAIR} {price}\n"
        try:
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            with open(LOG_FILE, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"❌ LOGGING ERROR: {e}")
        await asyncio.sleep(LOG_INTERVAL)


async def main():
    print("MAIN: launching event loop...")

    tg.init_telegram_credentials()  # Telegram tokenok inicializálása

    app = ApplicationBuilder().token(tg.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    asyncio.create_task(price_logger())  # Árfolyam logolása háttérben

    print("MAIN: sending Telegram start message...")
    await asyncio.to_thread(tg.send_telegram, "🤖 Forex bot elindult és figyel.")  # Telegram üzenet küldése
    print("MAIN: Telegram message sent.")

    await app.run_polling()  # Polling indítása


if __name__ == "__main__":
    asyncio.run(main())  # Az aszinkron fő program futtatása
