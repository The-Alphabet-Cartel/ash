"""
Core Bot Manager - Main AshBot class with modular coordination
Copy this to: ash/bot/core/bot_manager.py
"""

import discord
from discord.ext import commands
import logging

from integrations.claude_integration import ClaudeIntegration
from integrations.nlp_integration import NLPIntegration
from services.detection_service import DetectionService
from handlers.message_handler import MessageHandler
from handlers.crisis_handler import CrisisHandler
from crisis_commands import CrisisKeywordCommands
from discovery_commands import DiscoveryCommands

logger = logging.getLogger(__name__)

class AshBot(commands.Bot):
    """Modular Ash Bot - Coordinates all components"""
    
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
        
        # Component references
        self.claude_integration = None
        self.nlp_integration = None
        self.detection_service = None
        self.message_handler = None
        self.crisis_handler = None
        
        logger.info("🤖 AshBot initialized with modular architecture")
    
    async def start_bot(self):
        """Start the bot with full initialization"""
        try:
            # Initialize all components in order
            await self._initialize_components()
            
            # Start the Discord bot
            token = self.config.get('DISCORD_TOKEN')
            if not token:
                raise ValueError("DISCORD_TOKEN not found in environment")
            
            await self.start(token)
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            await self.close()
            raise
    
    async def _initialize_components(self):
        """Initialize all bot components in correct order"""
        logger.info("🔧 Initializing modular components...")
        
        # Step 1: Initialize integrations (external dependencies)
        logger.info("🔌 Initializing integrations...")
        self.claude_integration = ClaudeIntegration(self.config)
        self.nlp_integration = NLPIntegration(self.config)
        
        # Test connections (don't await here - just initialize)
        logger.info("🔌 Integrations initialized (connection tests will run on bot start)")
        # Note: Connection tests will happen in on_ready() event
        
        # Step 2: Initialize services (business logic)
        logger.info("⚙️ Initializing services...")
        self.detection_service = DetectionService(
            self.claude_integration,
            self.nlp_integration,
            self.config
        )
        
        # Step 3: Initialize handlers (Discord event handling)
        logger.info("📨 Initializing handlers...")
        self.crisis_handler = CrisisHandler(self, self.config)
        self.message_handler = MessageHandler(
            self,
            self.detection_service,
            self.config
        )
        
        logger.info("✅ All modular components initialized")
    
    async def setup_hook(self):
        """Setup hook - add commands and sync"""
        logger.info("🔄 Starting setup_hook...")
        
        try:
            # Add your existing command cogs
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
    
    async def on_ready(self):
        """Bot ready event - final setup"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel')
        
        # Now test connections (in async context)
        logger.info("🔍 Testing integrations...")
        try:
            claude_ok = await self.claude_integration.test_connection()
            nlp_ok = await self.nlp_integration.test_connection()
            
            logger.info(f"Claude API: {'✅ Connected' if claude_ok else '❌ Failed'}")
            logger.info(f"NLP Service: {'✅ Connected' if nlp_ok else '❌ Failed'}")
        except Exception as e:
            logger.warning(f"Integration test error: {e}")
        
        # Log guild information
        guild = discord.utils.get(self.guilds, id=self.config.get_int('GUILD_ID'))
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}, manage_roles={perms.manage_roles}')
        else:
            logger.error(f'Could not find guild with ID: {self.config.get_int("GUILD_ID")}')
        
        logger.info("🎉 Ash Bot fully operational with modular architecture")
    
    async def on_message(self, message):
        """Route messages to message handler"""
        # Let the message handler deal with all message logic
        await self.message_handler.handle_message(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def close(self):
        """Clean shutdown of all components"""
        logger.info("🛑 Starting clean shutdown...")
        
        # Close integrations
        if self.claude_integration:
            await self.claude_integration.close()
        if self.nlp_integration:
            await self.nlp_integration.close()
        
        # Close parent
        await super().close()
        
        logger.info("✅ Clean shutdown complete")
    
    # Convenience methods for accessing components
    def get_claude_integration(self):
        return self.claude_integration
    
    def get_nlp_integration(self):
        return self.nlp_integration
    
    def get_detection_service(self):
        return self.detection_service
    
    def get_message_handler(self):
        return self.message_handler
        """Start the bot with full initialization"""
        try:
            # Initialize all components in order
            await self._initialize_components()
            
            # Start the Discord bot
            token = self.config.get('DISCORD_TOKEN')
            if not token:
                raise ValueError("DISCORD_TOKEN not found in environment")
            
            await self.start(token)
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            await self.close()
            raise
    
    async def _initialize_components(self):
        """Initialize all bot components in correct order"""
        logger.info("🔧 Initializing modular components...")
        
        # Step 1: Initialize integrations (external dependencies)
        logger.info("🔌 Initializing integrations...")
        self.claude_integration = ClaudeIntegration(self.config)
        self.nlp_integration = NLPIntegration(self.config)
        
        # Test connections
        await self.claude_integration.test_connection()
        await self.nlp_integration.test_connection()
        
        # Step 2: Initialize services (business logic)
        logger.info("⚙️ Initializing services...")
        self.detection_service = DetectionService(
            self.claude_integration,
            self.nlp_integration,
            self.config
        )
        
        # Step 3: Initialize handlers (Discord event handling)
        logger.info("📨 Initializing handlers...")
        self.message_handler = MessageHandler(
            self,
            self.detection_service,
            self.config
        )
        
        logger.info("✅ All modular components initialized")
    
    async def setup_hook(self):
        """Setup hook - add commands and sync"""
        logger.info("🔄 Starting setup_hook...")
        
        try:
            # Add your existing command cogs
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
    
    async def on_ready(self):
        """Bot ready event - final setup"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel')
        
        # Log guild information
        guild = discord.utils.get(self.guilds, id=self.config.get_int('GUILD_ID'))
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}, manage_roles={perms.manage_roles}')
        else:
            logger.error(f'Could not find guild with ID: {self.config.get_int("GUILD_ID")}')
        
        logger.info("🎉 Ash Bot fully operational with modular architecture")
    
    async def on_message(self, message):
        """Handle incoming messages - simplified for now"""
        # Ignore bot messages
        if message.author.bot:
            return
            
        # Only respond in configured guild
        if not message.guild or message.guild.id != self.config.get_int('GUILD_ID'):
            return
        
        # Check channel restrictions
        if not self.config.is_channel_allowed(message.channel.id):
            return
        
        # For now, just log that we received a message
        # We'll add the full message handling logic next
        logger.debug(f"📨 Message from {message.author} in {message.channel}: {message.content[:50]}...")
        
        # Process commands
        await self.process_commands(message)
    
    async def close(self):
        """Clean shutdown of all components"""
        logger.info("🛑 Starting clean shutdown...")
        
        # Close integrations
        if self.claude_integration:
            await self.claude_integration.close()
        if self.nlp_integration:
            await self.nlp_integration.close()
        
        # Close parent
        await super().close()
        
        logger.info("✅ Clean shutdown complete")
    
    # Convenience methods for accessing components
    def get_claude_integration(self):
        return self.claude_integration
    
    def get_nlp_integration(self):
        return self.nlp_integration