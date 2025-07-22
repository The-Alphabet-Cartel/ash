#!/usr/bin/env python3
"""
Core Bot Manager - Fixed version with proper command loading
Copy this to: ash/bot/core/bot_manager.py (REPLACE the current one)
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class AshBot(commands.Bot):
    """Modular Ash Bot - Fixed command loading"""
    
    def __init__(self, config):
        self.config = config
        
        # Setup Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!ash ',
            intents=intents,
            help_command=None
        )
        
        # Enhanced component references
        self.claude_api = None
        self.nlp_client = None
        self.keyword_detector = None
        self.crisis_handler = None
        self.message_handler = None
        
        # Future additional components
        self.rate_limit_service = None
        self.discovery_integration = None
        
        logger.info("🤖 AshBot initialized with modular architecture")
    
    async def setup_hook(self):
        """Setup hook - initialize components and add commands"""
        logger.info("🔄 Starting setup_hook...")
        
        try:
            # Initialize components (now in async context)
            await self._initialize_components()
            
            # Add command cogs - FIXED: Load all 3 cogs
            cog_errors = []
            
            # Load Crisis Commands
            try:
                from commands.crisis_commands import CrisisKeywordCommands
                await self.add_cog(CrisisKeywordCommands(self))
                logger.info("✅ Loaded Crisis Commands cog")
            except Exception as e:
                logger.error(f"❌ Failed to load Crisis Commands: {e}")
                cog_errors.append(f"CrisisCommands: {e}")
            
            # Load Discovery Commands
            try:
                from commands.discovery_commands import DiscoveryCommands
                await self.add_cog(DiscoveryCommands(self))
                logger.info("✅ Loaded Discovery Commands cog")
            except Exception as e:
                logger.error(f"❌ Failed to load Discovery Commands: {e}")
                cog_errors.append(f"DiscoveryCommands: {e}")
            
            # Load Monitoring Commands - THIS WAS MISSING
            try:
                from commands.monitoring_commands import MonitoringCommands
                await self.add_cog(MonitoringCommands(self))
                logger.info("✅ Loaded Monitoring Commands cog")
            except Exception as e:
                logger.error(f"❌ Failed to load Monitoring Commands: {e}")
                cog_errors.append(f"MonitoringCommands: {e}")
            
            # Log any cog loading errors
            if cog_errors:
                logger.warning(f"⚠️ Cog loading errors: {cog_errors}")
            
            # Count total commands before sync
            total_commands = len([cmd for cmd in self.tree.walk_commands()])
            logger.info(f"📋 Found {total_commands} commands in tree before sync")
            
            # Sync commands globally with better error handling
            logger.info("🌍 Syncing slash commands globally...")
            try:
                synced = await self.tree.sync()
                logger.info(f"✅ Global sync successful: {len(synced)} commands")
                
                # Log each synced command for debugging
                for cmd in synced:
                    logger.info(f"   📝 Synced: /{cmd.name} - {cmd.description[:50]}...")
                
                return True
                
            except Exception as sync_error:
                logger.error(f"❌ Command sync failed: {sync_error}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Setup hook failed: {e}")
            logger.exception("Full setup_hook traceback:")
            return False
    
    async def _initialize_components(self):
        """Initialize all bot components with enhanced modular architecture"""
        logger.info("🔧 Initializing enhanced modular components...")
        
        # Step 1: Initialize your existing integrations
        logger.info("🔌 Initializing integrations...")
        from integrations.claude_api import ClaudeAPI
        from integrations.nlp_integration import RemoteNLPClient
        from utils.keyword_detector import KeywordDetector
        
        self.claude_api = ClaudeAPI()
        self.nlp_client = RemoteNLPClient()
        self.keyword_detector = KeywordDetector()
        
        # Test connections with better error handling
        logger.info("🔍 Testing integrations...")
        try:
            claude_ok = await self.claude_api.test_connection()
            logger.info(f"Claude API: {'✅ Connected' if claude_ok else '❌ Failed'}")
        except Exception as e:
            logger.warning(f"Claude API test error: {e}")
        
        try:
            nlp_ok = await self.nlp_client.test_connection()
            logger.info(f"NLP Service: {'✅ Connected' if nlp_ok else '❌ Failed'}")
        except Exception as e:
            logger.warning(f"NLP Service test error: {e}")
        
        # Step 2: Initialize enhanced handlers
        logger.info("🚨 Initializing enhanced crisis handler...")
        from handlers.crisis_handler import CrisisHandler
        self.crisis_handler = CrisisHandler(self, self.config)
        
        logger.info("📨 Initializing enhanced message handler...")
        from handlers.message_handler import MessageHandler
        self.message_handler = MessageHandler(
            self,
            self.claude_api,
            self.nlp_client, 
            self.keyword_detector,
            self.crisis_handler,
            self.config
        )
        
        logger.info("✅ All enhanced modular components initialized")
    
    async def on_ready(self):
        """Bot ready event with command verification"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel')
        
        # Log guild information
        guild = discord.utils.get(self.guilds, id=self.config.get_int('GUILD_ID'))
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}, use_slash_commands={perms.use_slash_commands}')
        
        # Verify slash commands are registered
        try:
            app_commands = await self.tree.fetch_commands()
            logger.info(f"🔍 Verified {len(app_commands)} commands registered with Discord:")
            for cmd in app_commands:
                logger.info(f"   ✅ /{cmd.name}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch registered commands: {e}")
        
        logger.info("🎉 Ash Bot fully operational with modular architecture")
    
    async def on_message(self, message):
        """Route messages to enhanced message handler"""
        if self.message_handler:
            await self.message_handler.handle_message(message)
        else:
            # Fallback to basic handling if message handler not ready
            logger.debug("Message handler not ready, using basic handling")
        
        # Process commands
        await self.process_commands(message)
    
    async def close(self):
        """Clean shutdown"""
        logger.info("🛑 Starting clean shutdown...")
        
        # Close integrations
        try:
            if self.claude_api:
                await self.claude_api.close()
        except:
            pass
        
        try:
            if self.nlp_client:
                # Assuming it has a close method
                pass
        except:
            pass
        
        # Close parent
        await super().close()
        
        logger.info("✅ Clean shutdown complete")