import os
import json
from typing import Optional

class Config:
    def __init__(self):
        self.api_base = os.getenv("API_BASE", "https://api.bugbounty.com")
        self.username = os.getenv("USERNAME", "")
        self.password = os.getenv("PASSWORD", "")
        
    def load_from_file(self, filename: str = "config.json") -> None:
        """Load configuration from JSON file."""
        try:
            with open(filename) as f:
                data = json.load(f)
                self.__dict__.update(data)
        except FileNotFoundError:
            pass
            
    def save_to_file(self, filename: str = "config.json") -> None:
        """Save configuration to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.__dict__, f, indent=4)
