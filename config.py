import os
from typing import Optional

class Config:
    """Configuration class for the Telegram Bot API Middleware"""
    
    def __init__(self):
        # Telegram API credentials
        self.API_ID: int = 29657994
        self.API_HASH: str = "85f461c4f637911d79c65da1fc2bdd77"
        
        # Session string provided by user
        self.SESSION_STRING: str = os.getenv(
            "TELEGRAM_SESSION_STRING", 
            "BQHEi4oARVfNi9N8a0db-nzObercY1MEaLdUYzDl3YiRul8HdLhcNP3Du1wspXXMov5flQ30chjV-iO0IbNqh97FjiRnGWWbKgcvMwo7ycVsua5hzUlZ4a1MRzb5mmuvMK5QoYiNpRG-IGw1bpxHfIGIu09Z6g4cZMj194iLKb9QnHtlPw-jmO4iPOR1bNPsualcMfv8GwtjBFdaKUFFW7OYaGGOXAnKLs6C3umDEGqUrmgU2wsvpucGNYHvXHA3JYlS5BCQKqWahvBbco0WC2GWBIOZuiD4mzsNu4YBBGIlgnfqR4uLAtWcc4FpdDtjHMzY68XpKB2epecoeHnxpIbQQiDjogAAAAGtezAlAA"
        )
        
        # Bot username
        self.BOT_USERNAME: str = os.getenv("BOT_USERNAME", "@MYEYEINFO_bot")
        
        # API Configuration
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "5000"))
        
        # Timeouts and limits
        self.REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that all required configuration is present"""
        if self.API_ID == 0:
            raise ValueError("TELEGRAM_API_ID environment variable is required")
        
        if not self.API_HASH:
            raise ValueError("TELEGRAM_API_HASH environment variable is required")
        
        if not self.SESSION_STRING:
            raise ValueError("TELEGRAM_SESSION_STRING is required")
        
        if not self.BOT_USERNAME:
            raise ValueError("BOT_USERNAME is required")

    def get_telegram_config(self) -> dict:
        """Get Telegram client configuration"""
        return {
            "api_id": self.API_ID,
            "api_hash": self.API_HASH,
            "session_string": self.SESSION_STRING
        }

    def get_api_config(self) -> dict:
        """Get API server configuration"""
        return {
            "host": self.HOST,
            "port": self.PORT,
            "timeout": self.REQUEST_TIMEOUT
        }
