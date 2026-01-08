#!/bin/bash
echo "=================================="
echo "StreamHunter Pro - MacOS Installer"
echo "=================================="

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is not installed. Please install it from https://brew.sh/"
    exit 1
fi

echo "[1/3] Installing System Dependencies (VLC + Python)..."
brew install vlc python

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
echo "To run the app, double click 'Start StreamHunter.command'"
echo "=================================="
chmod +x ../Start_StreamHunter.command
