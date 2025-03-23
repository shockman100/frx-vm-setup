from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from ib_insync import IB, Forex
import asyncio
import subprocess


# 🔐 Titok beolvasása gcloud-ból
def read_secret(name: str) -> str:
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={name}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print(f"❌ Hiba a titok beolvasásakor ({name})")
        return ""


def get_secret_or_default(name: str, default: str) -> str:
    value = read_secret(name)
    return value if value else default


# 📡 IB árfolyam lekérés
async def get_forex_price() -> str:
    try:
        ib = IB()
        await ib.connectAsync(ib_host, ib_port, clientId=ib_client_id, timeout=5)

        contract = Forex('EURUSD')
        ticker = ib.reqMktData(contract, '', False, False)

        # Várunk max. 2 másodpercet árra
        for _ in range(20):
            await asyncio.sleep(0.1)
            if ticker.bid and ticker.ask:
                break

        bid = ticker.bid or 0
        ask = ticker.ask or 0
        await ib.disconnect()
        return f"💶 EUR/USD árfolyam:\nBid: {bid:.5f}\nAsk: {ask:.5f}"

    except Exception as e:
        return f"❌ Hiba IB árfolyam lekérés közben: {e}"


# 📬 Telegram parancs: /status
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 FRX bot fut és válaszol. Minden rendben.")


# 📬 Telegram parancs: /price
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await get_forex_price()
    await update.message.reply_text(msg)


# 📬 Minden más szöveg
async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Ismeretlen parancs. Használható: /status, /price")


# 🚀 Főprogram
def main():
    global ib_host, ib_port, ib_client_id

    telegram_token = get_secret_or_default("telegram_bot_token", "")
    if not telegram_token:
        print("❌ Telegram token hiányzik.")
        return

    ib_host = get_secret_or_default("ib_host", "127.0.0.1")
    ib_port = int(get_secret_or_default("ib_port", "7497"))
    ib_client_id = int(get_secret_or_default("ib_client_id", "1"))

    print(f"📡 Csatlakozás: {ib_host}:{ib_port}, clientId={ib_client_id}")

    app = ApplicationBuilder().token(telegram_token).build()
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    print("🚀 Bot fut és várja a parancsokat...")
    app.run_polling()


if __name__ == "__main__":
    main()
