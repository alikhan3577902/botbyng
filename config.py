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
            "BQC_XyrnKFtrbfnZeceyJkttqcoh0_qBLoJ6qMsp2Uz4U4n6zH4hchmdGCZmiAtf4UuLH-vVhGlIrOo0487LR0bQKQAqG-NmBol4CH11LjltDKeBOiEylYp_S3mFEBmOV3oND1_vAYkF6dxO1MSxkYQcn6zY-yyYr8OCW9jV55teGLEVv5Kw4xxsp4zfIt7p5OmmMT2uLnWaQ4d_XnO3t3l2W4imCiJk_ovxxe_TYv4TjbaUBoQPCosQWdE9sf39U1pAoBkIPGPhJIoNdchcwUzDfQmzzc14x_-CFRa-XgXR0Eh2hr-kt6hdTaKuOnNuy5Y_gZWwkJ0zrTdzQrUH0BgSAAAAAa17MCUA"
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
