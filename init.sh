#!/bin/bash

set -e  # Hibára álljon le

# === 🌐 Naplózás bekapcsolása ===
LOG_FILE="$HOME/frx-init.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "📜 Telepítés naplózása: $LOG_FILE"

echo "🕒 $(date) – Telepítés indítása..."

REPO_URL="https://github.com/shockman100/frx-vm-setup.git"
CLONE_DIR="/tmp/frx-vm-setup"
INSTALL_DIR="/home/shockman100/forex-bot"
SERVICE_NAME="frxbot"
PYTHON_SCRIPT="$INSTALL_DIR/bot/main.py"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
IBG_DIR="/opt/ibgateway"
IBG_USER_DIR="/home/shockman100/ibgateway"
IBG_VERSION="1032"

# === 🔄 ÖNFRISSÍTÉS ===
if [ "$SELF_UPDATED" != "1" ]; then
  echo "🕒 $(date) – Init.sh önfrissítés a GitHubról..."
  rm -rf "$CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"
  echo "🚀 Frissített init.sh futtatása..."
  SELF_UPDATED=1 bash "$CLONE_DIR/init.sh"
  exit $?
fi

# === ⬇️ IB Gateway telepítése ===
echo "🕒 $(date) – Java futtatókörnyezet telepítése (IB Gateway-hez szükséges)..."
sudo apt update
sudo apt install -y default-jre

echo "🕒 $(date) – IB Gateway stabil verzió letöltése és telepítése..."
sudo mkdir -p "$IBG_DIR"
sudo mkdir -p "$IBG_USER_DIR"
sudo chown -R shockman100:shockman100 "$IBG_USER_DIR"
cd /tmp
wget -q https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh -O ibg.sh
chmod +x ibg.sh
sudo ./ibg.sh -q -overwrite -dir "$IBG_DIR" < /dev/null

# === ⚙️ IB Gateway konfigurálása ===
echo "🕒 $(date) – IB Gateway konfigurálása..."
cat <<EOF > "$IBG_USER_DIR/jts.ini"
[Logon]
username=$(gcloud secrets versions access latest --secret="ib_username")
password=$(gcloud secrets versions access latest --secret="ib_password")
trustedIP=127.0.0.1
autologin=true
captiveMode=true
suppresswarning=true
exitonlogout=true
EOF

# === 🛠️ IB Gateway systemd szolgáltatás ===
echo "🕒 $(date) – IB Gateway systemd szolgáltatás létrehozása..."
sudo tee /etc/systemd/system/ibgateway.service > /dev/null <<EOF
[Unit]
Description=IB Gateway headless
After=network.target

[Service]
User=shockman100
ExecStart=$IBG_DIR/ibgateway --headless -gwsilent -jts $IBG_USER_DIR/jts.ini
WorkingDirectory=$IBG_USER_DIR
Restart=always
TimeoutSec=30

[Install]
WantedBy=multi-user.target
EOF


sudo systemctl daemon-reload
sudo systemctl enable ibgateway.service
sudo systemctl restart ibgateway.service
echo "✅ IB Gateway elindítva."

# === 🤖 Bot telepítése ===
echo "🕒 $(date) – Előző bot telepítés eltávolítása (ha van)..."
sudo rm -rf "$INSTALL_DIR"

echo "🕒 $(date) – Repo klónozása..."
git clone "$REPO_URL" "$INSTALL_DIR"

echo "🕒 $(date) – Python csomagok telepítése..."
pip3 install --break-system-packages -r "$INSTALL_DIR/bot/requirements.txt"

echo "🕒 $(date) – Jogosultság beállítása..."
sudo chown -R shockman100:shockman100 "$INSTALL_DIR"

echo "🕒 $(date) – frxbot systemd szolgáltatás létrehozása..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=FRX bot
After=network.target ibgateway.service

[Service]
User=shockman100
WorkingDirectory=$INSTALL_DIR/bot
ExecStart=/usr/bin/python3 $PYTHON_SCRIPT
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ A bot és az IB Gateway telepítve és elindítva."
echo "📡 Ellenőrzés: sudo journalctl -u $SERVICE_NAME -f"
echo "🌐 IB port: netstat -tuln | grep 7497"

# === 📩 TELEGRAM ÉRTESÍTÉS A VÉGÉN ===
echo "🕒 $(date) – Telegram értesítés küldése..."

PROJECT_ID=$(curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/project/project-id)
TELEGRAM_TOKEN=$(gcloud secrets versions access latest --secret="telegram_bot_token" --project="$PROJECT_ID")
TELEGRAM_CHAT_ID=$(gcloud secrets versions access latest --secret="telegram_chat_id" --project="$PROJECT_ID")

if [[ -n "$TELEGRAM_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d chat_id="$TELEGRAM_CHAT_ID" \
    -d text="✅ Telepítés befejezve a VM-en! Ellenőrizd: journalctl -u frxbot -f"
  echo "📨 Telegram értesítés elküldve."
else
  echo "⚠️ Telegram token vagy chat_id hiányzik – nem küldhető értesítés."
fi

echo "🏁 Kész. Log: $LOG_FILE"
