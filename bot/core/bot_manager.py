"""
Core Bot Manager - Simplified version without async issues
Copy this to: ash/bot/core/bot_manager.py (REPLACE the current one)
"""

import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class AshBot(commands.Bot):
    """Modular Ash Bot - Simplified version"""
    
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
            
            # Add command cogs
            from crisis_commands import CrisisKeywordCommands
            from discovery_commands import DiscoveryCommands
            
            await self.add_cog(CrisisKeywordCommands(self))
            await self.add_cog(DiscoveryCommands(self))
            
            # Sync commands globally
            logger.info("🌍 Syncing slash commands globally...")
            synced = await self.tree.sync()
            logger.info(f"✅ Synced {len(synced)} commands globally")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup hook failed: {e}")
            return False
    
    async def _initialize_components(self):
        """Initialize all bot components with enhanced modular architecture"""
        logger.info("🔧 Initializing enhanced modular components...")
        
        # Step 1: Initialize your existing integrations
        logger.info("🔌 Initializing integrations...")
        from claude_api import ClaudeAPI
        from nlp_integration import RemoteNLPClient
        from keyword_detector import KeywordDetector
        
        self.claude_api = ClaudeAPI()
        self.nlp_client = RemoteNLPClient()
        self.keyword_detector = KeywordDetector()
        
        # Test connections
        logger.info("🔍 Testing integrations...")
        try:
            claude_ok = await self.claude_api.test_connection()
            nlp_ok = await self.nlp_client.test_connection()
            
            logger.info(f"Claude API: {'✅ Connected' if claude_ok else '❌ Failed'}")
            logger.info(f"NLP Service: {'✅ Connected' if nlp_ok else '❌ Failed'}")
        except Exception as e:
            logger.warning(f"Integration test error: {e}")
        
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
        """Bot ready event"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel')
        
        # Log guild information
        guild = discord.utils.get(self.guilds, id=self.config.get_int('GUILD_ID'))
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}')
        
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
            if self.claude_integration:
                await self.claude_integration.close()
        except:
            pass
        
        try:
            if self.nlp_integration:
                await self.nlp_integration.close()
        except:
            pass
        
        # Close parent
        await super().close()
        
        logger.info("✅ Clean shutdown complete")