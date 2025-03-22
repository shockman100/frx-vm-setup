from google.cloud import secretmanager
import requests
import os

def get_project_id():
    try:
        import requests
        r = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
            timeout=2
        )
        return r.text.strip()
    except Exception:
        return os.getenv("PROJECT_ID")

def read_secret(name):
    project_id = get_project_id()
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{name}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    return response.payload.data.decode("utf-8")

def send_telegram(message):
    token = read_secret("telegram_bot_token")
    chat_id = read_secret("telegram_chat_id")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {'chat_id': chat_id, 'text': message}
    try:
        r = requests.post(url, data=data)
        r.raise_for_status()
    except Exception as e:
        print("❌ Telegram hiba:", e)

