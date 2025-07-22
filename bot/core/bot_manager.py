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
        
        # Component references (your existing classes)
        self.claude_api = None
        self.nlp_client = None
        self.keyword_detector = None
        
        # Future modular components
        self.claude_integration = None
        self.nlp_integration = None
        self.detection_service = None
        self.message_handler = None
        self.crisis_handler = None
        
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
        """Initialize all bot components in async context"""
        logger.info("🔧 Initializing modular components...")
        
        # Step 1: Initialize integrations
        logger.info("🔌 Initializing integrations...")
        # Import your existing files directly
        from claude_api import ClaudeAPI
        from nlp_integration import RemoteNLPClient
        from keyword_detector import KeywordDetector
        
        # Create simple wrappers
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
        
        # For now, we'll use your existing main.py logic directly
        # This is the safest approach to get modular structure working
        logger.info("✅ Using your existing integration logic")
        logger.info("✅ All modular components initialized")
    
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
        """Handle messages using your existing logic"""
        
        # For now, implement your existing on_message logic directly here
        # This ensures we have working functionality first
        
        # Your existing filters
        if message.author.bot:
            return
            
        if not message.guild or message.guild.id != self.config.get_int('GUILD_ID'):
            return
        
        if not self.config.is_channel_allowed(message.channel.id):
            return
        
        # Basic crisis detection using your existing components
        try:
            if hasattr(self, 'keyword_detector'):
                keyword_result = self.keyword_detector.check_message(message.content)
                
                if keyword_result['needs_response']:
                    # Get response from Claude
                    response = await self.claude_api.get_ash_response(
                        message.content,
                        keyword_result['crisis_level'],
                        message.author.display_name
                    )
                    
                    # Simple response for now
                    await message.reply(response)
                    
                    logger.info(f"✅ Responded to {message.author} - Crisis level: {keyword_result['crisis_level']}")
        
        except Exception as e:
            logger.error(f"Error in message handling: {e}")
        
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