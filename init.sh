#!/bin/bash

set -e  # Ha hiba van, azonnal leáll

REPO_URL="https://github.com/shockman100/frx-vm-setup.git"
CLONE_DIR="/tmp/frx-vm-setup"
INSTALL_DIR="/home/shockman100/forex-bot"
SERVICE_NAME="frxbot"
PYTHON_SCRIPT="$INSTALL_DIR/bot/main.py"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
IB_DIR="/opt/ibgateway"
IB_JAR="IBGatewayLatestStandalone.jar"
IB_URL="https://download2.interactivebrokers.com/ibgateway/Installers/$IB_JAR"
IB_SERVICE="/etc/systemd/system/ibgateway.service"

# ÖNFRISSÍTÉS
if [ "$SELF_UPDATED" != "1" ]; then
  echo "🔄 Init.sh önfrissítés a GitHubról..."
  rm -rf "$CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"

  echo "🚀 Frissített init.sh futtatása..."
  SELF_UPDATED=1 bash "$CLONE_DIR/init.sh"
  exit $?
fi

# Python bot telepítés
echo ">> Előző telepítés eltávolítása (ha van)..."
sudo rm -rf "$INSTALL_DIR"
echo ">> Repo klónozása a végleges helyre..."
git clone "$REPO_URL" "$INSTALL_DIR"

echo ">> Python csomagok telepítése..."
pip3 install --break-system-packages -r "$INSTALL_DIR/bot/requirements.txt"

echo ">> Jogosultságok beállítása (shockman100)..."
sudo chown -R shockman100:shockman100 "$INSTALL_DIR"

# systemd bot szolgáltatás
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
StartLimitIntervalSec=60
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF

# Java telepítés
if ! command -v java &> /dev/null; then
  echo ">> Java nincs telepítve, telepítés..."
  sudo apt update
  sudo apt install -y default-jre
fi

# IB Gateway letöltés
echo ">> IB Gateway telepítése..."
sudo mkdir -p "$IB_DIR"
sudo wget -q -O "$IB_DIR/$IB_JAR" "$IB_URL"

# IB Gateway script
sudo tee "$IB_DIR/start.sh" > /dev/null <<EOF
#!/bin/bash
exec java -jar $IB_DIR/$IB_JAR &> $IB_DIR/gateway.log
EOF
sudo chmod +x "$IB_DIR/start.sh"

# IB Gateway systemd service
echo ">> IB Gateway systemd szolgáltatás létrehozása..."
sudo tee "$IB_SERVICE" > /dev/null <<EOF
[Unit]
Description=IB Gateway
After=network.target

[Service]
ExecStart=$IB_DIR/start.sh
Restart=always
RestartSec=10
User=shockman100

[Install]
WantedBy=multi-user.target
EOF

# systemd újratöltés és szolgáltatások indítása
echo ">> systemd újratöltés..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo ">> IB Gateway engedélyezése és indítása..."
sudo systemctl enable ibgateway
sudo systemctl restart ibgateway

echo ">> FRX bot engedélyezése és indítása..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ A bot és az IB Gateway telepítve és elindítva."
echo "ℹ️  Napló megtekintése: sudo journalctl -u $SERVICE_NAME -f"
