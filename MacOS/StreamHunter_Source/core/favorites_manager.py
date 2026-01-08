import json
import os

class FavoritesManager:
    def __init__(self, filename="favorites.json"):
        self.filename = filename
        self.favorites = self.load_favorites()
        
    def load_favorites(self):
        if not os.path.exists(self.filename):
            return {"channels": [], "countries": []}
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"channels": [], "countries": []}
            
    def save_favorites(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=4)
        except Exception as e:
            print(f"Error saving favorites: {e}")

    def add_channel(self, channel_info):
        # channel_info: {name, url, group}
        # Check if exists
        for ch in self.favorites["channels"]:
            if ch['url'] == channel_info['url']:
                return # Already exists
        self.favorites["channels"].append(channel_info)
        self.save_favorites()

    def remove_channel(self, url):
        self.favorites["channels"] = [c for c in self.favorites["channels"] if c['url'] != url]
        self.save_favorites()
        
    def add_country(self, country_name):
        if country_name not in self.favorites["countries"]:
            self.favorites["countries"].append(country_name)
            self.save_favorites()
            
    def remove_country(self, country_name):
        if country_name in self.favorites["countries"]:
            self.favorites["countries"].remove(country_name)
            self.save_favorites()

    def is_channel_fav(self, url):
        return any(c['url'] == url for c in self.favorites["channels"])
        
    def is_country_fav(self, name):
        return name in self.favorites["countries"]
