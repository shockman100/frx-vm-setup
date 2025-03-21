#!/bin/bash

# 🔹 Log fájlok
LOG_FILE="/var/log/startup.log"
ERROR_LOG="/var/log/startup-error.log"
IB_LOG="/var/log/ibgateway.log"
FOREX_LOG="/var/log/forex-bot.log"

timestamp() {
  date +"%Y-%m-%d %H:%M:%S"
}

log() {
  echo "$(timestamp) $1" | tee -a "$LOG_FILE"
}

log "🚀 Fő startup script elindult"

# 🔹 Rendszerfrissítés, alap csomagok
{
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y git python3-pip tmux curl unzip openjdk-11-jre
  pip install --quiet google-cloud-secret-manager
} >> "$LOG_FILE" 2>> "$ERROR_LOG"

# 🔹 Secretek beolvasása Google Secret Managerből
log "🔐 Titkos IB belépési adatok beolvasása"

PROJECT_ID="forex-data-collector"

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

log "✅ IB felhasználónév és jelszó beolvasva"

# 🔹 IB Gateway letöltése
log "⬇️ IB Gateway letöltése"

mkdir -p /root/ibgateway
cd /root/ibgateway
if [ ! -f "ibgateway-latest.jar" ]; then
  curl -O https://download.interactivebrokers.com/ibgateway/standalone-1010/ibgateway-latest.jar
fi

# 🔹 (Opcionális) IB konfiguráció fájl generálása automatikus loginhoz
log "⚙️ IB konfiguráció írása"

cat > /root/ibgateway/ib_login.txt <<EOF
User=$IB_USER
Password=$IB_PASS
EOF

# 🔹 IB Gateway indítása
log "🚀 IB Gateway indítása"
tmux new-session -d -s ibgateway "java -jar /root/ibgateway/ibgateway-latest.jar < /root/ibgateway/ib_login.txt" &>> "$IB_LOG"

# 🔹 Forex bot letöltése és indítása
log "⬇️ Forex adatletöltő letöltése"

cd /root
if [ ! -d "forex-bot" ]; then
  git clone https://github.com/YOUR_GITHUB_USER/YOUR_FOREX_REPO.git forex-bot
fi

cd forex-bot
pip install -r requirements.txt &>> "$LOG_FILE"

log "🚀 Forex bot indítása"
python main.py &>> "$FOREX_LOG"

log "🏁 Startup script befejeződött"


