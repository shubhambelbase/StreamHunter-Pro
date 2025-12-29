#!/bin/bash
echo "🌊 StreamHunter Pro Installation (Linux)"

# 1. Install System Dependencies (VLC + Tkinter)
# Detect package manager
if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y vlc python3-tk python3-pip
elif command -v dnf &> /dev/null; then
    echo "Detected Fedora/RHEL..."
    sudo dnf install -y vlc python3-tkinter python3-pip
elif command -v pacman &> /dev/null; then
    echo "Detected Arch Linux..."
    sudo pacman -S vlc tk python-pip
else
    echo "Unknown package manager. Please manually install VLC and Python3-Tkinter."
fi

# 2. Install Python Dependencies
echo "Installing Python Libraries..."
pip3 install -r ../../source/requirements.txt --break-system-packages

echo "✅ Installation Complete!"
echo "To run the app: python3 ../../source/main.py"
