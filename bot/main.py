import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# API vagy más módon az árfolyam lekérése (pl. EURUSD)
async def fetch_price(pair="EURUSD"):
    print(f"Fetching price for {pair}...")
    await asyncio.sleep(2)  # Szimulált várakozás, itt kellene az API vagy más logika
    return 1.2345  # Példa ár

# Telegram /start parancs kezelése
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running.")

# Telegram /ask parancs kezelése, mely árfolyamot kér
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = context.args[0].upper() if context.args else "EURUSD"
    price = await fetch_price(pair)
    await update.message.reply_text(f"{pair} current price: {price}")

# Eseményhurok, amely folyamatosan frissíti az árfolyamot
async def price_logger():
    while True:
        price = await fetch_price()  # Lekérjük az árfolyamot
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"{timestamp} EURUSD {price}\n"  # Árfolyam logolása
        try:
            with open("price_log.txt", "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"❌ LOGGING ERROR: {e}")
        await asyncio.sleep(60)  # 1 percenként frissít

# Telegram bot futtatása és figyelés
async def main():
    print("Bot is starting...")

    # Az alkalmazás tokenjét secretből szerezd meg (például környezeti változókból)
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()  # Ne felejtsd el cserélni a helyes tokenre
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask))

    # Két feladat párhuzamos futtatása: árfolyam figyelés és bot
    asyncio.create_task(price_logger())  # Árfolyam figyelése
    await app.run_polling()  # Telegram bot futtatása

if __name__ == "__main__":
    asyncio.run(main())
