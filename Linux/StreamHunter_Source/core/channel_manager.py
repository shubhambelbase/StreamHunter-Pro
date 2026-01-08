import requests
import threading
import concurrent.futures

class ChannelManager:
    def __init__(self):
        self.channels_by_category = {}
        self.is_loading = False
        self.total_channels = 0
        self.verified_count = 0
        
        # Session for faster reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def fetch_channels(self, on_complete=None, on_progress=None):
        """
        Fetches channels in background (No Auto-Verify to save speed).
        """
        self.is_loading = True
        t = threading.Thread(target=self._fetch_worker, args=(on_complete, on_progress), daemon=True)
        t.start()
        
    def _fetch_worker(self, on_complete, on_progress):
        try:
            # 1. Fetch the raw list
            url = "https://iptv-org.github.io/iptv/index.country.m3u"
            if on_progress: on_progress(0, 0, "Downloading List...")
            
            r = self.session.get(url, timeout=15)
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

    def verify_stream_url(self, url):
        try:
            # Try HEAD first
            try:
                r = self.session.head(url, timeout=2.5, allow_redirects=True)
                if r.status_code < 400: return True
            except:
                pass
            
            # Try GET with context manager to auto-close
            try:
                with self.session.get(url, timeout=3.5, stream=True) as r:
                    if r.status_code < 400:
                        return True
            except:
                pass
        except:
            pass
        return False
        
    def remove_channel(self, url, group=None):
        # Remove from memory
        found = False
        # If group known, faster
        if group and group in self.channels_by_category:
             self.channels_by_category[group] = [c for c in self.channels_by_category[group] if c['url'] != url]
             return True
             
        # Else search all (slower)
        for g in self.channels_by_category:
            before = len(self.channels_by_category[g])
            self.channels_by_category[g] = [c for c in self.channels_by_category[g] if c['url'] != url]
            if len(self.channels_by_category[g]) < before:
                found = True
        return found
        
    def verify_group(self, group_name, callback=None):
        if group_name not in self.channels_by_category: return
        
        channels = self.channels_by_category[group_name]
        valid = []
        total = len(channels)
        
        def check(c):
            if self.verify_stream_url(c['url']):
                return c
            return None
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exc:
            futures = [exc.submit(check, c) for c in channels]
            done = 0
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res: valid.append(res)
                done += 1
                if callback: callback(done, total)
                
        self.channels_by_category[group_name] = valid

    def _parse_m3u(self, content):
        lines = content.split('\n')
        current_group = "Uncategorized"
        self.channels_by_category = {}
        self.current_title = "Unknown"
        
        for line in lines:
            line = line.strip()
            if not line: continue
                
            if line.startswith("#EXTINF"):
                info = line.split(",", 1)
                self.current_title = info[1] if len(info) > 1 else "Unknown"
                
                if 'group-title="' in line:
                    start = line.find('group-title="') + 13
                    end = line.find('"', start)
                    current_group = line[start:end]
                else:
                    current_group = "Others"
                    
            elif not line.startswith("#"):
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
                    res = ch.copy()
                    res['group'] = group
                    results.append(res)
        return results
