#!/bin/bash

set -e

REPO_URL="https://github.com/shockman100/frx-vm-setup.git"
CLONE_DIR="/tmp/frx-vm-setup"
INSTALL_DIR="/home/shockman100/forex-bot"
SERVICE_NAME="frxbot"
PYTHON_SCRIPT="$INSTALL_DIR/bot/main.py"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

# ÖNFRISSÍTÉS
if [ "$SELF_UPDATED" != "1" ]; then
  echo "🔄 Init.sh önfrissítés a GitHubról..."
  rm -rf "$CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"
  echo "🚀 Frissített init.sh futtatása..."
  SELF_UPDATED=1 bash "$CLONE_DIR/init.sh"
  exit $?
fi

echo ">> Előző telepítés eltávolítása (ha van)..."
sudo rm -rf "$INSTALL_DIR"

echo ">> Repo klónozása..."
git clone "$REPO_URL" "$INSTALL_DIR"

echo ">> Python csomagok telepítése..."
pip3 install --break-system-packages -r "$INSTALL_DIR/bot/requirements.txt"

echo ">> IB Gateway telepítése..."
sudo apt-get update
sudo apt-get install -y openjdk-17-jre xvfb wget unzip

IB_DIR="/opt/ibgateway"
IB_VERSION="1019"
IB_URL="https://download2.interactivebrokers.com/installers/ibgateway/IBGateway$IB_VERSION.zip"

sudo mkdir -p "$IB_DIR"
cd "$IB_DIR"
sudo wget -q "$IB_URL" -O ibgateway.zip
sudo unzip -o ibgateway.zip -d "$IB_DIR"
sudo rm ibgateway.zip

sudo tee /usr/local/bin/start-ibgateway.sh > /dev/null <<EOF
#!/bin/bash
xvfb-run -a $IB_DIR/IBGateway/ibgateway &>/var/log/ibgateway.log
EOF
sudo chmod +x /usr/local/bin/start-ibgateway.sh

sudo tee /etc/systemd/system/ibgateway.service > /dev/null <<EOF
[Unit]
Description=IB Gateway
After=network.target

[Service]
ExecStart=/usr/local/bin/start-ibgateway.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ibgateway.service
sudo systemctl start ibgateway.service

echo ">> Jogosultságok beállítása..."
sudo chown -R shockman100:shockman100 "$INSTALL_DIR"

echo ">> systemd szolgáltatás fájl frissítése..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=FRX bot
After=network.target ibgateway.service
StartLimitIntervalSec=60
StartLimitBurst=5

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

echo ">> Szolgáltatás indítása..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "✅ A bot telepítve és elindítva."
echo "ℹ️ Napló megtekintése: sudo journalctl -u $SERVICE_NAME -f"
