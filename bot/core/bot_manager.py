#!/usr/bin/env python3
"""
Core Bot Manager - Integrated with Resource Management
Replace bot/core/bot_manager.py with this version
"""

import discord
from discord.ext import commands
import logging
from utils.resource_managers import ResourceCleanupMixin, graceful_shutdown
from utils.security import get_security_manager

logger = logging.getLogger(__name__)

class AshBot(commands.Bot, ResourceCleanupMixin):
    """Enhanced Ash Bot with Resource Management and Security"""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize resource management
        ResourceCleanupMixin.__init__(self)
        
        # Setup Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        commands.Bot.__init__(
            self,
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
        self.security_manager = None
        
        # Register shutdown handler
        graceful_shutdown.register_shutdown_handler(self.cleanup_resources)
        
        logger.info("🤖 AshBot initialized with enhanced resource management")
    
    async def setup_hook(self):
        """Setup hook - initialize components with resource management"""
        logger.info("🔄 Starting enhanced setup_hook...")
        
        try:
            # Initialize security manager first
            self.security_manager = get_security_manager(self.config)
            
            # Initialize components (now with resource management)
            await self._initialize_components()
            
            # Add command cogs
            await self._load_command_cogs()
            
            # Sync commands globally
            await self._sync_slash_commands()
            
            logger.info("✅ Enhanced setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup hook failed: {e}")
            logger.exception("Full setup_hook traceback:")
            return False
    
    async def _initialize_components(self):
        """Initialize all bot components with enhanced resource management"""
        logger.info("🔧 Initializing enhanced components...")
        
        # Step 1: Initialize integrations with resource management
        logger.info("🔌 Initializing integrations with resource management...")
        from integrations.claude_api import ClaudeAPI
        from integrations.nlp_integration import RemoteNLPClient
        from utils.keyword_detector import KeywordDetector
        
        self.claude_api = ClaudeAPI()
        self.nlp_client = RemoteNLPClient()
        self.keyword_detector = KeywordDetector()
        
        # Register cleanup for integrations
        self.register_cleanup(self.claude_api.close)
        # Note: Add nlp_client.close if it has one
        
        # Test connections with better error handling
        logger.info("🔍 Testing integrations with enhanced error handling...")
        try:
            claude_ok = await self.claude_api.test_connection()
            logger.info(f"Claude API: {'✅ Connected' if claude_ok else '❌ Failed'}")
            
            # Log security event for API connection
            if claude_ok:
                self.security_manager.log_security_event(
                    "api_connection_success", 0, 0, 0,
                    {"service": "claude_api"}, "info"
                )
            else:
                self.security_manager.log_security_event(
                    "api_connection_failed", 0, 0, 0,
                    {"service": "claude_api"}, "warning"
                )
                
        except Exception as e:
            logger.warning(f"Claude API test error: {e}")
            self.security_manager.log_security_event(
                "api_connection_error", 0, 0, 0,
                {"service": "claude_api", "error": str(e)}, "error"
            )
        
        try:
            nlp_ok = await self.nlp_client.test_connection()
            logger.info(f"NLP Service: {'✅ Connected' if nlp_ok else '❌ Failed'}")
            
            # Log security event for NLP connection
            if nlp_ok:
                self.security_manager.log_security_event(
                    "nlp_connection_success", 0, 0, 0,
                    {"service": "nlp_server", "host": self.config.get('NLP_SERVICE_HOST')}, "info"
                )
                
        except Exception as e:
            logger.warning(f"NLP Service test error: {e}")
            self.security_manager.log_security_event(
                "nlp_connection_error", 0, 0, 0,
                {"service": "nlp_server", "error": str(e)}, "error"
            )
        
        # Step 2: Initialize enhanced handlers with security
        logger.info("🚨 Initializing enhanced handlers with security...")
        from handlers.crisis_handler import CrisisHandler
        from handlers.message_handler import MessageHandler
        
        self.crisis_handler = CrisisHandler(self, self.config)
        
        self.message_handler = MessageHandler(
            self,
            self.claude_api,
            self.nlp_client, 
            self.keyword_detector,
            self.crisis_handler,
            self.config,
            security_manager=self.security_manager  # Pass security manager
        )
        
        logger.info("✅ All enhanced components initialized")
    
    async def _load_command_cogs(self):
        """Load command cogs with enhanced learning system"""
        cog_errors = []
        
        # Load Crisis Commands
        try:
            from commands.crisis_commands import CrisisKeywordCommands
            await self.add_cog(CrisisKeywordCommands(self))
            logger.info("✅ Loaded Crisis Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load Crisis Commands: {e}")
            cog_errors.append(f"CrisisCommands: {e}")
        
        # Load Monitoring Commands
        try:
            from commands.monitoring_commands import MonitoringCommands
            await self.add_cog(MonitoringCommands(self))
            logger.info("✅ Loaded Monitoring Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load Monitoring Commands: {e}")
            cog_errors.append(f"MonitoringCommands: {e}")

        # Load Enhanced Learning Commands (replaces false_positive_commands)
        try:
            from commands.enhanced_learning_commands import EnhancedLearningCommands
            await self.add_cog(EnhancedLearningCommands(self))
            logger.info("✅ Loaded Enhanced Learning Commands cog (false positives + negatives)")
        except Exception as e:
            logger.error(f"❌ Failed to load Enhanced Learning Commands: {e}")
            cog_errors.append(f"EnhancedLearningCommands: {e}")

        # Log cog loading errors as security events
        if cog_errors:
            logger.warning(f"⚠️ Cog loading errors: {cog_errors}")
            self.security_manager.log_security_event(
                "cog_loading_errors", 0, 0, 0,
                {"errors": cog_errors}, "warning"
            )

    async def _sync_slash_commands(self):
        """Sync slash commands with enhanced logging"""
        total_commands = len([cmd for cmd in self.tree.walk_commands()])
        logger.info(f"📋 Found {total_commands} commands in tree before sync")
        
        # Log command sync attempt
        self.security_manager.log_security_event(
            "command_sync_attempt", 0, 0, 0,
            {"command_count": total_commands}, "info"
        )
        
        logger.info("🌍 Syncing slash commands globally...")
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Global sync successful: {len(synced)} commands")
            
            # Log each synced command
            for cmd in synced:
                logger.info(f"   📝 Synced: /{cmd.name} - {cmd.description[:50]}...")
            
            # Log successful sync
            self.security_manager.log_security_event(
                "command_sync_success", 0, 0, 0,
                {"synced_count": len(synced)}, "info"
            )
            
            return True
            
        except Exception as sync_error:
            logger.error(f"❌ Command sync failed: {sync_error}")
            self.security_manager.log_security_event(
                "command_sync_failed", 0, 0, 0,
                {"error": str(sync_error)}, "error"
            )
            return False
    
    async def on_ready(self):
        """Bot ready event with enhanced security logging"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel')
        
        # Log bot startup as security event
        self.security_manager.log_security_event(
            "bot_startup", 0, 0, 0,
            {"bot_user": str(self.user), "bot_id": self.user.id}, "info"
        )
        
        # Log guild information with security context
        guild = discord.utils.get(self.guilds, id=self.config.get_int('GUILD_ID'))
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}, use_application_commands={perms.use_application_commands}')
                
                # Log permission status as security event
                self.security_manager.log_security_event(
                    "bot_permissions_check", 0, guild.id, 0,
                    {
                        "send_messages": perms.send_messages,
                        "use_application_commands": perms.use_application_commands,
                        "guild_name": guild.name
                    }, 
                    "info"
                )
        
        # Verify slash commands are registered
        try:
            app_commands = await self.tree.fetch_commands()
            logger.info(f"🔍 Verified {len(app_commands)} commands registered with Discord:")
            for cmd in app_commands:
                logger.info(f"   ✅ /{cmd.name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch registered commands: {e}")
            self.security_manager.log_security_event(
                "command_verification_failed", 0, 0, 0,
                {"error": str(e)}, "error"
            )
        
        logger.info("🎉 Ash Bot fully operational with enhanced security")
    
    async def on_message(self, message):
        """Route messages with security validation"""
        # Basic security validation
        if not self.security_manager.validate_channel_access(message.channel.id):
            # Removed the warning log since this is expected behavior
            # If you need debugging, uncomment the following line:
            #logger.warning(f"Message from unauthorized channel: {message.channel.id}")
            return
        
        # Pass to message handler (which now has security manager)
        if self.message_handler:
            await self.message_handler.handle_message(message)
        else:
            logger.debug("Message handler not ready, using basic handling")
        
        # Process commands
        await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors with security logging"""
        logger.error(f"Command error in {ctx.command}: {error}")
        
        # Log as security event if it might be malicious
        if isinstance(error, (commands.CommandNotFound, commands.MissingPermissions)):
            self.security_manager.log_security_event(
                "command_error", ctx.author.id, ctx.guild.id if ctx.guild else 0, ctx.channel.id,
                {"command": str(ctx.command), "error": str(error)}, "warning"
            )
    
    async def close(self):
        """Enhanced cleanup with resource management"""
        logger.info("🛑 Starting enhanced shutdown...")
        
        # Use resource cleanup mixin
        await self.cleanup_resources()
        
        # Close parent
        await super().close()
        
        logger.info("✅ Enhanced shutdown complete")

# Export for backwards compatibility
AshBotEnhanced = AshBot