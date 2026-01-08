import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import threading

# Core imports
from core.extractor import StreamExtractor
from core.channel_manager import ChannelManager
from core.favorites_manager import FavoritesManager

# UI Imports
from ui.player import VideoPlayer
from ui.theme import Theme

# Setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class StreamHunterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Window Setup ---
        self.title("StreamHunter Pro")
        self.geometry("1400x900")
        self.minsize(1100, 750)
        self.configure(fg_color=Theme.BG_MAIN)
        
        # --- Managers ---
        self.extractor = StreamExtractor()
        self.channel_manager = ChannelManager()
        self.fav_manager = FavoritesManager()
        
        # --- Layout Configuration ---
        self.grid_columnconfigure(1, weight=1) # Content Area
        self.grid_rowconfigure(0, weight=1)
        
        # --- 1. Sidebar (Navigation) ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=Theme.BG_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1) # Spacer
        
        # Branding
        self._init_sidebar_branding()
        
        # Nav Buttons (Stored to update state)
        self.nav_buttons = {}
        self._create_nav_btn("scanner", "🔍  Stream Scanner", 2)
        self._create_nav_btn("browser", "🌍  World TV", 3)
        self._create_nav_btn("favorites", "⭐  Favorites", 4)
        
        # Status footer
        self.status_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_container.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        
        self.status_indicator = ctk.CTkLabel(self.status_container, text="●", font=("Arial", 12), text_color=Theme.SUCCESS)
        self.status_indicator.pack(side="left", padx=(0, 5))
        
        self.status_label = ctk.CTkLabel(self.status_container, text="System Ready", font=Theme.FONT_SMALL, text_color=Theme.TEXT_GRAY, anchor="w")
        self.status_label.pack(side="left", fill="x")

        # --- 2. Content Area (Container for Views) ---
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        
        # --- Views ---
        self.view_scanner = self._init_scanner_view()
        self.view_browser = self._init_browser_view()
        self.view_favorites = self._init_favorites_view()
        
        # State
        self.active_view = None
        self.is_fullscreen = False
        self.bind("<Escape>", lambda e: self.exit_fullscreen())
        
        # Initial Load
        self.show_view("scanner")
        self.after(500, self.load_channels_db)
        self.after(2000, self.cleanup_favorites_on_start) # Auto-Verify Favs
        
    def _init_sidebar_branding(self):
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=25, pady=(40, 20), sticky="w")
        
        ctk.CTkLabel(brand_frame, text="STREAM", font=("Roboto", 26, "bold"), text_color=Theme.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(brand_frame, text="HUNTER", font=("Roboto", 26, "bold"), text_color=Theme.ACCENT_SECONDARY).pack(anchor="w")
        
        ctk.CTkLabel(self.sidebar, text="v2.1 PRO EDITION", font=("Segoe UI", 10, "bold"), text_color=Theme.TEXT_DARK).grid(row=1, column=0, padx=25, pady=(0, 40), sticky="w")

    def _create_nav_btn(self, key, text, row):
        # Container for the button to allow for the 'active border' effect
        container = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=50)
        container.grid(row=row, column=0, sticky="ew", pady=5)
        
        # The actual button
        btn = ctk.CTkButton(
            container, 
            text=text, 
            anchor="w", 
            fg_color="transparent", 
            text_color=Theme.TEXT_GRAY, 
            hover_color=Theme.SURFACE_2, 
            height=45, 
            corner_radius=8,
            font=Theme.FONT_BODY_BOLD, 
            command=lambda: self.show_view(key)
        )
        btn.pack(side="right", fill="x", expand=True, padx=(15, 15))
        
        # Active Indicator (Hidden by default)
        indicator = ctk.CTkFrame(container, width=4, height=30, fg_color=Theme.ACCENT_SECONDARY, corner_radius=2)
        
        self.nav_buttons[key] = {'btn': btn, 'indicator': indicator, 'container': container}

    def show_view(self, view_name):
        # Update Nav State
        for key, item in self.nav_buttons.items():
            if key == view_name:
                item['btn'].configure(fg_color=Theme.SURFACE_1, text_color=Theme.TEXT_WHITE)
                item['indicator'].pack(side="left", padx=(10, 0), pady=10) # Show indicator
            else:
                item['btn'].configure(fg_color="transparent", text_color=Theme.TEXT_GRAY)
                item['indicator'].pack_forget()
        
        # Switch View
        self.view_scanner.grid_forget()
        self.view_browser.grid_forget()
        self.view_favorites.grid_forget()
        
        if view_name == "scanner":
            self.view_scanner.grid(row=0, column=0, sticky="nsew")
        elif view_name == "browser":
            self.view_browser.grid(row=0, column=0, sticky="nsew")
        elif view_name == "favorites":
            self.refresh_favorites_view()
            self.view_favorites.grid(row=0, column=0, sticky="nsew")
            
        self.active_view = view_name

    # --- VIEW: SCANNER ---
    def _init_scanner_view(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1) 
        
        # Top Bar (Floating Capsule Style)
        self.scanner_top_bar = ctk.CTkFrame(frame, height=70, fg_color="transparent")
        self.scanner_top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # URL Input Container
        input_container = ctk.CTkFrame(self.scanner_top_bar, fg_color=Theme.SURFACE_1, corner_radius=12, border_width=1, border_color=Theme.SURFACE_2)
        input_container.pack(side="left", fill="x", expand=True, ipady=5)
        
        self.entry_url = ctk.CTkEntry(
            input_container, 
            placeholder_text="Paste Video URL to Scan...", 
            height=40,
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 14),
            placeholder_text_color=Theme.TEXT_DARK
        )
        self.entry_url.pack(fill="x", padx=15, pady=5)
        
        # Action Buttons
        btn_scan = ctk.CTkButton(
            self.scanner_top_bar, 
            text="START SCAN", 
            width=140, 
            height=50, 
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color="#2b7ab8",
            corner_radius=12,
            font=("Segoe UI", 13, "bold"),
            command=self.start_extraction
        )
        btn_scan.pack(side="left", padx=(15, 0))
        
        btn_save = ctk.CTkButton(
            self.scanner_top_bar, 
            text="EXPORT M3U", 
            width=140, 
            height=50, 
            fg_color=Theme.SURFACE_1, 
            text_color=Theme.TEXT_WHITE,
            hover_color=Theme.SURFACE_2, 
            corner_radius=12,
            font=("Segoe UI", 13, "bold"),
            command=self.save_playlist
        )
        btn_save.pack(side="right", padx=(15, 0))
        
        # Main Content Split
        self.scanner_split_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.scanner_split_frame.grid(row=1, column=0, sticky="nsew")
        self.scanner_split_frame.grid_columnconfigure(0, weight=3) # Player
        self.scanner_split_frame.grid_columnconfigure(1, weight=1) # Results
        self.scanner_split_frame.grid_rowconfigure(0, weight=1)
        
        # Player Area
        self.player_container = ctk.CTkFrame(self.scanner_split_frame, fg_color="#000", corner_radius=0) # Player is square
        self.player_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        self.player_container.grid_rowconfigure(0, weight=1)
        self.player_container.grid_columnconfigure(0, weight=1)
        
        self.player = VideoPlayer(self.player_container, on_fullscreen_request=self.toggle_fullscreen)
        self.player.grid(row=0, column=0, sticky="nsew")
        
        # Results Sidebar
        self.scanner_results_area = ctk.CTkFrame(self.scanner_split_frame, fg_color=Theme.SURFACE_1, corner_radius=15)
        self.scanner_results_area.grid(row=0, column=1, sticky="nsew")
        self.scanner_results_area.grid_rowconfigure(1, weight=1)
        self.scanner_results_area.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.scanner_results_area, text="DETECTED STREAMS", font=("Segoe UI", 12, "bold"), text_color=Theme.TEXT_GRAY).grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        self.scan_results_frame = ctk.CTkScrollableFrame(self.scanner_results_area, label_text=None, fg_color="transparent")
        self.scan_results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        return frame

    # --- VIEW: BROWSER ---
    def _init_browser_view(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        # Controls
        ctrl = ctk.CTkFrame(frame, height=60, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Search Bar
        search_container = ctk.CTkFrame(ctrl, fg_color=Theme.SURFACE_1, corner_radius=10)
        search_container.pack(side="left", fill="x", expand=True, ipady=4)
        
        self.entry_search = ctk.CTkEntry(search_container, placeholder_text="Search Global Channels...", height=40, fg_color="transparent", border_width=0, font=("Segoe UI", 14))
        self.entry_search.pack(fill="x", padx=15)
        self.entry_search.bind("<Return>", self.perform_search)
        
        ctk.CTkButton(ctrl, text="SEARCH", width=120, height=48, fg_color=Theme.ACCENT_PRIMARY, corner_radius=10, command=lambda: self.perform_search(None)).pack(side="left", padx=15)
        
        self.btn_db_status = ctk.CTkButton(ctrl, text="UPDATE DB", width=120, height=48, fg_color=Theme.SURFACE_1, hover_color=Theme.SURFACE_2, corner_radius=10, command=self.load_channels_db)
        self.btn_db_status.pack(side="left")
        
        # Styled Treeview Container
        tree_container = ctk.CTkFrame(frame, fg_color=Theme.SURFACE_1, corner_radius=15)
        tree_container.grid(row=1, column=0, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        # Treeview Styling
        style = ttk.Style()
        style.theme_use("default")
        
        # Configure colors for Treeview
        style.configure("Treeview", 
                        background=Theme.SURFACE_1, 
                        fieldbackground=Theme.SURFACE_1, 
                        foreground=Theme.TEXT_WHITE, 
                        rowheight=35, 
                        font=("Segoe UI", 11),
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        background=Theme.BG_MAIN, 
                        foreground="white", 
                        font=("Segoe UI", 12, "bold"),
                        borderwidth=0,
                        relief="flat")
                        
        style.map("Treeview", 
                  background=[('selected', Theme.ACCENT_PRIMARY)], 
                  foreground=[('selected', 'white')])
        
        style.map("Treeview.Heading", 
                  background=[('active', Theme.SURFACE_2)])

        self.tree = ttk.Treeview(tree_container, columns=("url", "group"), show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="  Name / Category", anchor="w")
        self.tree.heading("url", text="Stream URL", anchor="w")
        self.tree.heading("group", text="Country", anchor="w")
        self.tree.column("#0", width=400)
        self.tree.column("url", width=0, stretch=False)
        self.tree.column("group", width=150)
        
        # Remove borders
        self.tree.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Custom Scrollbar
        scroll = ctk.CTkScrollbar(tree_container, command=self.tree.yview, fg_color="transparent")
        scroll.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<Button-3>", self.on_tree_right_click)
        
        return frame

    # --- VIEW: FAVORITES ---
    def _init_favorites_view(self):
        frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1) # 2 Column layout
        frame.grid_rowconfigure(1, weight=1) 
        
        # Channels Section
        c_frame = ctk.CTkFrame(frame, fg_color=Theme.SURFACE_1, corner_radius=15)
        c_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 15))
        c_frame.grid_columnconfigure(0, weight=1)
        c_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(c_frame, text="FAVORITE CHANNELS", font=("Roboto", 16, "bold"), text_color=Theme.TEXT_WHITE).grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        self.fav_channels_frame = ctk.CTkScrollableFrame(c_frame, fg_color="transparent")
        self.fav_channels_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Countries Section
        co_frame = ctk.CTkFrame(frame, fg_color=Theme.SURFACE_1, corner_radius=15)
        co_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(15, 0))
        co_frame.grid_columnconfigure(0, weight=1)
        co_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(co_frame, text="PINNED COUNTRIES", font=("Roboto", 16, "bold"), text_color=Theme.TEXT_WHITE).grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        self.fav_countries_frame = ctk.CTkScrollableFrame(co_frame, fg_color="transparent")
        self.fav_countries_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        return frame

    # --- LOGIC ---
    def start_extraction(self):
        url = self.entry_url.get().strip()
        if not url: return
        if not url.startswith("http"): url = "https://" + url
        
        self.status_label.configure(text=f"Scanning {url}...", text_color=Theme.ACCENT_SECONDARY)
        self.status_indicator.configure(text_color=Theme.WARNING)
        
        for w in self.scan_results_frame.winfo_children(): w.destroy()
        self.extractor.extract(url, self.add_scan_result, self.on_scan_complete)
        
    def add_scan_result(self, stream_info):
        self.after(0, lambda: self._create_result_card(stream_info))
        
    def _create_result_card(self, stream_info):
        url = stream_info['url']
        name = url.split("/")[-1].split("?")[0]
        
        card = ctk.CTkFrame(self.scan_results_frame, fg_color=Theme.SURFACE_2, height=60, corner_radius=8)
        card.pack(fill="x", pady=4)
        
        # Label with truncation
        lbl = ctk.CTkLabel(card, text=name if len(name) < 40 else name[:37]+"...", anchor="w", font=("Segoe UI", 12, "bold"))
        lbl.pack(side="top", fill="x", padx=10, pady=(8, 2))
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent", height=25)
        btn_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        btn_play = ctk.CTkButton(btn_frame, text="▶ PLAY", width=70, height=24, fg_color=Theme.ACCENT_PRIMARY, corner_radius=6, command=lambda: self.play_stream(stream_info))
        btn_play.pack(side="left")
        
        btn_fav = ctk.CTkButton(btn_frame, text="⭐", width=30, height=24, fg_color=Theme.SURFACE_3, corner_radius=6, command=lambda: self.add_fav_channel(name, url, "Scanned"))
        btn_fav.pack(side="left", padx=5)

    def on_scan_complete(self):
        self.after(0, lambda: self._set_status_ready(f"Scan Complete. Found {len(self.extractor.found_streams)} streams."))

    def _set_status_ready(self, msg):
        self.status_label.configure(text=msg, text_color=Theme.TEXT_GRAY)
        self.status_indicator.configure(text_color=Theme.SUCCESS)

    def play_stream(self, stream_info):
        # Switch to Scanner
        self.show_view("scanner")
        self.player.load_stream(stream_info)
        self.status_label.configure(text=f"Playing stream...", text_color=Theme.ACCENT_PRIMARY)
        self.status_indicator.configure(text_color=Theme.ACCENT_PRIMARY)

    def toggle_fullscreen(self):
        if self.is_fullscreen: self.exit_fullscreen()
        else: self.enter_fullscreen()
        
    def enter_fullscreen(self):
        # STRATEGY: Do NOT move Player. Hide everything else.
        self.is_fullscreen = True
        self.player.toggle_controls(False)
        
        # 1. Attributes
        self.attributes("-fullscreen", True)
        self.update_idletasks()
        
        # 2. Hide surrounding UI
        self.sidebar.grid_remove() # Col 0
        
        # Remove padding from content area to fill screen
        self.content_area.grid_configure(padx=0, pady=0)
        
        # In Scanner View: Hide Top Bar and Results Column
        if self.active_view == "scanner":
             self.scanner_top_bar.grid_remove()
             self.scanner_results_area.grid_remove()
             
             # Force Player to take full width
             self.scanner_split_frame.grid_columnconfigure(0, weight=1)
             self.scanner_split_frame.grid_columnconfigure(1, weight=0)
             self.player_container.grid_configure(padx=0)
             
        # Focus player for keyboard shortcuts if any
        self.player.focus_set()
        
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.player.toggle_controls(True)
            
            # 1. Attributes
            self.attributes("-fullscreen", False)
            self.update_idletasks()
            
            # 2. Restore UI
            self.sidebar.grid()
            self.content_area.grid_configure(padx=30, pady=30)
            
            if self.active_view == "scanner":
                self.scanner_top_bar.grid()
                self.scanner_results_area.grid()
                
                # Restore Split Weights
                self.scanner_split_frame.grid_columnconfigure(0, weight=3)
                self.scanner_split_frame.grid_columnconfigure(1, weight=1)
                self.player_container.grid_configure(padx=(0, 20))

    def load_channels_db(self):
        self.btn_db_status.configure(state="disabled", text="LOADING...")
        self.status_label.configure(text="Updating Worldwide Channels (Fast Mode)...", text_color=Theme.WARNING)
        
        # Fast load without verification
        self.channel_manager.fetch_channels(
            on_complete=lambda: self.after(0, self.on_db_loaded)
        )

    def on_db_progress(self, current, total, message="Working..."):
        # Not used anymore but kept for compatibility
        pass

    def on_db_loaded(self):
        self.btn_db_status.configure(state="normal", text="REFRESH DB")
        count = sum(len(v) for v in self.channel_manager.channels_by_category.values())
        self._set_status_ready(f"Loaded {count} channels.")
        self.populate_tree()

    def populate_tree(self, items=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        if items:
            for ch in items[:300]:
                self.tree.insert("", "end", text=ch['name'], values=(ch['url'], ch.get('group', 'Unknown')))
        else:
            data = self.channel_manager.channels_by_category
            for cat in sorted(data.keys()):
                # Use a dummy value for group to make row selection easier
                pid = self.tree.insert("", "end", text=f"{cat} ({len(data[cat])})", values=("", "Category"))
                for ch in data[cat]:
                    self.tree.insert(pid, "end", text=ch['name'], values=(ch['url'], cat))

    def perform_search(self, event):
        q = self.entry_search.get()
        if not q: self.populate_tree(); return
        res = self.channel_manager.search_channels(q)
        self.populate_tree(res)

    def on_tree_double_click(self, event):
        item = self.tree.focus()
        if not item: return
        vals = self.tree.item(item)['values']
        # Check if it has a URL
        if vals and vals[0]: 
            self.play_stream({'url': vals[0]})
        else:
            if self.tree.item(item, "open"): self.tree.item(item, open=False)
            else: self.tree.item(item, open=True)
            
    def on_tree_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item: return
        self.tree.selection_set(item)
        
        menu = tk.Menu(self, tearoff=0, bg=Theme.SURFACE_2, fg="white", activebackground=Theme.ACCENT_PRIMARY)
        vals = self.tree.item(item)['values']
        text = self.tree.item(item)['text']
        
        if vals and vals[0]:
             menu.add_command(label="▶ Play", command=lambda: self.play_stream({'url':vals[0]}))
             menu.add_command(label="⭐ Add to Favorites", command=lambda: self.add_fav_channel(text, vals[0], vals[1]))
             menu.add_separator()
             menu.add_command(label="🧪 Test & Eliminate (If Broken)", command=lambda: self.test_and_eliminate_channel(vals[0], item, vals[1]))
             menu.add_command(label="🗑 Remove from List", command=lambda: self.manually_remove_channel(vals[0], item, vals[1]))
             menu.add_separator()
             menu.add_command(label=f"📌 Pin Country: {vals[1]}", command=lambda: self.add_fav_country(vals[1]))
        else:
             # Category
             country = text.split(" (")[0]
             menu.add_command(label=f"📌 Pin Country '{country}'", command=lambda: self.add_fav_country(country))
             menu.add_separator()
             menu.add_command(label=f"🧪 Test All Channels in '{country}'", command=lambda: self.run_category_test(country, item))
             
        menu.tk_popup(event.x_root, event.y_root)

    def manually_remove_channel(self, url, item_id, group):
        self.channel_manager.remove_channel(url, group)
        self.tree.delete(item_id)
        
    def test_and_eliminate_channel(self, url, item_id, group):
        self._set_status_ready("Testing stream availability...")
        
        def run_test():
            is_valid = self.channel_manager.verify_stream_url(url)
            self.after(0, lambda: self._handle_test_result(is_valid, url, item_id, group))
            
        threading.Thread(target=run_test, daemon=True).start()
        
    def _handle_test_result(self, is_valid, url, item_id, group):
        if is_valid:
            self.status_label.configure(text="✔ Stream is ONLINE", text_color=Theme.SUCCESS)
        else:
            self.status_label.configure(text="✖ Stream is DEAD - Removing...", text_color=Theme.ERROR)
            self.manually_remove_channel(url, item_id, group)
            
    def run_category_test(self, group, item_id):
        self.btn_db_status.configure(state="disabled")
        
        def on_prog(done, total):
            pct = (done/total)*100
            self.after(0, lambda: self.status_label.configure(text=f"Testing {group}: {done}/{total} ({pct:.0f}%)"))
            
        def run():
            self.channel_manager.verify_group(group, on_prog)
            self.after(0, lambda: self._on_cat_test_done(group, item_id))
            
        threading.Thread(target=run, daemon=True).start()
        
    def _on_cat_test_done(self, group, item_id):
        self.btn_db_status.configure(state="normal")
        self._set_status_ready(f"Verified {group}. Reloading view...")
        # Refresh tree or just that category (easier to refresh all or user must re-open)
        # Ideally, we should update the text count
        count = len(self.channel_manager.channels_by_category.get(group, []))
        self.tree.item(item_id, text=f"{group} ({count})")
        
        # Close and Reopen to refresh children
        if self.tree.item(item_id, "open"):
             self.tree.item(item_id, open=False)
             self.tree.item(item_id, open=True)
             pass

    # --- Favorites Logic ---
    def refresh_favorites_view(self):
        for w in self.fav_channels_frame.winfo_children(): w.destroy()
        for w in self.fav_countries_frame.winfo_children(): w.destroy()
        
        for ch in self.fav_manager.favorites["channels"]:
            f = ctk.CTkFrame(self.fav_channels_frame, height=50, fg_color=Theme.SURFACE_2, corner_radius=8)
            f.pack(fill="x", pady=4); f.pack_propagate(False)
            
            btn = ctk.CTkButton(f, text=f" {str(ch['name'])}", anchor="w", fg_color="transparent", 
                          text_color=Theme.TEXT_WHITE, font=("Segoe UI", 12), hover_color=Theme.SURFACE_3,
                          command=lambda u=ch['url']: self.play_stream({'url':u}))
            btn.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkButton(f, text="✕", width=30, fg_color="transparent", hover_color=Theme.ERROR, 
                          text_color=Theme.ERROR, command=lambda u=ch['url']: self.rem_fav_channel(u)).pack(side="right", padx=10)
            
        for co in self.fav_manager.favorites["countries"]:
            f = ctk.CTkFrame(self.fav_countries_frame, height=50, fg_color=Theme.SURFACE_2, corner_radius=8)
            f.pack(fill="x", pady=4); f.pack_propagate(False)
            
            btn = ctk.CTkButton(f, text=f"🌍 {co}", anchor="w", fg_color="transparent", 
                          text_color=Theme.TEXT_WHITE, font=("Segoe UI", 12), hover_color=Theme.SURFACE_3,
                          command=lambda c=co: self.open_country(c))
            btn.pack(side="left", fill="both", expand=True, padx=5)
            
             # Corrected removal to use correct lambda capture
            ctk.CTkButton(f, text="✕", width=30, fg_color="transparent", hover_color=Theme.ERROR,
                          text_color=Theme.ERROR, command=lambda c=co: self.rem_fav_country(c)).pack(side="right", padx=10)
            
    def add_fav_channel(self, name, url, group):
        self.fav_manager.add_channel({'name':name, 'url':url, 'group':group})
        self._set_status_ready(f"Added {name} to favorites")
        
    def add_fav_country(self, country):
        self.fav_manager.add_country(country)
        self._set_status_ready(f"Added {country} to favorites")
        
    def rem_fav_channel(self, url):
        self.fav_manager.remove_channel(url)
        self.refresh_favorites_view()
        
    def rem_fav_country(self, country):
        self.fav_manager.remove_country(country)
        self.refresh_favorites_view()
        
    def open_country(self, country):
        self.show_view("browser")
        self.entry_search.delete(0, "end")
        self.entry_search.insert(0, country)
        self.perform_search(None)

    def save_playlist(self):
        try:
             with open("saved_playlist.m3u", "w", encoding="utf-8") as f:
                 f.write("#EXTM3U\n")
                 for s in self.extractor.found_streams:
                     f.write(f"#EXTINF:-1,{s['url']}\n{s['url']}\n")
             self._set_status_ready("Playlist saved to folder!")
        except Exception as e:
            self.status_label.configure(text="Error saving playlist", text_color=Theme.ERROR)

    def cleanup_favorites_on_start(self):
        # Auto-test favorites on startup
        def _check():
             valid_count = 0
             removed_count = 0
             favs = self.fav_manager.favorites["channels"][:] # Copy list safely
             
             if not favs: return
             
             self.after(0, lambda: self.status_label.configure(text=f"Auto-Verifying {len(favs)} Favorites...", text_color=Theme.ACCENT_SECONDARY))
             
             for ch in favs:
                 # Use the robust check from channel manager
                 if self.channel_manager.verify_stream_url(ch['url']):
                     valid_count += 1
                 else:
                     self.fav_manager.remove_channel(ch['url'])
                     removed_count += 1
                     
             self.after(0, lambda: self._on_fav_check_complete(valid_count, removed_count))
             
        threading.Thread(target=_check, daemon=True).start()

    def _on_fav_check_complete(self, valid, removed):
        if removed > 0:
            msg = f"Cleaned Favorites: {valid} Online, {removed} Dead Removed."
            self.refresh_favorites_view() # Refresh UI if items removed
        else:
            msg = f"Favorites Verified: All {valid} Online."
            
        self._set_status_ready(msg)
