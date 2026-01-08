import sys
import os
import ctypes

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_vlc_installation():
    """
    Check if VLC is installed and reachable.
    """
    try:
        import vlc
        # Try to instantiate to see if DLLs are found
        i = vlc.Instance()
        i.release()
        return True
    except (ImportError, OSError, ctypes.CDLLError):
        return False

if __name__ == "__main__":
    # Check for VLC
    if not check_vlc_installation():
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showerror(
            "VLC Not Found", 
            "VLC Media Player is required for playback.\n\nPlease install VLC Media Player 64-bit (if using Python 64-bit) from videolan.org."
        )
        # We continue anyway, but playback won't work. 
        # Actually better to warn and continue so they can still extract.
        
    try:
        from ui.app import StreamHunterApp
        app = StreamHunterApp()
        app.mainloop()
    except Exception as e:
        print(f"Error launching app: {e}")
        input("Press Enter to close...")
