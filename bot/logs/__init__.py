"""
Logs Package for Ash Bot
Utilities for log file management and analysis
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Logs directory path
LOGS_DIR = Path(__file__).parent

def ensure_logs_directory():
    """Ensure logs directory exists"""
    LOGS_DIR.mkdir(exist_ok=True)

def get_log_files() -> List[Path]:
    """Get list of all log files"""
    ensure_logs_directory()
    return [f for f in LOGS_DIR.iterdir() if f.suffix == '.log']

def get_recent_logs(hours: int = 24) -> List[str]:
    """
    Get recent log entries from main log file
    
    Args:
        hours: Number of hours to look back
        
    Returns:
        List of recent log lines
    """
    log_file = LOGS_DIR / 'ash.log'
    
    if not log_file.exists():
        return []
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    recent_lines = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Simple timestamp check (assumes standard format)
                if line.startswith('202') and len(line) > 19:
                    try:
                        # Extract timestamp from log line
                        timestamp_str = line[:19]
                        log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        if log_time >= cutoff_time:
                            recent_lines.append(line.strip())
                    except ValueError:
                        # If timestamp parsing fails, include the line anyway
                        recent_lines.append(line.strip())
                else:
                    # Include non-timestamped lines (continuations, etc.)
                    recent_lines.append(line.strip())
                    
    except IOError as e:
        logging.error(f"Error reading log file: {e}")
    
    return recent_lines

def get_crisis_log_entries(hours: int = 24) -> List[str]:
    """Get recent crisis-related log entries"""
    crisis_log = LOGS_DIR / 'ash_crisis.log'
    
    if not crisis_log.exists():
        return []
    
    try:
        with open(crisis_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Return last N lines (simple approach)
        return [line.strip() for line in lines[-100:] if line.strip()]
        
    except IOError as e:
        logging.error(f"Error reading crisis log: {e}")
        return []

def get_error_log_entries(hours: int = 24) -> List[str]:
    """Get recent error log entries"""
    error_log = LOGS_DIR / 'ash_errors.log'
    
    if not error_log.exists():
        return []
    
    try:
        with open(error_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Return last N lines
        return [line.strip() for line in lines[-50:] if line.strip()]
        
    except IOError as e:
        logging.error(f"Error reading error log: {e}")
        return []

def cleanup_old_logs(days: int = 30):
    """
    Clean up log files older than specified days
    
    Args:
        days: Number of days to keep logs
    """
    ensure_logs_directory()
    cutoff_time = datetime.now() - timedelta(days=days)
    
    for log_file in get_log_files():
        try:
            # Check file modification time
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_time < cutoff_time:
                log_file.unlink()
                logging.info(f"Cleaned up old log file: {log_file.name}")
                
        except OSError as e:
            logging.error(f"Error cleaning up {log_file.name}: {e}")

def get_log_file_sizes() -> Dict[str, int]:
    """Get sizes of all log files in bytes"""
    sizes = {}
    
    for log_file in get_log_files():
        try:
            sizes[log_file.name] = log_file.stat().st_size
        except OSError:
            sizes[log_file.name] = 0
    
    return sizes

# Initialize logs directory on import
ensure_logs_directory()

__all__ = [
    "LOGS_DIR",
    "ensure_logs_directory",
    "get_log_files", 
    "get_recent_logs",
    "get_crisis_log_entries",
    "get_error_log_entries",
    "cleanup_old_logs",
    "get_log_file_sizes"
]