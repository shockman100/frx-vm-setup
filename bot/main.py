import os
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from modules.telegram_sender import send_telegram
from modules.fetch import fetch_price

PAIR = "EURUSD"
LOG_INTERVAL = 60  # másodperc

# Dinamikus logfájl elérési útvonal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "price_log.txt")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running.")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else PAIR
    price = await fetch_price(pair)
    await update.message.reply_text(f"{pair} price: {price}")


async def price_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    while True:
        price = await fetch_price(PAIR)
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"{timestamp} {PAIR} {price}\n"
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"LOGGING ERROR: {e}")
        await asyncio.sleep(LOG_INTERVAL)


async def main():
    print("MAIN: starting async main()")

    app = ApplicationBuilder().token(send_telegram.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    asyncio.create_task(price_logger())

    print("MAIN: próbálkozás Telegram üzenet küldésével...")
    await asyncio.to_thread(send_telegram, "🤖 Forex bot elindult és figyel.")
    print("MAIN: Telegram üzenetküldés befejeződött.")

    await app.run_polling()


if __name__ == "__main__":
    print("MAIN: launching event loop...")
    asyncio.run(main())
