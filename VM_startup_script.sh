#!/bin/bash
# Frissítések és függőségek
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git python3-pip

# Töltsük le a startup scriptet GitHubról vagy GCS-ről
curl -o /root/startup.sh https://raw.githubusercontent.com/shockman100/frx-vm-setup/refs/heads/main/startup.sh

# Futtassuk le a letöltött scriptet
chmod +x /root/startup.sh
bash /root/startup.sh

# Futtassuk le a letöltött scriptet
chmod +x /root/startup.sh
bash /root/startup.sh
