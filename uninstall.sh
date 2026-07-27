#!/bin/bash

echo "===================================="
echo "   Uninstalling CleanIt Hub v4.0    "
echo "===================================="

echo "[*] Removing app directory..."
rm -rf ~/.termux-cleaner

echo "[*] Removing desktop shortcut..."
rm -f ~/.local/share/applications/cleanit-hub.desktop

echo "[*] Removing GTK4 dependencies (optional)..."
echo "    Run: apt remove python3-gi libgtk-4-dev gir1.2-gtk-4.0 -y"
echo "    Or skip if you still need them for other apps."

echo "===================================="
echo "[+] Uninstallation Complete!"
echo "===================================="
