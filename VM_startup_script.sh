#!/bin/bash

# Frissítések és függőségek
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git python3-pip

# Hová tegye a projektet? → saját mappába
USER_HOME="/home/$(logname)"
TARGET_DIR="$USER_HOME/forex-bot"

# Startup script letöltése
curl -o "$TARGET_DIR/startup.sh" https://raw.githubusercontent.com/shockman100/frx-vm-setup/refs/heads/main/startup.sh

# Futtatás
chmod +x "$TARGET_DIR/startup.sh"
bash "$TARGET_DIR/startup.sh"
