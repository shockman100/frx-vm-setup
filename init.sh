#!/bin/bash

set -e  # Ha hiba van, azonnal leáll

REPO_URL="https://github.com/shockman100/frx-vm-setup.git"
CLONE_DIR="/tmp/frx-vm-setup"
INSTALL_DIR="/home/shockman100/forex-bot"
SERVICE_NAME="frxbot"
PYTHON_SCRIPT="$INSTALL_DIR/bot/main.py"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
IBG_DIR="/opt/ibgateway"
IBG_USER_DIR="/home/shockman100/ibgateway"
IBG_VERSION="1032"

# --- ÖNFRISSÍTÉS ---
if [ "$SELF_UPDATED" != "1" ]; then
  echo "🔄 Init.sh önfrissítés a GitHubról..."
  rm -rf "$CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"
  echo "🚀 Frissített init.sh futtatása..."
  SELF_UPDATED=1 bash "$CLONE_DIR/init.sh"
  exit $?
fi

# --- IB Gateway telepítése (headless) ---
echo "⬇️ IB Gateway letöltése és telepítése..."
sudo mkdir -p "$IBG_DIR"
sudo mkdir -p "$IBG_USER_DIR"
cd /tmp
wget -q https://download2.interactivebrokers.com/installers/ibgateway/${IBG_VERSION}-standalone/ibgateway-${IBG_VERSION}-standalone-linux-x64.sh -O ibg.sh
chmod +x ibg.sh
yes | sudo ./ibg.sh -q -dir "$IBG_DIR"

echo "⚙️ IB Gateway konfigurálása..."
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

# IB Gateway systemd szolgáltatás
echo "🛠️ IB Gateway service létrehozása..."
sudo tee /etc/systemd/system/ibgateway.service > /dev/null <<EOF
[Unit]
Description=IB Gateway headless
After=network.target

[Service]
User=shockman100
ExecStart=$IBG_DIR/ibgatewaystart.sh
WorkingDirectory=$IBG_USER_DIR
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ibgateway.service
sudo systemctl restart ibgateway.service
echo "✅ IB Gateway elindítva."

# --- FRX bot telepítés ---
echo ">> Előző bot telepítés eltávolítása (ha van)..."
sudo rm -rf "$INSTALL_DIR"

echo ">> Repo klónozása a végleges helyre..."
git clone "$REPO_URL" "$INSTALL_DIR"

echo ">> Python csomagok telepítése..."
pip3 install --break-system-packages -r "$INSTALL_DIR/bot/requirements.txt"

echo ">> Jogosultságok beállítása (shockman100)..."
sudo chown -R shockman100:shockman100 "$INSTALL_DIR"

echo ">> systemd szolgáltatás fájl frissítése..."
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

echo ">> systemd újratöltés..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo ">> Szolgáltatás engedélyezése és (újra)indítása..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ A bot és az IB Gateway telepítve és elindítva."
echo "ℹ️ Napló: sudo journalctl -u $SERVICE_NAME -f"
