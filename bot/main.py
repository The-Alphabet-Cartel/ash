#!/usr/bin/env python3
"""
Ash Discord Bot - Modular Entry Point
Copy this to: ash/bot/main.py (REPLACE your current main.py)
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the bot directory to Python path
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from utils.logging_utils import setup_logging
from core.config_manager import ConfigManager

# Load environment variables
load_dotenv()

def print_startup_banner():
    """Print Ash's startup banner"""
    banner = """
    ╔══════════════════════════════════════╗
    ║              ASH BOT v2.0            ║
    ║     The Alphabet Cartel's            ║
    ║       Mental Health Sage             ║
    ║         Modular Architecture         ║
    ║                                      ║
    ║  "Building chosen family,            ║
    ║   one conversation at a time."       ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main entry point for Ash bot"""
    print_startup_banner()
    
    # Setup logging first
    logger = setup_logging()
    logger.info("🚀 Starting Ash Bot v2.0 (Modular Architecture)...")
    
    try:
        # Test configuration loading
        logger.info("🔧 Testing configuration...")
        config = ConfigManager()
        logger.info("✅ Configuration loaded successfully")
        
        # TODO: Initialize the full bot
        logger.info("🤖 Bot initialization logic will go here...")
        logger.info("📝 For now, testing configuration and logging...")
        
        # Test Discord token exists
        token = config.get('DISCORD_TOKEN')
        if token:
            logger.info(f"✅ Discord token configured ({len(token)} chars)")
        else:
            logger.error("❌ Discord token missing!")
            return
        
        # Test other critical configs
        guild_id = config.get_int('GUILD_ID')
        logger.info(f"✅ Guild ID: {guild_id}")
        
        allowed_channels = config.get_allowed_channels()
        if allowed_channels:
            logger.info(f"✅ Allowed channels: {len(allowed_channels)} configured")
        else:
            logger.info("✅ Allowed channels: All channels (no restrictions)")
        
        nlp_url = config.get_nlp_url()
        logger.info(f"✅ NLP service: {nlp_url}")
        
        logger.info("🎉 Modular configuration test complete!")
        logger.info("💡 Next: Run the bot with full modular components...")
        
    except Exception as e:
        logger.error(f"💥 Configuration test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Startup interrupted by user")
    except Exception as e:
        print(f"💥 Critical startup error: {e}")
        sys.exit(1)