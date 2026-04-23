import json
import os

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.mode = "Counting"
        self.iot_endpoints = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.save_default()
        
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.mode = data.get("mode", "Counting")
                self.iot_endpoints = data.get("iot_endpoints", {})
            print(f"[Config] Loaded config from {self.config_path} | Mode: {self.mode}")
        except Exception as e:
            print(f"[Config] Error loading config: {e}")

    def save_default(self):
        default_data = {
            "mode": "Counting",
            "iot_endpoints": {
                "1": "http://192.168.1.100/light/1/on",
                "2": "http://192.168.1.100/light/2/on",
                "3": "http://192.168.1.100/light/3/on",
                "4": "http://192.168.1.100/light/4/on",
                "5": "http://192.168.1.100/light/5/on"
            }
        }
        try:
            with open(self.config_path, "w") as f:
                json.dump(default_data, f, indent=4)
            print(f"[Config] Default config created at {self.config_path}")
        except Exception as e:
            print(f"[Config] Error creating default: {e}")

    def reload(self, new_path=None):
        if new_path:
            self.config_path = new_path
        self.load_config()

