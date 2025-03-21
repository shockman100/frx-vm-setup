#!/bin/bash

# 🔹 Log fájlok
LOG_FILE="/var/log/startup.log"
ERROR_LOG="/var/log/startup-error.log"
IB_LOG="/var/log/ibgateway.log"
FOREX_LOG="/var/log/forex-bot.log"

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "$(timestamp) $1" | tee -a "$LOG_FILE"; }

log "🚀 Startup script elindult"

# 🔹 Rendszerfrissítés + alap csomagok
{
  apt update && apt upgrade -y
  apt install -y git python3-pip tmux curl unzip default-jre
  pip install google-cloud-secret-manager
} >> "$LOG_FILE" 2>> "$ERROR_LOG"

# 🔐 PROJECT_ID lekérdezése metadataból
PROJECT_ID=$(curl -s -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/project/project-id)

# 🔐 Titkok beolvasása Secret Managerből
read_secret() {
  python3 -c "
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
name = 'projects/$PROJECT_ID/secrets/$1/versions/latest'
response = client.access_secret_version(request={'name': name})
print(response.payload.data.decode('UTF-8'))
"
}

IB_USER=$(read_secret "ib_username")
IB_PASS=$(read_secret "ib_password")
TELEGRAM_TOKEN=$(read_secret "telegram_bot_token")
TELEGRAM_CHAT_ID=$(read_secret "telegram_chat_id")

log "✅ Titkok beolvasva"

# 🔔 Telegram üzenetküldés függvény
send_telegram() {
  local msg="$1"
  curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_CHAT_ID" \
    -d "text=$msg" > /dev/null
}

send_telegram "📡 Forex VM elindult. IB Gateway és bot indulása folyamatban."

# ⬇️ IB Gateway letöltés + indítás
{
  log "⬇️ IB Gateway letöltése"
  mkdir -p /root/ibgateway
  cd /root/ibgateway
  if [ ! -f "ibgateway-latest.jar" ]; then
    curl -O https://download.interactivebrokers.com/ibgateway/standalone-1010/ibgateway-latest.jar
  fi

  echo "$IB_USER" > user.txt
  echo "$IB_PASS" > pass.txt

  log "🚀 IB Gateway indítása"
  tmux new-session -d -s ibgateway "java -jar ibgateway-latest.jar < user.txt" &>> "$IB_LOG"
} >> "$LOG_FILE" 2>> "$ERROR_LOG"

# ⬇️ Forex bot letöltése + indítása
{
  log "⬇️ Forex bot letöltése és indítása"
  cd /root
  if [ ! -d "forex-bot" ]; then
    git clone https://github.com/YOUR_GITHUB_USER/YOUR_FOREX_REPO.git forex-bot
  fi
  cd forex-bot
  pip install -r requirements.txt
  python main.py &>> "$FOREX_LOG" &
} >> "$LOG_FILE" 2>> "$ERROR_LOG"

send_telegram "✅ IB Gateway és forex bot elindult. Minden rendben."

log "🏁 Startup script befejeződött"
