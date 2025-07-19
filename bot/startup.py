#!/usr/bin/env python3
"""
Ash Bot Startup Script
Tests connections and starts the bot with proper error handling
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

from main import AshBot
from claude_api import ClaudeAPI
from keyword_detector import KeywordDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/ash_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_connections():
    """Test all critical connections before starting bot"""
    logger.info("🔧 Testing Ash Bot connections...")
    
    # Test environment variables
    required_vars = [
        'DISCORD_TOKEN', 'CLAUDE_API_KEY', 'GUILD_ID', 
        'RESOURCES_CHANNEL_ID', 'STAFF_PING_USER'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ Environment variables loaded")
    
    # Test Claude API connection
    try:
        claude_api = ClaudeAPI()
        api_test = await claude_api.test_connection()
        await claude_api.close()
        
        if api_test:
            logger.info("✅ Claude API connection successful")
        else:
            logger.error("❌ Claude API connection failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Claude API test error: {e}")
        return False
    
    # Test keyword detector
    try:
        detector = KeywordDetector()
        stats = detector.get_keyword_stats()
        logger.info(f"✅ Keyword detector loaded: {stats['total']} keywords across {len(stats)-1} crisis levels")
        
        # Test detection
        test_result = detector.check_message("I feel really depressed today")
        if test_result['needs_response']:
            logger.info(f"✅ Keyword detection test passed: {test_result['crisis_level']} level")
        else:
            logger.warning("⚠️ Keyword detection test unexpected result")
            
    except Exception as e:
        logger.error(f"❌ Keyword detector test error: {e}")
        return False
    
    logger.info("🎉 All connection tests passed!")
    return True

async def create_directories():
    """Create necessary directories for logs and data"""
    directories = ['/app/logs', '/app/data']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"📁 Ensured directory exists: {directory}")

def print_startup_banner():
    """Print Ash's startup banner"""
    banner = """
    ╔══════════════════════════════════════╗
    ║              ASH BOT                 ║
    ║     The Alphabet Cartel's            ║
    ║       Mental Health Sage             ║
    ║                                      ║
    ║  "Building chosen family,            ║
    ║   one conversation at a time."       ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main startup function"""
    print_startup_banner()
    
    # Load environment variables
    load_dotenv()
    logger.info("🔄 Starting Ash Bot initialization...")
    
    # Create necessary directories
    await create_directories()
    
    # Test all connections
    if not await test_connections():
        logger.error("💥 Connection tests failed. Exiting.")
        sys.exit(1)
    
    # Initialize and start the bot
    try:
        logger.info("🚀 Starting Ash Bot...")
        bot = AshBot()
        
        # Add graceful shutdown handling
        async def shutdown():
            logger.info("🛑 Shutting down Ash Bot...")
            await bot.close()
        
        # Register shutdown handler
        import signal
        def signal_handler(signum, frame):
            logger.info(f"📢 Received signal {signum}")
            asyncio.create_task(shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the bot
        await bot.start(os.getenv('DISCORD_TOKEN'))
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Unexpected error starting bot: {e}")
        sys.exit(1)
    finally:
        logger.info("👋 Ash Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Startup interrupted by user")
    except Exception as e:
        logger.error(f"💥 Critical startup error: {e}")
        sys.exit(1)