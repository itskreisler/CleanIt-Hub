#!/bin/bash

echo "===================================="
echo "    Installing CleanIt Hub v4.0     "
echo "===================================="

echo "[*] Updating package list..."
apt update -y

echo "[*] Installing Native GTK4 dependencies..."
apt install python3 python3-gi libgtk-4-dev gir1.2-gtk-4.0 curl -y

echo "[*] Setting up app directories..."
mkdir -p ~/.termux-cleaner
mkdir -p ~/.local/share/applications

echo "[*] Downloading CleanIt Hub..."
curl -sL "https://raw.githubusercontent.com/itskreisler/CleanIt-Hub/main/cleanit.py" -o ~/.termux-cleaner/cleanit.py

echo "[*] Downloading Icon..."
curl -sL "https://raw.githubusercontent.com/itskreisler/CleanIt-Hub/main/logo.png" -o ~/.termux-cleaner/logo.png

echo "[*] Adding shortcut to XFCE Start Menu..."
cat <<EOF > ~/.local/share/applications/cleanit-hub.desktop
[Desktop Entry]
Version=4.0
Type=Application
Name=CleanIt Hub
Comment=Termux System Optimizer & Cleaner
Exec=python3 /data/data/com.termux/files/home/.termux-cleaner/cleanit.py
Icon=/data/data/com.termux/files/home/.termux-cleaner/logo.png
Categories=System;Utility;Settings;
Terminal=false
EOF

echo "===================================="
echo "[+] Installation Complete!"
echo "[+] Look for 'CleanIt Hub' in your Start Menu."
echo "===================================="
