from google.cloud import secretmanager
import requests
import os

# --- Projekt ID lekérdezése (GCP metadata vagy fallback) ---
def get_project_id():
    try:
        r = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
            timeout=2
        )
        return r.text.strip()
    except Exception:
        return os.getenv("PROJECT_ID")

# --- Secret leolvasása a Secret Managerből ---
def read_secret(name):
    project_id = get_project_id()
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{name}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode("utf-8")

# --- Token és chat ID egyszeri betöltése ---
try:
    TELEGRAM_TOKEN = read_secret("telegram_bot_token")
    TELEGRAM_CHAT_ID = read_secret("telegram_chat_id")
except Exception as e:
    print("❌ Hiba a Telegram secret betöltésekor:", e)
    TELEGRAM_TOKEN = None
    TELEGRAM_CHAT_ID = None

# --- Üzenetküldés ---
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Nincs Telegram token vagy chat_id inicializálva.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        r = requests.post(url, data=data)
        r.raise_for_status()
    except Exception as e:
        print("❌ Telegram hiba:", e)

