#!/bin/bash
echo "=================================="
echo "StreamHunter Pro - Linux Installer"
echo "=================================="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 could not be found. Please install python3 first."
    exit 1
fi

echo "[1/3] Installing System Dependencies (VLC + Tkinter)..."
# Detect package manager
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y vlc python3-tk python3-pip python3-venv
elif command -v dnf &> /dev/null; then
    sudo dnf install -y vlc python3-tkinter python3-pip
elif command -v pacman &> /dev/null; then
    sudo pacman -S vlc python-tk python-pip
else
    echo "Warning: Could not detect apt/dnf/pacman. Please ensure VLC and Python-Tk are installed manually."
fi

echo "[2/3] Setting up Python Environment..."
cd StreamHunter_Source
python3 -m venv venv
source venv/bin/activate

echo "[3/3] Installing Python Libraries..."
pip install --upgrade pip
pip install -r requirements.txt
playwright install

echo "=================================="
echo "Installation Complete!"
echo "To run the app, executing ./run.sh"
echo "=================================="
chmod +x ../run.sh
