import os
import requests
import base64
import aiohttp

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
        print("TELEGRAM: GCP metadata lookup failed")
        return os.environ.get("PROJECT_ID", None)

def read_secret(name):
    project_id = get_project_id()
    if not project_id:
        print("TELEGRAM: No project ID found")
        return None

    url = f"https://secretmanager.googleapis.com/v1/projects/{project_id}/secrets/{name}/versions/latest:access"
    headers = {"Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN', '')}"}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            encoded_data = r.json()["payload"]["data"]
            return base64.b64decode(encoded_data).decode("utf-8")
        else:
            print(f"TELEGRAM: Secret request failed ({r.status_code})")
    except Exception as e:
        print(f"TELEGRAM: Exception during secret read: {e}")
    return None

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or read_secret("telegram_bot_token")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or read_secret("telegram_chat_id")


async def send_telegram(message: str):
    print(f"TELEGRAM: preparing to send -> {message}")

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("TELEGRAM: Missing token or chat ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print(f"TELEGRAM: failed to send message ({resp.status})")
                    print(await resp.text())
                else:
                    print("TELEGRAM: message sent successfully.")
    except Exception as e:
        print(f"TELEGRAM: exception during send -> {e}")
