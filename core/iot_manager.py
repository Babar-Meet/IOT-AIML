import time
import requests
import threading

class IOTManager:
    def __init__(self, debounce_duration=1.0):
        self.debounce_duration = debounce_duration
        
        self.current_count = -1
        self.count_start_time = 0
        self.last_triggered_count = -1

    def update_count(self, count, mode, endpoints):
        """
        Continuously called for every frame with the current finger count.
        Returns the triggered count if a trigger just happened, else None.
        """
        current_time = time.time()

        # If count changed, reset the timer
        if count != self.current_count:
            self.current_count = count
            self.count_start_time = current_time
            return None

        # Check if held long enough and hasn't been triggered yet
        if (current_time - self.count_start_time) >= self.debounce_duration:
            if self.current_count != self.last_triggered_count:
                self.last_triggered_count = self.current_count
                
                if mode == "Counting":
                    print(f"[Counting] Locked in: {self.current_count} fingers (No API call)")
                    return self.current_count
                
                # If we officially lock in a valid finger count > 0 in IOT mode, fire it
                if mode == "IOT" and self.current_count > 0:
                    api_url = endpoints.get(str(self.current_count))
                    if api_url:
                        self._trigger_api(api_url, self.current_count)
                        return self.current_count
                    else:
                        print(f"[IOT] No endpoint configured for {self.current_count} fingers.")
        return None

    def _trigger_api(self, url, count):
        def worker():
            print(f"[IOT] Firing trigger for {count} fingers: GET {url}")
            try:
                # Add a timeout so it doesn't hang threads forever
                resp = requests.get(url, timeout=3.0)
                print(f"[IOT] Response [{resp.status_code}]: {resp.text[:50]}")
            except Exception as e:
                print(f"[IOT] Error triggering {url}: {e}")
        
        # Fire and forget
        t = threading.Thread(target=worker, daemon=True)
        t.start()
