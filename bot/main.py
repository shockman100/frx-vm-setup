import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from modules import telegram, fetch

PAIR = "EURUSD"
LOG_INTERVAL = 60  # seconds
LOG_FILE = "/logs/price_log.txt"


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running.")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        pair = context.args[0].upper()
    else:
        pair = PAIR

    price = await fetch.fetch_price(pair)
    await update.message.reply_text(f"{pair} price: {price}")


async def price_logger():
    while True:
        price = await fetch.fetch_price(PAIR)
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"{timestamp} {PAIR} {price}\n"
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Logging failed: {e}")
        await asyncio.sleep(LOG_INTERVAL)


async def main():
    app = ApplicationBuilder().token(telegram.TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ask", ask))

    asyncio.create_task(price_logger())

    # Aszinkron Telegram üzenet indításkor
    await telegram.send_telegram("Bot started.")

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
