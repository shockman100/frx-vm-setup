import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import modules.telegram as tg
from modules.fetch import fetch_price
import os

PAIR = "EURUSD"
LOG_INTERVAL = 60  # másodperc
LOG_FILE = "/home/shockman100/forex-bot/bot/logs/price_log.txt"

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running.")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else PAIR
    price = await fetch_price(pair)
    await update.message.reply_text(f"{pair} price: {price}")

async def price_logger():
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
    print("MAIN: starting async main()")

    app = ApplicationBuilder().token(tg.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    asyncio.create_task(price_logger())

    print("MAIN: próbálkozás Telegram üzenet küldésével...")
    await asyncio.to_thread(tg.send_telegram, "🤖 Forex bot elindult és figyel.")
    print("MAIN: Telegram üzenetküldés befejeződött.")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
