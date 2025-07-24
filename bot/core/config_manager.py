"""
Enhanced Configuration Manager with Better Validation
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ConfigValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigManager:
    """Enhanced configuration management with comprehensive validation"""
    
    def __init__(self, env_file: Optional[str] = None):
        self._config = {}
        self._validation_result = None
        self._load_environment(env_file)
        self._load_and_validate_config()
    
    def _load_environment(self, env_file: Optional[str] = None):
        """Load environment file if specified"""
        if env_file and Path(env_file).exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                logger.info(f"📁 Loaded environment from {env_file}")
            except ImportError:
                logger.warning("python-dotenv not available, using system environment only")
    
    def _load_and_validate_config(self) -> ConfigValidationResult:
        """Load and comprehensively validate all configuration"""
        logger.info("📋 Loading and validating configuration...")
        
        errors = []
        warnings = []
        
        # Define configuration schema
        config_schema = {
            # Required Discord configurations
            'DISCORD_TOKEN': {
                'required': True,
                'type': str,
                'description': 'Discord bot token',
                'validator': self._validate_discord_token
            },
            'GUILD_ID': {
                'required': True,
                'type': int,
                'description': 'Discord server ID',
                'validator': self._validate_snowflake
            },
            
            # Required Claude API
            'CLAUDE_API_KEY': {
                'required': True,
                'type': str,
                'description': 'Claude API key',
                'validator': self._validate_claude_key
            },
            'CLAUDE_MODEL': {
                'required': False,
                'type': str,
                'default': 'claude-sonnet-4-20250514',
                'description': 'Claude model to use'
            },
            
            # Required Discord channels/roles
            'RESOURCES_CHANNEL_ID': {
                'required': True,
                'type': int,
                'description': 'Resources channel ID',
                'validator': self._validate_snowflake
            },
            'CRISIS_RESPONSE_CHANNEL_ID': {
                'required': True,
                'type': int,
                'description': 'Crisis response channel ID',
                'validator': self._validate_snowflake
            },
            'CRISIS_RESPONSE_ROLE_ID': {
                'required': True,
                'type': int,
                'description': 'Crisis response role ID',
                'validator': self._validate_snowflake
            },
            'STAFF_PING_USER': {
                'required': True,
                'type': int,
                'description': 'Staff user ID for pings',
                'validator': self._validate_snowflake
            },
            
            # Optional configurations with defaults
            'ALLOWED_CHANNELS': {
                'required': False,
                'type': str,
                'default': '',
                'description': 'Comma-separated channel IDs'
            },
            'RESOURCES_CHANNEL_NAME': {
                'required': False,
                'type': str,
                'default': 'resources',
                'description': 'Display name for resources channel'
            },
            'CRISIS_RESPONSE_ROLE_NAME': {
                'required': False,
                'type': str,
                'default': 'CrisisResponse',
                'description': 'Display name for crisis role'
            },
            'STAFF_PING_NAME': {
                'required': False,
                'type': str,
                'default': 'Staff',
                'description': 'Display name for staff'
            },
            
            # NLP Service configuration
            'NLP_SERVICE_HOST': {
                'required': False,
                'type': str,
                'default': '10.20.30.16',
                'description': 'NLP service host IP',
                'validator': self._validate_ip_address
            },
            'NLP_SERVICE_PORT': {
                'required': False,
                'type': int,
                'default': 8881,
                'description': 'NLP service port',
                'validator': self._validate_port
            },
            
            # Rate limiting and performance
            'LOG_LEVEL': {
                'required': False,
                'type': str,
                'default': 'INFO',
                'description': 'Logging level',
                'validator': self._validate_log_level
            },
            'MAX_DAILY_CALLS': {
                'required': False,
                'type': int,
                'default': 1000,
                'description': 'Max daily API calls',
                'validator': lambda x: x > 0
            },
            'RATE_LIMIT_PER_USER': {
                'required': False,
                'type': int,
                'default': 10,
                'description': 'Rate limit per user per hour',
                'validator': lambda x: 0 < x <= 100
            },
            
            # Discovery system (optional)
            'ENABLE_KEYWORD_DISCOVERY': {
                'required': False,
                'type': bool,
                'default': True,
                'description': 'Enable keyword discovery system'
            },
            'DISCOVERY_MIN_CONFIDENCE': {
                'required': False,
                'type': float,
                'default': 0.6,
                'description': 'Minimum confidence for keyword discovery',
                'validator': lambda x: 0.0 <= x <= 1.0
            },
            'MAX_DAILY_DISCOVERIES': {
                'required': False,
                'type': int,
                'default': 10,
                'description': 'Max daily keyword discoveries',
                'validator': lambda x: x > 0
            }
        }
        
        # Validate each configuration item
        for key, schema in config_schema.items():
            try:
                value = self._get_and_validate_config_item(key, schema, errors, warnings)
                if value is not None:
                    self._config[key] = value
            except Exception as e:
                errors.append(f"Error processing {key}: {str(e)}")
        
        # Parse composite configurations
        self._parse_special_configs()
        
        # Validate configuration relationships
        self._validate_config_relationships(errors, warnings)
        
        # Store validation result
        self._validation_result = ConfigValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
        # Log results
        self._log_config_summary(errors, warnings)
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return self._validation_result
    
    def _get_and_validate_config_item(self, key: str, schema: Dict[str, Any], 
                                     errors: List[str], warnings: List[str]) -> Any:
        """Get and validate a single configuration item"""
        
        raw_value = os.getenv(key)
        
        # Handle missing required values
        if schema.get('required', False) and not raw_value:
            errors.append(f"Missing required configuration: {key} ({schema['description']})")
            return None
        
        # Use default if value is missing
        if not raw_value and 'default' in schema:
            raw_value = str(schema['default'])
        
        if not raw_value:
            return None
        
        # Type conversion
        try:
            if schema['type'] == int:
                value = int(raw_value)
            elif schema['type'] == float:
                value = float(raw_value)
            elif schema['type'] == bool:
                value = raw_value.lower() in ['true', '1', 'yes', 'on']
            else:
                value = raw_value
        except ValueError:
            errors.append(f"Invalid {schema['type'].__name__} value for {key}: {raw_value}")
            return None
        
        # Custom validation
        validator = schema.get('validator')
        if validator and not validator(value):
            errors.append(f"Validation failed for {key}: {value}")
            return None
        
        return value
    
    def _validate_discord_token(self, token: str) -> bool:
        """Validate Discord token format"""
        if not token or len(token) < 50:
            return False
        # Basic format check for Discord bot tokens
        parts = token.split('.')
        return len(parts) >= 2 and len(parts[0]) > 10
    
    def _validate_claude_key(self, key: str) -> bool:
        """Validate Claude API key format"""
        return key.startswith('sk-ant-') and len(key) > 20
    
    def _validate_snowflake(self, snowflake: int) -> bool:
        """Validate Discord snowflake ID"""
        # Discord snowflakes are 64-bit integers
        return 0 < snowflake < (2**63 - 1)
    
    def _validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def _validate_port(self, port: int) -> bool:
        """Validate port number"""
        return 1 <= port <= 65535
    
    def _validate_log_level(self, level: str) -> bool:
        """Validate logging level"""
        return level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def _parse_special_configs(self):
        """Parse configurations that need special handling"""
        
        # Parse allowed channels
        allowed_channels_str = self._config.get('ALLOWED_CHANNELS', '')
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
    
    def _validate_config_relationships(self, errors: List[str], warnings: List[str]):
        """Validate relationships between configuration values"""
        
        # Ensure crisis channel != resources channel
        crisis_channel = self._config.get('CRISIS_RESPONSE_CHANNEL_ID')
        resources_channel = self._config.get('RESOURCES_CHANNEL_ID')
        
        if crisis_channel == resources_channel:
            warnings.append("Crisis response and resources channels are the same")
        
        # Check if NLP service is configured properly
        nlp_host = self._config.get('NLP_SERVICE_HOST')
        nlp_port = self._config.get('NLP_SERVICE_PORT')
        
        if nlp_host and nlp_port:
            if nlp_host in ['localhost', '127.0.0.1'] and nlp_port == 8881:
                warnings.append("NLP service appears to be configured for local development")
    
    def _log_config_summary(self, errors: List[str], warnings: List[str]):
        """Log a comprehensive summary of loaded configuration"""
        
        if errors:
            logger.error("❌ Configuration validation failed:")
            for error in errors:
                logger.error(f"   • {error}")
        
        if warnings:
            logger.warning("⚠️ Configuration warnings:")
            for warning in warnings:
                logger.warning(f"   • {warning}")
        
        if not errors:
            logger.info("✅ Configuration loaded successfully:")
            logger.info(f"   🎯 Guild ID: {self._config.get('GUILD_ID')}")
            logger.info(f"   📺 Allowed channels: {len(self._config.get('ALLOWED_CHANNELS_LIST', []))}")
            logger.info(f"   🧠 NLP service: {self._config.get('NLP_SERVICE_HOST')}:{self._config.get('NLP_SERVICE_PORT')}")
            logger.info(f"   🔍 Discovery enabled: {self._config.get('ENABLE_KEYWORD_DISCOVERY')}")
            logger.info(f"   🤖 Claude model: {self._config.get('CLAUDE_MODEL')}")
            logger.info(f"   📊 Rate limits: {self._config.get('RATE_LIMIT_PER_USER')}/hr per user, {self._config.get('MAX_DAILY_CALLS')}/day total")
    
    # Existing getter methods with enhanced error handling...
    def get(self, key: str, default=None):
        """Get configuration value with fallback"""
        return self._config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = self._config.get(key, default)
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        value = self._config.get(key, default)
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            logger.warning(f"Invalid float value for {key}: {value}, using default: {default}")
            return default
    
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
    
    def get_validation_result(self) -> Optional[ConfigValidationResult]:
        """Get the configuration validation result"""
        return self._validation_result
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return self._validation_result and self._validation_result.is_valid