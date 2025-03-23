import os
import requests
from google.cloud import secretmanager

TELEGRAM_TOKEN = None
TELEGRAM_CHAT_ID = None


def get_project_id():
    try:
        r = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
            timeout=1,
        )
        if r.status_code == 200:
            return r.text
    except Exception:
        return os.environ.get("PROJECT_ID", None)


def read_secret(name):
    try:
        project_id = get_project_id()
        if not project_id:
            print("❌ Nincs PROJECT_ID")
            return None

        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/{name}/versions/latest"
        response = client.access_secret_version(request={"name": secret_name})
        return response.payload.data.decode("utf-8")

    except Exception as e:
        print(f"❌ Hiba a titok beolvasásakor ({name}): {e}")
        return None


def init_telegram_credentials():
    global TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return  # Már inicializálva

    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or read_secret("telegram_bot_token")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or read_secret("telegram_chat_id")

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        print("✅ Telegram tokenek betöltve")
    else:
        print("❌ Telegram tokenek hiányoznak vagy hibásak")


def send_telegram(message: str):
    init_telegram_credentials()

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram token vagy chat_id nincs inicializálva")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            print("✅ Telegram üzenet sikeresen elküldve")
        else:
            print(f"❌ Telegram hiba [{response.status_code}]: {response.text}")
    except Exception as e:
        print(f"❌ Telegram küldési kivétel: {e}")
