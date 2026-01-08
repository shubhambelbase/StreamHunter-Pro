# 🌊 StreamHunter Pro
### *Vibe Coded by Shubham Belbase*

![StreamHunter Pro Banner](https://img.shields.io/badge/StreamHunter-Pro-00ccff?style=for-the-badge&logo=youtube&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-00a2ed?style=for-the-badge&logo=linux&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**StreamHunter Pro** is the ultimate, modern M3U8 stream extractor and media center. Re-imagined with a stunning "Obsidian & Neon" aesthetic, it combines powerful stream detection with a premium viewing experience.

---

## 🚀 Features

*   **🕵️‍♂️ Intelligent Stream Scanner**: Automatically detects and extracts hidden `.m3u8` and `hls` streams from complex web pages.
*   **🌍 Global TV Browser**: Access thousands of free live TV channels from around the world (powered by IPTV-org).
*   **🎨 Ultra-Premium UI**:
    *   **Obsidian & Neon Theme**: Deep dark modes with vibrant cyan accents.
    *   **Glassmorphism**: Modern transparency effects and floating cards.
    *   **Fluid Animations**: Reactive hover states and smooth transitions.
*   **🎬 Pro Video Player**:
    *   **VLC Native Quality**: Uses libVLC for industry-standard playback stability.
    *   **Smart Fullscreen**: Distraction-free viewing mode.
*   **⭐ Favorites**: Save channels and pin countries for quick access.
*   **💾 Playlist Export**: Convert scanned streams into `.m3u` playlists.

---

## 📦 Installation Details

This repository contains installers and scripts for all major platforms in the `Installers/` directory.


### 🪟 Windows

1. [![Download ZIP](https://img.shields.io/badge/Download_Project_ZIP-ff0066?style=for-the-badge&logo=github)](https://github.com/shubhambelbase/StreamHunter-Pro/releases/download/windows2.1/StreamHunterPro.exe)

2.  Run the `StreamHunterPro.exe` (if available) or build it using the provided `setup_script.iss`.
3.  **Requirement**: [VLC Media Player (64-bit)](https://www.videolan.org/vlc/) must be installed.

### **Linux**
1.  Navigate to `Installers/Linux/`.
2.  Run the install script:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    *(This automatically installs VLC and Python dependencies)*.

### **macOS**
1.  Navigate to `Installers/Mac/`.
2.  Run the install script:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```

---

## 👨‍💻 Developer Setup

Clone the repository and start coding in minutes.

```bash
# 1. Clone
git clone https://github.com/yourusername/StreamHunterPro.git
cd StreamHunterPro

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

### Building the Executable (Windows)
Use the included PyInstaller spec file:
```bash
pyinstaller StreamHunterPro.spec
```

---

## 🛠️ Tech Stack
*   **Core**: Python 3.10+
*   **UI Engine**: CustomTkinter
*   **Media Engine**: LibVLC (python-vlc)
*   **Extraction**: Selenium / Headless Browser integration

---

**Developed with 💙 using Python & CustomTkinter.**
*Vibe Coded for maximum performance and aesthetic.*


