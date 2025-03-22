import aiohttp
import requests
import os

# Projekt ID lekérdezése
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

# Secret Manager olvasás
def read_secret(name):
    project_id = get_project_id()
    if not project_id:
        return None
    url = f"https://secretmanager.googleapis.com/v1/projects/{project_id}/secrets/{name}/versions/latest:access"
    headers = {"Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN', '')}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()["payload"]["data"]
    return None

# Tokenek betöltése
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or read_secret("telegram_bot_token")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or read_secret("telegram_chat_id")

# ASZINKRON Telegram üzenetküldő
async def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram token or chat ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print(f"Failed to send Telegram message: {resp.status}")
    except Exception as e:
        print(f"Exception in send_telegram: {e}")
