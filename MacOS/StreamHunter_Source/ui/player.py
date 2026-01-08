import customtkinter as ctk
import vlc
import sys
import platform
import os
import time
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
            "--network-caching=2000",    # 2s buffer (Fast start)
            
            # --- Hardware & Perf ---
            "--vout=direct3d11",
            "--avcodec-hw=any",          
            
            # --- Network Resilience ---
            "--http-reconnect",
            "--http-continuous",
            "--http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
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
        self.byte_history = [] 
        self.start_time = 0
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
        
        # Reset Stats
        self.byte_history = []
        self.start_time = time.time()
        
        # Reset UI
        self.btn_play.configure(text="⏸")
        self.lbl_status.configure(text="Connecting...", text_color=Theme.WARNING)

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
            self.lbl_status.configure(text="Stream Ended", text_color=Theme.TEXT_GRAY)
            return self.after(1000, self.update_loop)
            
        elif state == vlc.State.Error:
            self.btn_play.configure(text="▶")
            self.lbl_status.configure(text="⚠ Stream Offline / Broken", text_color=Theme.ERROR)
            return self.after(1000, self.update_loop) # Keep loop in case user reloads
            
        elif state == vlc.State.Opening or state == vlc.State.Buffering:
             # Timeout Check
             if self.start_time and (time.time() - self.start_time > 15.0):
                  self.lbl_status.configure(text="⚠ Connection Timeout", text_color=Theme.ERROR)
             else:
                  self.lbl_status.configure(text="Buffering...", text_color=Theme.WARNING)
                  
        elif state == vlc.State.Playing:
            self.btn_play.configure(text="⏸")
            # Live stats
            fps = self.player.get_fps()
             
            # Calculate Network Speed (Rolling Average)
            media = self.player.get_media()
            speed_str = "0 KB/s"
             
            if media:
                 try:
                     stats = vlc.MediaStats()
                     media.get_stats(stats)
                     
                     found_speed = False
                     
                     # Get monotonic increasing byte count
                     current_bytes = getattr(stats, 'read_bytes', 0)
                     if current_bytes == 0:
                         current_bytes = getattr(stats, 'demux_read_bytes', 0)
                         
                     now = time.time()
                     
                     # Update History
                     self.byte_history.append((now, current_bytes))
                     
                     # Prune old samples (Keep last 3 seconds)
                     while self.byte_history and now - self.byte_history[0][0] > 3.0:
                         self.byte_history.pop(0)
                     
                     # Calculate weighted speed
                     if len(self.byte_history) > 1:
                         b_start = self.byte_history[0][1]
                         b_end = self.byte_history[-1][1]
                         t_start = self.byte_history[0][0]
                         t_end = self.byte_history[-1][0]
                         
                         if b_end < b_start:
                             # Reset detected
                             self.byte_history = [(now, current_bytes)]
                             bps = 0
                         else:
                             diff_bytes = b_end - b_start
                             diff_time = t_end - t_start
                             if diff_time > 0:
                                bps = diff_bytes / diff_time
                             else:
                                bps = 0
                                
                         # Format
                         if bps > 1024 * 1024:
                             speed_str = f"{bps / (1024*1024):.1f} MB/s"
                         else:
                             speed_str = f"{bps / 1024:.0f} KB/s"
                             
                 except Exception:
                     pass

            self.lbl_status.configure(text=f"Live • {speed_str} • {fps:.0f} FPS", text_color=Theme.ACCENT_SECONDARY)
            
        self.after(1000, self.update_loop)
