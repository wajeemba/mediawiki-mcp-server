"""
Configuration management for Feruchemist MCP Server
Supports development and production environments
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration class supporting multiple environments"""
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv("FERUCHEMIST_ENV", "development")
        self.base_url = "https://coppermind.net/w/"
        self.path_prefix = "api.php"
        
        # Environment-specific settings
        if self.environment == "production":
            self.cards_dir = Path.home() / ".cosmere_dm" / "cards"
            self.log_level = "INFO"
            self.cache_ttl = 3600  # 1 hour
        else:  # development
            self.cards_dir = Path.home() / ".cosmere_dm" / "cards_dev"
            self.log_level = "DEBUG"
            self.cache_ttl = 300   # 5 minutes
        
        # Ensure cards directory exists
        self.cards_dir.mkdir(parents=True, exist_ok=True)
        
        # Environment variable overrides
        self.cards_dir = Path(os.getenv("FERUCHEMIST_CARDS_DIR", str(self.cards_dir)))
        self.log_level = os.getenv("FERUCHEMIST_LOG_LEVEL", self.log_level)
        
    def get_card_path(self, card_type: str, card_id: str) -> Path:
        """Get the full path for a card file"""
        return self.cards_dir / card_type / f"{card_id}.json"
        
    def get_type_dir(self, card_type: str) -> Path:
        """Get the directory for a card type"""
        type_dir = self.cards_dir / card_type
        type_dir.mkdir(parents=True, exist_ok=True)
        return type_dir
        
    def __repr__(self):
 