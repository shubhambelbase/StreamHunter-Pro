import threading
from playwright.sync_api import sync_playwright
import time

class StreamExtractor:
    def __init__(self):
        self.found_streams = []
        self._stop_event = threading.Event()
        self._is_running = False

    def extract(self, url, on_stream_found_callback=None, on_finish_callback=None):
        """
        Extracts m3u8 streams from the URL in a separate thread.
        on_stream_found_callback: function(stream_url)
        on_finish_callback: function() called when extraction loop finishes
        """
        if self._is_running:
            return
            
        self.found_streams = []
        self._stop_event.clear()
        self._is_running = True
        
        def run():
            try:
                with sync_playwright() as p:
                    # Launch with some args to bypass simple bot detection
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
                        ]
                    )
                    
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                        viewport={'width': 1280, 'height': 720}
                    )
                    
                    page = context.new_page()
                    
                    def handle_request(request):
                        try:
                            url = request.url
                            # Check for m3u8 extension or content type
                            # Added .m3u support
                            is_stream = False
                            if ".m3u8" in url or ".m3u" in url:
                                is_stream = True
                            elif "application/vnd.apple.mpegurl" in request.headers.get("content-type", ""):
                                is_stream = True
                            elif "audio/mpegurl" in request.headers.get("content-type", ""):
                                is_stream = True

                            if is_stream:
                                # Avoid duplicates (check by URL only)
                                if not any(s['url'] == url for s in self.found_streams):
                                    headers = request.all_headers()
                                    
                                    # Only send headers if they look 'real' or non-standard. 
                                    # Some m3u links fail if we pass the bot-like Playwright UA.
                                    ua = headers.get('user-agent', '')
                                    ref = headers.get('referer', '')
                                    
                                    stream_info = {
                                        'url': url,
                                        'user_agent': ua,
                                        'referer': ref
                                    }
                                    
                                    self.found_streams.append(stream_info)
                                    if on_stream_found_callback:
                                        on_stream_found_callback(stream_info)
                        except Exception as e:
                            print(f"Error handling request: {e}")

                    page.on("request", handle_request)
                    
                    try:
                        print(f"Navigating to {url}...")
                        page.goto(url, timeout=30000, wait_until="domcontentloaded")
                        
                        # Simulate some user interaction
                        page.mouse.move(100, 100)
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                        
                        # Wait loop
                        for _ in range(15): # Monitor for 15 seconds
                            if self._stop_event.is_set():
                                break
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"Extraction error: {e}")
                    finally:
                        try:
                            browser.close()
                        except:
                            pass
            except Exception as e:
                print(f"Playwright error: {e}")
            finally:
                self._is_running = False
                if on_finish_callback:
                    on_finish_callback()

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def stop(self):
        self._stop_event.set()
