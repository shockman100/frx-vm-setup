#!/bin/bash

LOCK_FILE="/tmp/startup.lock"
if [ -f "$LOCK_FILE" ]; then
  echo "⚠️ Startup script már futott, kilépés."
  exit 0
else
  touch "$LOCK_FILE"
fi

# 🔹 Elérési utak
USER_NAME="shockman100"
USER_HOME="/home/$USER_NAME"
PROJECT_DIR="$USER_HOME/forex-bot"

LOG_DIR="/logs"
mkdir -p "$LOG_DIR"

MAIN_LOG="$LOG_DIR/main_log.log"
ERROR_LOG="$LOG_DIR/error.log"
IB_LOG="$LOG_DIR/ibgateway.log"
FOREX_LOG="$LOG_DIR/forex-bot.log"

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "$(timestamp) $1" | tee -a "$MAIN_LOG"; }

log "🚀 Startup script elindult"

{
  apt update && apt upgrade -y
  apt install -y git python3-pip tmux curl unzip default-jre
  pip install --break-system-packages google-cloud-secret-manager
} >> "$MAIN_LOG" 2>> "$ERROR_LOG"

PROJECT_ID=$(curl -s -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/project/project-id)

read_secret() {
  SECRET_NAME=$1
  python3 -c "
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
name = f'projects/${PROJECT_ID}/secrets/${SECRET_NAME}/versions/latest'
response = client.access_secret_version(request={'name': name})
print(response.payload.data.decode('UTF-8'))
"
}

IB_USER=$(read_secret "ib_username")
IB_PASS=$(read_secret "ib_password")
TELEGRAM_TOKEN=$(read_secret "telegram_bot_token")
TELEGRAM_CHAT_ID=$(read_secret "telegram_chat_id")

log "✅ Secretek sikeresen beolvasva"
log "ℹ️ TELEGRAM_TOKEN karakterek száma: ${#TELEGRAM_TOKEN}"
log "ℹ️ TELEGRAM_CHAT_ID: $TELEGRAM_CHAT_ID"

send_telegram() {
  local msg="$1"
  curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_CHAT_ID" \
    -d "text=$msg" >> "$MAIN_LOG" 2>> "$ERROR_LOG"
}
send_telegram "--------------------------------------------"
send_telegram "📡 Forex VM újraindult – startup script fut"

{
  log "⬇️ IB Gateway előkészítés"
  mkdir -p "$USER_HOME/ibgateway"
  cd "$USER_HOME/ibgateway"
  if [ ! -f "ibgateway-latest.jar" ]; then
    curl -O https://download.interactivebrokers.com/ibgateway/standalone-1010/ibgateway-latest.jar
  fi
  echo "$IB_USER" > user.txt
  echo "$IB_PASS" > pass.txt

  log "🚀 IB Gateway indítása"
  tmux new-session -d -s ibgateway "java -jar ibgateway-latest.jar < user.txt" &>> "$IB_LOG"
} >> "$MAIN_LOG" 2>> "$ERROR_LOG"

{
  log "⬇️ Forex bot letöltés és indítás"
  cd "$USER_HOME"
  if [ ! -d "$PROJECT_DIR/bot" ]; then
    rm -rf "$PROJECT_DIR"
    git clone https://github.com/shockman100/frx-vm-setup.git "$PROJECT_DIR"
  fi
  cd "$PROJECT_DIR"

  if [ ! -f "bot/requirements.txt" ]; then
    echo "❌ Nincs bot/requirements.txt, megszakítom."
    exit 1
  fi

  if [ ! -d "venv" ]; then
  sudo -u shockman100 python3 -m venv venv
  fi

  "$PROJECT_DIR/venv/bin/pip" install --upgrade pip
  "$PROJECT_DIR/venv/bin/pip" install -r bot/requirements.txt

  "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/bot/main.py" &>> "$FOREX_LOG" &
} >> "$MAIN_LOG" 2>> "$ERROR_LOG"

send_telegram "✅ IB Gateway + Forex bot elindult. Napló: $MAIN_LOG"
log "🏁 Startup script teljesítve"
