import requests
import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet

class EnhancedBugBountyClient:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._init_encryption()
        
    def _init_encryption(self):
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            os.environ['ENCRYPTION_KEY'] = key.decode()
        self.cipher_suite = Fernet(key)
        
    def encrypt(self, data: str) -> str:
        return self.cipher_suite.encrypt(data.encode()).decode()
        
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
        
    def get_token(self) -> str:
        # Enhanced token management
        if not hasattr(self, '_token') or self._token_expiry < datetime.now():
            self._refresh_token()
        return self._token
        
    def _refresh_token(self):
        auth_url = f"{self.config.api_base}/auth"
        response = requests.post(
            auth_url,
            json={"username": self.config.username, "password": self.config.password}
        )
        response.raise_for_status()
        
        data = response.json()
        self._token = data["access_token"]
        self._token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])
        
    def search(self, query: str, sort: str = "default") -> Dict:
        search_url = f"{self.config.api_base}/search"
        params = {"q": query, "sort": sort}
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        return response.json()
        
    def analyze_code(self, code: str) -> Dict:
        # Basic code analysis
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.md5(code.encode()).hexdigest(),
            "lines": len(code.split('\n')),
            "complexity": self._calculate_complexity(code)
        }
        return analysis
        
    def _calculate_complexity(self, code: str) -> float:
        # Simple complexity calculation
        lines = code.split('\n')
        complexity = 0
        for line in lines:
            if any(keyword in line for keyword in ['if', 'for', 'while', 'try']):
                complexity += 1
        return complexity / len(lines) if lines else 0
