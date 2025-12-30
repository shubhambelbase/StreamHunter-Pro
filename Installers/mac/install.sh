#!/bin/bash
echo "🌊 StreamHunter Pro Installation (macOS)"

# 1. Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Error: Homebrew is required. Visit https://brew.sh/"
    exit 1
fi

# 2. Install System Dependencies
echo "Installing VLC and Python-Tk..."
brew install --cask vlc
brew install python-tk

# 3. Install Python Dependencies
echo "Installing Python Libraries..."
pip3 install -r ../../source/requirements.txt

echo "✅ Installation Complete!"
echo "To run the app: python3 ../../source/main.py"
