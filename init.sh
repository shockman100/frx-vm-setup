#!/bin/bash

set -e  # Ha hiba van, azonnal leáll

REPO_URL="https://github.com/shockman100/frx-vm-setup.git"
CLONE_DIR="/tmp/frx-vm-setup"
INSTALL_DIR="/home/shockman100/forex-bot"
SERVICE_NAME="frxbot"
PYTHON_SCRIPT="$INSTALL_DIR/bot/main.py"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# ÖNFRISSÍTÉS: ha nem a legfrissebb példányból futunk
if [ "$SELF_UPDATED" != "1" ]; then
  echo "🔄 Init.sh önfrissítés a GitHubról..."
  rm -rf "$CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"

  echo "🚀 Frissített init.sh futtatása..."
  SELF_UPDATED=1 bash "$CLONE_DIR/init.sh"
  exit $?
fi

# Most már a legfrissebb példány fut tovább
echo ">> Előző telepítés eltávolítása (ha van)..."
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
After=network.target

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

echo ">> systemd újratöltés..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo ">> Szolgáltatás engedélyezése és (újra)indítása..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ A bot telepítve és elindítva."
echo "ℹ️  Napló megtekintése: sudo journalctl -u $SERVICE_NAME -f"
