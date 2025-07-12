"""
Configuration management for Feruchemist MCP Server
"""
import os
from pathlib import Path


class Config:
    """Simple configuration class"""
    
    def __init__(self):
        self.base_url = "https://coppermind.net/w/"
        self.path_prefix = "api.php"
        
        # Cards storage - single shared location
        self.cards_dir = Path.home() / ".cosmere_dm" / "cards"
        self.cards_dir.mkdir(parents=True, exist_ok=True)
        
    def get_card_path(self, card_type: str, card_id: str) -> Path:
        """Get the full path for a card file"""
        return self.cards_dir / card_type / f"{card_id}.json"
        
    def get_type_dir(self, card_type: str) -> Path:
        """Get the directory for a card type"""
        type_dir = self.cards_dir / card_type
        type_dir.mkdir(parents=True, exist_ok=True)
        return type_dir
        
    def __repr__(self):
        return f"Config(base_url='{self.base_url}', cards_dir='{self.cards_dir}')"
 