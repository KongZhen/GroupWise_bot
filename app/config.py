"""Configuration management."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Bot configuration."""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # MiniMax API
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_GROUP_ID: str = os.getenv("MINIMAX_GROUP_ID", "")
    MINIMAX_BASE_URL: str = "https://api.minimax.chat/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "bot.db")
    
    # Admin
    ADMIN_USER_ID: Optional[int] = None
    
    # Webhook (Railway)
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    
    def __post_init__(self):
        """Validate required config."""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.MINIMAX_API_KEY:
            raise ValueError("MINIMAX_API_KEY is required")
        # MINIMAX_GROUP_ID is optional - used for MiniMax group API (not required for basic bot)
        
        if admin_id := os.getenv("ADMIN_USER_ID"):
            self.ADMIN_USER_ID = int(admin_id)


config = Config()
