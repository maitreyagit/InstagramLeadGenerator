import random
import os
from typing import Optional

class ProxyManager:
    def __init__(self, proxy_file: Optional[str] = None):
        self.proxies = []
        if proxy_file and os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
                
    def get_random_proxy(self) -> Optional[str]:
        """Returns a random proxy from the list, or None if no proxies loaded."""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
        
    def get_proxy_server_format(self) -> Optional[dict]:
        """Returns proxy in a format suitable for Playwright (server, username, password)"""
        proxy = self.get_random_proxy()
        if not proxy:
            return None
            
        # Basic parsing assuming format: http://user:pass@ip:port or http://ip:port
        # Playwright format: {'server': 'http://ip:port', 'username': 'user', 'password': 'pw'}
        
        # Simplified parsing for example purposes
        if '@' in proxy:
            try:
                protocol_parts = proxy.split('://')
                protocol = protocol_parts[0]
                rest = protocol_parts[1]
                auth, server = rest.split('@')
                user, pwd = auth.split(':')
                return {
                    "server": f"{protocol}://{server}",
                    "username": user,
                    "password": pwd
                }
            except Exception:
                return {"server": proxy}
        else:
            return {"server": proxy}
