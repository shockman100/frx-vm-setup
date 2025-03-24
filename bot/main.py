import threading
import asyncio
import time
import logging
import requests

from modules import telegram_sender


# --- Globális állapotváltozók ---
status_flags = {
    "ib_loop_active": False,
    "telegram_loop_active": False,
}


# === 1. TELEGRAM BOT THREAD ===
def telegram_loop():
    status_flags["telegram_loop_active"] = True
    telegram_sender.send_telegram("🤖 Forex bot elindult. Írj /status parancsot az állapot lekérdezéséhez.")

    last_update_id = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{telegram_sender.TELEGRAM_TOKEN}/getUpdates"
            if last_update_id:
                url += f"?offset={last_update_id + 1}"
            response = requests.get(url, timeout=5)
            updates = response.json().get("result", [])

            for update in updates:
                last_update_id = update["update_id"]
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id", "")

                if text == "/status" and str(chat_id) == telegram_sender.TELEGRAM_CHAT_ID:
                    msg = f"""📊 Állapotjelentés:
- IB kommunikáció aktív: {'✅' if status_flags['ib_loop_active'] else '❌'}
- Telegram modul aktív: {'✅' if status_flags['telegram_loop_active'] else '❌'}
- Bot főszál fut: ✅"""
                    telegram_sender.send_telegram(msg)

        except Exception as e:
            logging.warning(f"Telegram loop hiba: {e}")
        time.sleep(3)


# === 2. IB KOMMUNIKÁCIÓS ASZINKRON LOOP ===
async def ib_loop():
    status_flags["ib_loop_active"] = True
    while True:
        # Például: árfolyam lekérdezése itt történne
        print("📈 Árfolyam lekérdezés (IB)")
        await asyncio.sleep(10)


def start_ib_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ib_loop())


# === 3. FŐ THREAD ===
def main():
    print("🚀 Bot indul...")
    telegram_sender.init_telegram_credentials()

    # Indítjuk a Telegram szálat
    t1 = threading.Thread(target=telegram_loop, name="TelegramThread", daemon=True)
    t1.start()

    # Indítjuk az IB aszinkron szálat
    t2 = threading.Thread(target=start_ib_thread, name="IBThread", daemon=True)
    t2.start()

    # Fő loop: figyeli a szálakat
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("🛑 Leállítás kérve...")

if __name__ == "__main__":
    main()
