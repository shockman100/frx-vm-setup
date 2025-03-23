#!/bin/bash

# Beállítások
REPO_URL="https://github.com/shockman100/frx-vm-setup.git"
INSTALL_DIR="/home/shockman100/forex-bot"
SERVICE_NAME="frxbot"
PYTHON_SCRIPT="$INSTALL_DIR/bot/main.py"

echo ">> Repo klónozása..."
git clone "$REPO_URL" "$INSTALL_DIR"

echo ">> Követelmények telepítése..."
pip3 install --break-system-packages -r "$INSTALL_DIR/bot/requirements.txt"

echo ">> Jogosultság beállítása (shockman100)..."
chown -R shockman100:shockman100 "$INSTALL_DIR"

echo ">> systemd szolgáltatás létrehozása..."
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=FRX bot
After=network.target

[Service]
User=shockman100
WorkingDirectory=$INSTALL_DIR/bot
ExecStart=/usr/bin/python3 $PYTHON_SCRIPT
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo ">> systemd újratöltés és szolgáltatás indítása..."
systemctl daemon-reexec
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo ">> Kész! A bot automatikusan fut."
