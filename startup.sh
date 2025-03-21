#!/bin/bash
echo "🚀 Fő startup script elindult!"

# Telepítések
sudo apt update
sudo apt install -y git python3-pip tmux

# IB Gateway beállítás
mkdir -p /root/ibgateway
cd /root/ibgateway
if [ ! -f "ibgateway-latest.jar" ]; then
    curl -O https://download.interactivebrokers.com/ibgateway/standalone-1010/ibgateway-latest.jar
fi

# IB Gateway indítása
tmux new-session -d -s ibgateway "java -jar /root/ibgateway/ibgateway-latest.jar"

# Forex adatletöltő futtatása
cd /root
git clone https://github.com/YOUR_GITHUB_USER/YOUR_FOREX_REPO.git forex-bot
cd forex-bot
pip install -r requirements.txt
python main.py

