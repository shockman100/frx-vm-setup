from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from modules.telegram_sender import send_telegram, read_secret


def get_secret_or_default(name: str, default: str) -> str:
    value = read_secret(name)
    return value if value else default


# Telegram parancskezelő: /status
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 FRX bot fut és válaszol. Minden rendben.")


def main():
    telegram_token = get_secret_or_default("telegram_bot_token", "")
    if not telegram_token:
        print("❌ Telegram token hiányzik.")
        return

    # Opcionális: IB csatlakozási adatok (még nem használjuk)
    ib_host = get_secret_or_default("ib_host", "127.0.0.1")
    ib_port = int(get_secret_or_default("ib_port", "7497"))
    ib_client_id = int(get_secret_or_default("ib_client_id", "1"))

    send_telegram(f"🤖 FRX bot elindult.\n📡 Csatlakozás: {ib_host}:{ib_port}, clientId={ib_client_id}")

    app = ApplicationBuilder().token(telegram_token).build()
    app.add_handler(CommandHandler("status", status_command))

    print("🚀 Bot fut és várja a parancsokat...")
    app.run_polling()  # <- nem async!


if __name__ == "__main__":
    main()
