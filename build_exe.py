import PyInstaller.__main__
import customtkinter
import os
import shutil

# Get CustomTkinter path
ctk_path = os.path.dirname(customtkinter.__file__)
print(f"CustomTkinter found at: {ctk_path}")

# Define args
# Windows separator is ;
add_data = f"{ctk_path};customtkinter"

print("Building StreamHunter Pro...")

PyInstaller.__main__.run([
    'main.py',
    '--name=StreamHunterPro',
    '--onefile',
    '--windowed', # No console
    f'--add-data={add_data}',
    '--clean',
    '--noconfirm',
    # Hidden imports that might be missed
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=vlc',
    '--hidden-import=requests',
    '--hidden-import=playwright',
])

print("Build Complete! Check the 'dist' folder.")
