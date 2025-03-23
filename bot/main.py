from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from modules.telegram_sender import send_telegram, read_secret
from ib_insync import IB, Forex, util
import asyncio


# IB csatlakozás próbálása
async def connect_ib():
    ib_host = read_secret("ib_host") or "127.0.0.1"
    ib_port = int(read_secret("ib_port") or 7497)
    ib_client_id = int(read_secret("ib_client_id") or 1)

    ib = IB()
    try:
        await ib.connectAsync(ib_host, ib_port, clientId=ib_client_id, timeout=5)
        return ib
    except Exception as e:
        print(f"❌ IB kapcsolódási hiba: {e}")
        return None


# /status parancs kezelése
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 FRX bot fut és válaszol. Minden rendben.")


# /price parancs kezelése (pl. EUR.USD árfolyam)
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ib = await connect_ib()
    if not ib:
        await update.message.reply_text("⚠️ IB Gateway nem elérhető.")
        return

    try:
        contract = Forex("EURUSD")
        ticker = ib.reqMktData(contract, "", False, False)
        await asyncio.sleep(2)
        price = ticker.marketPrice()
        if price:
            await update.message.reply_text(f"💱 EUR/USD: {price:.5f}")
        else:
            await update.message.reply_text("⚠️ Nem sikerült lekérni az árfolyamot.")
    finally:
        ib.disconnect()


# Ismeretlen üzenet kezelése
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤔 Ismeretlen parancs. Próbáld: /status vagy /price")


def main():
    telegram_token = read_secret("telegram_bot_token")
    if not telegram_token:
        print("❌ Telegram token hiányzik.")
        return

    send_telegram("🤖 FRX bot elindult. Készen áll a parancsokra.")

    app = ApplicationBuilder().token(telegram_token).build()
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_message))  # /ismeretlen

    print("🚀 Bot fut és várja a parancsokat...")
    app.run_polling()


if __name__ == "__main__":
    main()
