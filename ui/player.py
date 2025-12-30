import customtkinter as ctk
import vlc
import sys
import platform
import os
from ui.theme import Theme

class VideoPlayer(ctk.CTkFrame):
    def __init__(self, master, on_fullscreen_request=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_fullscreen_request = on_fullscreen_request
        self.stream_info = None
        self.is_muted = False
        self.volume = 80
        
        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Video takes all space
        self.grid_rowconfigure(1, weight=0) # Controls take min space
        
        # --- VLC Setup ---
        # Robust arguments for stability and embedding
        args = [
            "--no-xlib",
            "--network-caching=5000",
            "--file-caching=5000",
            "--live-caching=5000",
            "--clock-jitter=0",
            "--clock-synchro=0",
            "--avcodec-hw=none",
            "--no-mouse-events",
            "--no-video-title-show",
            "--quiet",
            "--no-osd"
        ]
        self.instance = vlc.Instance(*args)
        self.player = self.instance.media_player_new()
        
        # --- GUI Elements ---
        
        # 1. Video Canvas (The Screen)
        self.canvas = ctk.CTkCanvas(self, bg="#000000", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Binding for double-click fullscreen
        self.canvas.bind("<Double-1>", self._on_double_click)
        self.canvas.bind("<Button-1>", self._on_click) 
        
        # IMPORTANT: Set HWND immediately
        self.player.set_hwnd(self.canvas.winfo_id())
        
        # 2. Control Bar (Overlay/Bottom)
        self.controls_frame = ctk.CTkFrame(self, height=55, fg_color=Theme.BG_SIDEBAR, corner_radius=0)
        self.controls_frame.grid(row=1, column=0, sticky="ew")
        
        # Play/Pause
        self.btn_play = ctk.CTkButton(self.controls_frame, text="▶", width=45, height=35, 
                                      fg_color="transparent", hover_color=Theme.SURFACE_2, 
                                      text_color=Theme.ACCENT_SECONDARY,
                                      border_width=1, border_color=Theme.SURFACE_3,
                                      corner_radius=8,
                                      font=("Arial", 18), command=self.toggle_play)
        self.btn_play.pack(side="left", padx=15, pady=10)
        
        # Reload
        self.btn_reload = ctk.CTkButton(self.controls_frame, text="⟳", width=40, height=35,
                                        fg_color="transparent", hover_color=Theme.SURFACE_2, 
                                        text_color=Theme.TEXT_WHITE,
                                        font=("Arial", 18), command=self.reload_stream)
        self.btn_reload.pack(side="left", padx=5)
        
        # Status Label
        self.lbl_status = ctk.CTkLabel(self.controls_frame, text="Ready", font=("Segoe UI", 12), text_color=Theme.TEXT_GRAY)
        self.lbl_status.pack(side="left", padx=15, fill="x")
        
        # Right Side controls
        if self.on_fullscreen_request:
            self.btn_fs = ctk.CTkButton(self.controls_frame, text="⛶", width=40, height=35,
                                        fg_color="transparent", hover_color=Theme.SURFACE_2,
                                        text_color=Theme.TEXT_WHITE,
                                        font=("Arial", 16), command=self.on_fullscreen_request)
            self.btn_fs.pack(side="right", padx=15)
            
        # Volume
        self.vol_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=100, width=120, height=18, 
                                        button_color=Theme.ACCENT_PRIMARY, progress_color=Theme.ACCENT_PRIMARY, 
                                        command=self.set_volume)
        self.vol_slider.set(self.volume)
        self.vol_slider.pack(side="right", padx=10)
        
        self.btn_mute = ctk.CTkButton(self.controls_frame, text="🔊", width=35, height=35,
                                      fg_color="transparent", hover_color=Theme.SURFACE_2,
                                      text_color=Theme.TEXT_WHITE,
                                      font=("Arial", 16), command=self.toggle_mute)
        self.btn_mute.pack(side="right", padx=2)
        
        # Loop for updates
        self.after(1000, self.update_loop)
        
    def load_stream(self, stream_info):
        self.stream_info = stream_info
        url = stream_info.get('url')
        if not url: return
        
        # Stop existing
        self.player.stop()
        
        # Create Media
        options = []
        if stream_info.get('user_agent'):
            options.append(f":http-user-agent={stream_info['user_agent']}")
        if stream_info.get('referer'):
            options.append(f":http-referrer={stream_info['referer']}")
            
        media = self.instance.media_new(url, *options)
        self.player.set_media(media)
        self.player.play()
        
        # Reset UI
        self.btn_play.configure(text="⏸")
        self.lbl_status.configure(text="Buffering...", text_color=Theme.WARNING)

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.btn_play.configure(text="▶")
            self.lbl_status.configure(text="Paused", text_color=Theme.TEXT_GRAY)
        else:
            self.player.play()
            self.btn_play.configure(text="⏸")
            self.lbl_status.configure(text="Playing", text_color=Theme.ACCENT_SECONDARY)
            
    def reload_stream(self):
        if self.stream_info:
            self.player.stop()
            self.load_stream(self.stream_info)
            
    def stop(self):
        self.player.stop()
        self.btn_play.configure(text="▶")
        self.lbl_status.configure(text="Stopped")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.player.audio_set_mute(self.is_muted)
        self.btn_mute.configure(text="🔇" if self.is_muted else "🔊")

    def set_volume(self, value):
        self.volume = int(value)
        if not self.is_muted:
            self.player.audio_set_volume(self.volume)
            
    def _on_double_click(self, event):
        if self.on_fullscreen_request:
            self.on_fullscreen_request()
            
    def _on_click(self, event):
        # Optional: toggle controls visibility?
        pass

    def toggle_controls(self, show=True):
        if show:
            self.controls_frame.grid(row=1, column=0, sticky="ew")
        else:
            self.controls_frame.grid_forget()

    def update_loop(self):
        # Check player state and health
        state = self.player.get_state()
        
        if state == vlc.State.Ended:
            self.btn_play.configure(text="▶")
            self.lbl_status.configure(text="Ended", text_color=Theme.TEXT_GRAY)
        elif state == vlc.State.Error:
            self.btn_play.configure(text="▶")
            self.lbl_status.configure(text="Stream Error", text_color=Theme.ERROR)
        elif state == vlc.State.Playing:
            self.btn_play.configure(text="⏸")
            # Live stats
            if not self.player.will_play():
                 self.lbl_status.configure(text="Buffering...", text_color=Theme.WARNING)
            else:
                 fps = self.player.get_fps()
                 self.lbl_status.configure(text=f"Live • {fps:.0f} FPS", text_color=Theme.ACCENT_SECONDARY)
            
        self.after(1000, self.update_loop)
