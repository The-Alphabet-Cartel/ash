"""
Configuration Manager - Centralized config handling
Copy this to: ash/bot/core/config_manager.py
"""

import os
import logging
from typing import List

logger = logging.getLogger(__name__)

class ConfigManager:
    """Centralized configuration management with validation"""
    
    def __init__(self):
        self._config = {}
        self._load_and_validate_config()
    
    def _load_and_validate_config(self):
        """Load and validate all configuration"""
        logger.info("📋 Loading and validating configuration...")
        
        # Required configurations
        required_configs = {
            'DISCORD_TOKEN': 'Discord bot token',
            'GUILD_ID': 'Discord server ID',
            'CLAUDE_API_KEY': 'Claude API key',
            'RESOURCES_CHANNEL_ID': 'Resources channel ID',
            'CRISIS_RESPONSE_CHANNEL_ID': 'Crisis response channel ID',
            'CRISIS_RESPONSE_ROLE_ID': 'Crisis response role ID',
            'STAFF_PING_USER': 'Staff user ID for pings'
        }
        
        # Load required configs
        missing_configs = []
        for key, description in required_configs.items():
            value = os.getenv(key)
            if not value:
                missing_configs.append(f"{key} ({description})")
            else:
                self._config[key] = value
        
        if missing_configs:
            raise ValueError(f"Missing required configuration: {', '.join(missing_configs)}")
        
        # Load optional configs with defaults
        optional_configs = {
            'ALLOWED_CHANNELS': '',
            'RESOURCES_CHANNEL_NAME': 'resources',
            'CRISIS_RESPONSE_ROLE_NAME': 'CrisisResponse',
            'STAFF_PING_NAME': 'Staff',
            'NLP_SERVICE_HOST': '192.168.1.100',
            'NLP_SERVICE_PORT': '8881',
            'LOG_LEVEL': 'INFO',
            'MAX_DAILY_CALLS': '1000',
            'RATE_LIMIT_PER_USER': '10',
            'ENABLE_KEYWORD_DISCOVERY': 'true',
            'DISCOVERY_MIN_CONFIDENCE': '0.6',
            'MAX_DAILY_DISCOVERIES': '10',
            'DISCOVERY_INTERVAL_HOURS': '24'
        }
        
        for key, default in optional_configs.items():
            self._config[key] = os.getenv(key, default)
        
        # Parse special configurations
        self._parse_special_configs()
        
        # Log configuration summary
        self._log_config_summary()
    
    def _parse_special_configs(self):
        """Parse configurations that need special handling"""
        
        # Parse allowed channels
        allowed_channels_str = self._config['ALLOWED_CHANNELS']
        if allowed_channels_str:
            try:
                self._config['ALLOWED_CHANNELS_LIST'] = [
                    int(ch.strip()) for ch in allowed_channels_str.split(',') 
                    if ch.strip()
                ]
            except ValueError as e:
                logger.warning(f"Invalid ALLOWED_CHANNELS format: {e}")
                self._config['ALLOWED_CHANNELS_LIST'] = []
        else:
            self._config['ALLOWED_CHANNELS_LIST'] = []
        
        # Parse integer configs
        int_configs = [
            'GUILD_ID', 'RESOURCES_CHANNEL_ID', 'CRISIS_RESPONSE_CHANNEL_ID',
            'CRISIS_RESPONSE_ROLE_ID', 'STAFF_PING_USER', 'NLP_SERVICE_PORT',
            'MAX_DAILY_CALLS', 'RATE_LIMIT_PER_USER', 'MAX_DAILY_DISCOVERIES',
            'DISCOVERY_INTERVAL_HOURS'
        ]
        
        for key in int_configs:
            try:
                self._config[key] = int(self._config[key])
            except ValueError:
                raise ValueError(f"Invalid integer value for {key}: {self._config[key]}")
        
        # Parse float configs
        float_configs = ['DISCOVERY_MIN_CONFIDENCE']
        for key in float_configs:
            try:
                self._config[key] = float(self._config[key])
            except ValueError:
                raise ValueError(f"Invalid float value for {key}: {self._config[key]}")
        
        # Parse boolean configs
        bool_configs = ['ENABLE_KEYWORD_DISCOVERY']
        for key in bool_configs:
            self._config[key] = self._config[key].lower() in ['true', '1', 'yes', 'on']
    
    def _log_config_summary(self):
        """Log a summary of loaded configuration"""
        logger.info("✅ Configuration loaded successfully:")
        logger.info(f"   Guild ID: {self._config['GUILD_ID']}")
        logger.info(f"   Allowed channels: {len(self._config['ALLOWED_CHANNELS_LIST'])}")
        logger.info(f"   NLP service: {self._config['NLP_SERVICE_HOST']}:{self._config['NLP_SERVICE_PORT']}")
        logger.info(f"   Discovery enabled: {self._config['ENABLE_KEYWORD_DISCOVERY']}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = self._config.get(key, default)
        return int(value) if value is not None else default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        value = self._config.get(key, default)
        return float(value) if value is not None else default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = self._config.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ['true', '1', 'yes', 'on']
    
    def get_allowed_channels(self) -> List[int]:
        """Get list of allowed channel IDs"""
        return self._config.get('ALLOWED_CHANNELS_LIST', [])
    
    def is_channel_allowed(self, channel_id: int) -> bool:
        """Check if channel is in allowed list (empty list = all allowed)"""
        allowed = self.get_allowed_channels()
        return len(allowed) == 0 or channel_id in allowed
    
    def get_nlp_url(self) -> str:
        """Get NLP service URL"""
        host = self.get('NLP_SERVICE_HOST')
        port = self.get_int('NLP_SERVICE_PORT')
        return f"http://{host}:{port}"