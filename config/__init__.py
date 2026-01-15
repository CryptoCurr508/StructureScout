"""
StructureScout Trading Bot - Configuration Loader

Loads configuration from config.yaml and environment variables from .env file.
Provides centralized access to all configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for StructureScout trading bot."""
    
    def __init__(self, config_path: Optional[str] = None, env_path: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to config.yaml file (default: config/config.yaml)
            env_path: Path to .env file (default: .env in project root)
        """
        self.project_root = Path(__file__).parent.parent
        
        # Load environment variables from .env file
        if env_path is None:
            env_path = self.project_root / ".env"
        load_dotenv(env_path)
        
        # Load YAML configuration
        if config_path is None:
            config_path = self.project_root / "config" / "config.yaml"
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    # MetaTrader5 credentials from .env
    @property
    def mt5_login(self) -> str:
        """MT5 account login number."""
        return os.getenv('MT5_LOGIN', '')
    
    @property
    def mt5_password(self) -> str:
        """MT5 account password."""
        return os.getenv('MT5_PASSWORD', '')
    
    @property
    def mt5_server(self) -> str:
        """MT5 broker server."""
        return os.getenv('MT5_SERVER', '')
    
    @property
    def mt5_path(self) -> str:
        """MT5 installation path."""
        return os.getenv('MT5_PATH', '')
    
    # OpenAI API credentials from .env
    @property
    def openai_api_key(self) -> str:
        """OpenAI API key."""
        return os.getenv('OPENAI_API_KEY', '')
    
    # Telegram credentials from .env
    @property
    def telegram_bot_token(self) -> str:
        """Telegram bot token."""
        return os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    @property
    def telegram_chat_id(self) -> str:
        """Telegram chat ID."""
        return os.getenv('TELEGRAM_CHAT_ID', '')
    
    # System configuration from config.yaml
    @property
    def current_mode(self) -> str:
        """Current trading mode (observation, paper_trading, micro_live, full_live)."""
        return self.config['system']['current_mode']
    
    @property
    def enable_live_trading(self) -> bool:
        """Master switch for live trading."""
        return self.config['system'].get('enable_live_trading', False)
    
    @property
    def require_manual_confirmation(self) -> bool:
        """Require manual confirmation for trades."""
        return self.config['system'].get('require_manual_confirmation', True)
    
    @property
    def trading_enabled(self) -> bool:
        """Additional safety layer for trading."""
        return self.config['system'].get('trading_enabled', False)
    
    @property
    def is_live_trading_allowed(self) -> bool:
        """Check if live trading is fully enabled."""
        return (self.enable_live_trading and 
                self.trading_enabled and 
                self.current_mode in ['micro_live', 'full_live'])
    
    @property
    def timezone(self) -> str:
        """Trading timezone."""
        return self.config['trading_hours']['timezone']
    
    @property
    def trading_start_time(self) -> str:
        """Market open time."""
        return self.config['trading_hours']['start_time']
    
    @property
    def trading_end_time(self) -> str:
        """Market close time."""
        return self.config['trading_hours']['end_time']
    
    @property
    def scan_schedule(self) -> list:
        """List of scan times during trading day."""
        return self.config['trading_hours']['scan_schedule']
    
    @property
    def trading_symbol(self) -> str:
        """Trading symbol (e.g., NAS100 or #NAS100_Mar)."""
        return self.config['trading']['symbol']
    
    # Allow dynamic update of trading symbol
    @trading_symbol.setter
    def trading_symbol(self, value: str):
        """Set trading symbol dynamically."""
        self.config['trading']['symbol'] = value
    
    @property
    def symbol_base(self) -> str:
        """Base symbol name for matching (e.g., NAS100)."""
        return self.config['trading'].get('symbol_base', 'NAS100')
    
    @property
    def auto_detect_symbol(self) -> bool:
        """Whether to auto-detect broker symbol format."""
        return self.config['trading'].get('auto_detect_symbol', True)
    
    @property
    def trading_timeframe(self) -> str:
        """Chart timeframe (e.g., M5)."""
        return self.config['trading']['timeframe']
    
    @property
    def risk_per_trade(self) -> float:
        """Risk percentage per trade."""
        return self.config['risk_management']['risk_per_trade']
    
    @property
    def daily_loss_limit(self) -> float:
        """Daily loss limit as percentage."""
        return self.config['risk_management']['daily_loss_limit']
    
    @property
    def weekly_loss_limit(self) -> float:
        """Weekly loss limit as percentage."""
        return self.config['risk_management']['weekly_loss_limit']
    
    @property
    def max_trades_per_day(self) -> int:
        """Maximum trades allowed per day."""
        return self.config['risk_management']['max_trades_per_day']
    
    @property
    def openai_model(self) -> str:
        """OpenAI model name."""
        return self.config['openai']['model']
    
    @property
    def openai_max_tokens(self) -> int:
        """OpenAI max tokens."""
        return self.config['openai']['max_tokens']
    
    @property
    def openai_temperature(self) -> float:
        """OpenAI temperature setting."""
        return self.config['openai']['temperature']
    
    @property
    def min_reward_risk_ratio(self) -> float:
        """Minimum reward:risk ratio for valid setups."""
        return self.config['setup_filters']['min_reward_risk_ratio']
    
    @property
    def min_confidence_score(self) -> int:
        """Minimum AI confidence score for valid setups."""
        return self.config['setup_filters']['min_confidence_score']
    
    @property
    def trading_log_path(self) -> Path:
        """Path to trading log CSV file."""
        return self.project_root / self.config['storage']['trading_log']
    
    @property
    def screenshot_folder(self) -> Path:
        """Path to screenshots folder."""
        return self.project_root / self.config['storage']['screenshot_folder']
    
    @property
    def error_log_path(self) -> Path:
        """Path to error log file."""
        return self.project_root / self.config['storage']['error_log']
    
    @property
    def system_log_path(self) -> Path:
        """Path to system log file."""
        return self.project_root / self.config['storage']['system_log']
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key path.
        
        Args:
            key_path: Dot-notation path (e.g., 'system.current_mode')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            config.get('trading_hours.start_time')  # Returns '09:30'
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def validate_credentials(self) -> Dict[str, bool]:
        """
        Validate that all required credentials are present.
        
        Returns:
            Dictionary with validation status for each credential set
        """
        validation = {
            'mt5': all([
                self.mt5_login,
                self.mt5_password,
                self.mt5_server,
                self.mt5_path
            ]),
            'openai': bool(self.openai_api_key),
            'telegram': all([
                self.telegram_bot_token,
                self.telegram_chat_id
            ])
        }
        
        return validation
    
    def get_missing_credentials(self) -> list:
        """
        Get list of missing credential sets.
        
        Returns:
            List of credential set names that are incomplete
        """
        validation = self.validate_credentials()
        return [name for name, valid in validation.items() if not valid]


# Global config instance (loaded on import)
_config_instance = None


def get_config() -> Config:
    """
    Get global configuration instance (singleton pattern).
    
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


# Convenience function for direct access
def load_config(config_path: Optional[str] = None, env_path: Optional[str] = None) -> Config:
    """
    Load configuration from files.
    
    Args:
        config_path: Path to config.yaml file
        env_path: Path to .env file
        
    Returns:
        Config instance
    """
    return Config(config_path=config_path, env_path=env_path)
