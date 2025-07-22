"""
Logging Utilities - Centralized logging configuration
Copy this to: ash/bot/utils/logging_utils.py
"""

import logging
import os
import sys
from pathlib import Path

def setup_logging() -> logging.Logger:
    """Setup centralized logging configuration"""
    
    # Ensure logs directory exists
    logs_dir = Path('./logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler('./logs/ash.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for important logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Create separate error log
    error_handler = logging.FileHandler('./logs/ash_errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Reduce Discord.py noise
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    # Main application logger
    app_logger = logging.getLogger('ash')
    app_logger.setLevel(numeric_level)
    
    # Log startup message
    app_logger.info("=" * 50)
    app_logger.info("🚀 ASH BOT MODULAR LOGGING INITIALIZED")
    app_logger.info(f"📊 Log level: {log_level}")
    app_logger.info("=" * 50)
    
    return app_logger