#!/bin/bash

set -e  # Hibánál kilép

REPO_URL="https://github.com/shockman100/frx-vm-setup.git"
CLONE_DIR="/tmp/frx-vm-setup"
INSTALL_DIR="/home/shockman100/forex-bot"
SERVICE_NAME="frxbot"
PYTHON_SCRIPT="$INSTALL_DIR/bot/main.py"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
IBG_DIR="/opt/ibgateway"
IBG_VERSION="1032"
IBG_RUN_PATH="$IBG_DIR/ibgateway-${IBG_VERSION}/ibgateway.run"
JTS_DIR="/home/shockman100/Jts"
IB_SERVICE_FILE="/etc/systemd/system/ibgateway.service"

### 🔁 ÖNFRISSÍTÉS
if [ "$SELF_UPDATED" != "1" ]; then
  echo "🔄 Init.sh önfrissítés a GitHubról..."
  rm -rf "$CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"
  echo "🚀 Frissített init.sh futtatása..."
  SELF_UPDATED=1 bash "$CLONE_DIR/init.sh"
  exit $?
fi

### ⬇️ IB Gateway telepítése
echo "⬇️ IB Gateway letöltése és telepítése..."
sudo mkdir -p "$IBG_DIR"
cd /tmp
wget -q https://download2.interactivebrokers.com/installers/ibgateway/${IBG_VERSION}-standalone/ibgateway-${IBG_VERSION}-standalone-linux-x64.sh -O ibg.sh
chmod +x ibg.sh
yes | sudo ./ibg.sh -q -dir "$IBG_DIR"

echo "⚙️ jts.ini beállítása..."
mkdir -p "$JTS_DIR"
cat <<EOF > "$JTS_DIR/jts.ini"
[Logon]
username=$(gcloud secrets versions access latest --secret="ib_username")
password=$(gcloud secrets versions access latest --secret="ib_password")
trustedIP=127.0.0.1
autologin=true
captiveMode=true
suppresswarning=true
exitonlogout=true
EOF

### 🛠️ IB Gateway systemd service
echo "🛠️ IB Gateway systemd szolgáltatás létrehozása..."
sudo tee "$IB_SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=IB Gateway headless
After=network.target

[Service]
User=shockman100
WorkingDirectory=$JTS_DIR
ExecStart=$IBG_RUN_PATH
Restart=always
TimeoutSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ibgateway.service
sudo systemctl restart ibgateway.service
echo "✅ IB Gateway elindítva."

### 🤖 Bot telepítése
echo ">> Előző bot telepítés eltávolítása (ha van)..."
sudo rm -rf "$INSTALL_DIR"

echo ">> Repo klónozása..."
git clone "$REPO_URL" "$INSTALL_DIR"

echo ">> Python csomagok telepítése..."
pip3 install --break-system-packages -r "$INSTALL_DIR/bot/requirements.txt"

echo ">> Jogosultság beállítása..."
sudo chown -R shockman100:shockman100 "$INSTALL_DIR"

echo ">> frxbot systemd szolgáltatás létrehozása..."
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
