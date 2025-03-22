import os
import requests
import base64

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
    project_id = get_project_id()
    if not project_id:
        return None

    url = f"https://secretmanager.googleapis.com/v1/projects/{project_id}/secrets/{name}/versions/latest:access"
    headers = {"Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN', '')}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            encoded_data = r.json()["payload"]["data"]
            return base64.b64decode(encoded_data).decode("utf-8")
    except Exception as e:
        print(f"Telegram secret read error: {e}")
    return None

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or read_secret("telegram_bot_token")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or read_secret("telegram_chat_id")

def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured properly.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        r = requests.post(url, json=payload, timeout=5)
        if r.status_code != 200:
            print(f"Telegram failed: {r.status_code} - {r.text}")
        else:
            print("Telegram message sent.")
    except Exception as e:
        print(f"Telegram send error: {e}")
