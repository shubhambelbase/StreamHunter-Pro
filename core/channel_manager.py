import requests
import threading

class ChannelManager:
    def __init__(self):
        # We will fetch a subset or a curated list. 
        # Using iptv-org/iptv main list which is huge might be slow, but let's try a country-specific consolidated one if possible.
        # However, user wants "organized as country language".
        # We will fetch the main index for categories or countries.
        self.channels_by_category = {}
        self.is_loading = False
        
    def fetch_channels(self, on_complete=None):
        """
        Fetches channels in a background thread.
        """
        self.is_loading = True
        t = threading.Thread(target=self._fetch_worker, args=(on_complete,), daemon=True)
        t.start()
        
    def _fetch_worker(self, on_complete):
        try:
            # We'll use a grouped list from iptv-org
            # 'https://iptv-org.github.io/iptv/index.country.m3u' organizes by country tags
            url = "https://iptv-org.github.io/iptv/index.country.m3u"
            print(f"Fetching channels from {url}...")
            r = requests.get(url, timeout=15)
            
            if r.status_code == 200:
                self._parse_m3u(r.text)
            else:
                print("Failed to fetch channels")
                
        except Exception as e:
            print(f"Error fetching channels: {e}")
        finally:
            self.is_loading = False
            if on_complete:
                on_complete()

    def _parse_m3u(self, content):
        lines = content.split('\n')
        current_group = "Uncategorized"
        
        # Structure: { 'Group Name': [ {'name': 'Chan 1', 'url': '...'}, ... ] }
        self.channels_by_category = {}
        
        for line in lines:
            line = line.strip()
            if not line: 
                continue
                
            if line.startswith("#EXTINF"):
                # Parse Group/Title
                # Example: #EXTINF:-1 group-title="Afghanistan",RTA Planet
                # Simple parsing strategies
                info = line.split(",", 1)
                title = info[1] if len(info) > 1 else "Unknown"
                
                # Extract group-title
                if 'group-title="' in line:
                    start = line.find('group-title="') + 13
                    end = line.find('"', start)
                    current_group = line[start:end]
                else:
                    current_group = "Others"
                    
                self.current_title = title
                
            elif not line.startswith("#"):
                # URL
                url = line
                if current_group not in self.channels_by_category:
                    self.channels_by_category[current_group] = []
                    
                self.channels_by_category[current_group].append({
                    'name': self.current_title,
                    'url': url
                })

    def search_channels(self, query):
        results = []
        query = query.lower()
        for group, channels in self.channels_by_category.items():
            for ch in channels:
                if query in ch['name'].lower() or query in group.lower():
                    # Add group info to result
                    res = ch.copy()
                    res['group'] = group
                    results.append(res)
        return results
