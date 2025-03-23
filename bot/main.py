from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from modules.telegram_sender import send_telegram, read_secret
from ib_insync import IB, Stock

import asyncio

def get_secret_or_default(name: str, default: str) -> str:
    value = read_secret(name)
    return value if value else default

# Telegram parancskezelő: /status
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 FRX bot fut és válaszol. Minden rendben.")

# Telegram parancskezelő: /price EURUSD
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = "EURUSD"  # default
    if context.args:
        symbol = context.args[0].upper()

    await update.message.reply_text(f"🔍 Árfolyam lekérése: {symbol}...")

    try:
        ib = IB()
        ib_host = get_secret_or_default("ib_host", "127.0.0.1")
        ib_port = int(get_secret_or_default("ib_port", "7497"))
        ib_client_id = int(get_secret_or_default("ib_client_id", "1"))

        ib.connect(ib_host, ib_port, clientId=ib_client_id)

        contract = Forex(symbol)
        ticker = ib.reqMktData(contract, snapshot=True)

        # Várjuk meg az adatot
        ib.sleep(2)

        if ticker.bid is not None and ticker.ask is not None:
            msg = f"💱 {symbol} árfolyam:\n• Bid: {ticker.bid}\n• Ask: {ticker.ask}"
        else:
            msg = f"⚠️ Nem érkezett árfolyamadat a {symbol} instrumentumhoz."

        await update.message.reply_text(msg)
        ib.disconnect()

    except Exception as e:
        await update.message.reply_text(f"❌ Hiba történt: {e}")

def main():
    telegram_token = get_secret_or_default("telegram_bot_token", "")
    if not telegram_token:
        print("❌ Telegram token hiányzik.")
        return

    ib_host = get_secret_or_default("ib_host", "127.0.0.1")
    ib_port = int(get_secret_or_default("ib_port", "7497"))
    ib_client_id = int(get_secret_or_default("ib_client_id", "1"))

    send_telegram(f"🤖 FRX bot elindult.\n📡 Csatlakozás: {ib_host}:{ib_port}, clientId={ib_client_id}")

    app = ApplicationBuilder().token(telegram_token).build()
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("price", price_command))  # új parancs

    print("🚀 Bot fut és várja a parancsokat...")
    app.run_polling()

if __name__ == "__main__":
    main()
