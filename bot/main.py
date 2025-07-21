import asyncio
import logging
import os
import warnings
import time
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keyword_detector import KeywordDetector
from claude_api import ClaudeAPI
from ash_character import ASH_CHARACTER_PROMPT
from nlp_integration import RemoteNLPClient, hybrid_crisis_detection
from crisis_commands import CrisisKeywordCommands

# Suppress specific aiohttp cleanup warnings
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*client_session.*")
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*connector.*")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/ash.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AshBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!ash ',
            intents=intents,
            help_command=None
        )
        
        self.keyword_detector = KeywordDetector()
        self.claude_api = ClaudeAPI()
        self.nlp_client = RemoteNLPClient()

        self.guild_id = int(os.getenv('GUILD_ID', '0'))
        self.resources_channel_id = int(os.getenv('RESOURCES_CHANNEL_ID', '0'))
        self.crisis_response_channel_id = int(os.getenv('CRISIS_RESPONSE_CHANNEL_ID', '0'))
        self.crisis_response_role_id = os.getenv('CRISIS_RESPONSE_ROLE_ID', '0')
        self.staff_ping_user = os.getenv('STAFF_PING_USER', '0')

        # Add validation
        if not self.guild_id:
            raise ValueError("GUILD_ID environment variable is required")
        if not self.resources_channel_id:
            raise ValueError("RESOURCES_CHANNEL_ID environment variable is required")
        if not self.crisis_response_channel_id:
            raise ValueError("CRISIS_RESPONSE_CHANNEL_ID environment variable is required")
        if not self.crisis_response_role_id:
            raise ValueError("CRISIS_RESPONSE_ROLE_ID environment variable is required")
        if not self.staff_ping_user:
            raise ValueError("STAFF_PING_USER environment variable is required")

        # Parse allowed channels from environment variable
        allowed_channels_str = os.getenv('ALLOWED_CHANNELS', '')
        if allowed_channels_str:
            self.allowed_channels = [int(ch.strip()) for ch in allowed_channels_str.split(',') if ch.strip()]
        else:
            self.allowed_channels = []  # Empty list means no restrictions
            
        logger.info(f"Ash will respond in {len(self.allowed_channels)} allowed channels: {self.allowed_channels}")
        
        # Rate limiting
        self.user_cooldowns = {}
        self.daily_call_count = 0
        self.max_daily_calls = int(os.getenv('MAX_DAILY_CALLS', 1000))
        
        # Conversation tracking for follow-ups
        self.active_conversations = {}  # user_id: {'start_time': time, 'crisis_level': str, 'channel_id': int}
        self.conversation_timeout = 300  # 5 minutes in seconds
        
    async def on_ready(self):
        logger.info(f'{self.user} has awakened in The Alphabet Cartel')
        await self.nlp_client.test_connection()
        guild = discord.utils.get(self.guilds, id=self.guild_id)
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions in guild
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}, manage_roles={perms.manage_roles}')
            
            # Try to fetch existing commands
            try:
                commands = await self.tree.fetch_commands(guild=guild)
                if commands:
                    cmd_names = [cmd.name for cmd in commands]
                    logger.info(f'✅ Available slash commands: {", ".join(cmd_names)}')
                else:
                    logger.warning('⚠️ No slash commands found in guild')
                    
                    # Try global commands
                    global_commands = await self.tree.fetch_commands()
                    if global_commands:
                        global_names = [cmd.name for cmd in global_commands]
                        logger.info(f'ℹ️ Global commands available: {", ".join(global_names)}')
                    else:
                        logger.error('❌ No commands found globally either')
                        
            except discord.Forbidden:
                logger.error('❌ Bot lacks permission to fetch commands')
            except Exception as e:
                logger.error(f'❌ Error fetching commands: {e}')
            
            logger.info(f'🎯 Crisis Response role ID: {self.crisis_response_role_id}')
            
        else:
            logger.error(f'Could not find guild with ID: {self.guild_id}')

    async def setup_hook(self):
        """Setup hook to add cogs and sync commands"""
        logger.info("🔄 Starting setup_hook...")
        
        try:
            # Load the cog
            cog = CrisisKeywordCommands(self)
            await self.add_cog(cog)
            logger.info("✅ CrisisKeywordCommands cog added successfully")
            
            # Check how many commands the cog has
            cog_commands = [cmd for cmd in self.tree.walk_commands()]
            logger.info(f"📋 Found {len(cog_commands)} commands in tree:")
            for cmd in cog_commands:
                logger.info(f"   - {cmd.name}: {cmd.description}")
            
            # Check if we can access the guild
            guild_obj = discord.Object(id=self.guild_id)
            logger.info(f"🎯 Target guild ID: {self.guild_id}")
            
            # Attempt to sync commands
            logger.info("🔄 Syncing slash commands...")
            synced = await self.tree.sync(guild=guild_obj)
            
            logger.info(f"✅ Successfully synced {len(synced)} commands!")
            for cmd in synced:
                logger.info(f"   📋 /{cmd.name} - {cmd.description}")
                
            return True
            
        except discord.Forbidden as e:
            logger.error(f"❌ FORBIDDEN: Bot lacks permissions to sync commands")
            logger.error(f"   Error details: {e}")
            logger.error("   💡 Solution: Re-invite bot with 'applications.commands' scope")
            return False
            
        except discord.HTTPException as e:
            logger.error(f"❌ HTTP Error syncing commands: {e}")
            if e.status == 403:
                logger.error("   💡 This is likely a permissions issue")
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in setup_hook: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
            
        # Only respond in the configured guild
        if not message.guild or message.guild.id != self.guild_id:
            return
        
        # Check if channel is in allowed list (if restrictions are enabled)
        if self.allowed_channels and message.channel.id not in self.allowed_channels:
            return  # Silently ignore messages in non-allowed channels
        
        # Clean up expired conversations
        self.cleanup_expired_conversations()
        
        # Check if user is in an active conversation
        user_id = message.author.id
        if user_id in self.active_conversations:
            await self.handle_conversation_followup(message)
            return
            
        # Check for keywords that indicate need for support using hybrid detection
        detection_result = await hybrid_crisis_detection(
            self.keyword_detector, 
            self.nlp_client, 
            message
        )

        if detection_result['needs_response']:
            await self.handle_support_message(message, detection_result)

        # Process commands
        await self.process_commands(message)
    
    async def handle_support_message(self, message, keyword_result):
        """Handle messages that need Ash's support"""
        
        # Rate limiting check
        if not await self.check_rate_limits(message.author.id):
            return
            
        # Daily call limit check
        if self.daily_call_count >= self.max_daily_calls:
            logger.warning("Daily API call limit reached")
            return
            
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Get response from Claude as Ash
                response = await self.claude_api.get_ash_response(
                    message.content,
                    keyword_result['crisis_level'],
                    message.author.display_name
                )
                
                # Handle crisis escalation
                if keyword_result['crisis_level'] == 'high':
                    await self.handle_crisis_escalation(message, response)
                elif keyword_result['crisis_level'] == 'medium':
                    await self.handle_medium_crisis(message, response)
                else:
                    await message.reply(response)
                
                # Start conversation tracking for all support responses
                self.start_conversation_tracking(message.author.id, keyword_result['crisis_level'], message.channel.id)
                    
                self.daily_call_count += 1
                logger.info(f"Responded to {message.author} - Crisis level: {keyword_result['crisis_level']}")
                
        except Exception as e:
            logger.error(f"Error handling support message: {e}")
            await message.add_reaction('❌')
    
    async def handle_crisis_escalation(self, message, ash_response):
        """Handle high-crisis situations with staff DM and role ping"""
        
        # Send Ash's response
        await message.reply(ash_response)
        
        # DM the staff member directly
        if self.staff_ping_user:
            try:
                staff_user = await self.fetch_user(int(self.staff_ping_user))
                
                embed = discord.Embed(
                    title="🚨 Crisis Support Needed - URGENT",
                    description=f"High-crisis keywords detected requiring immediate attention",
                    color=discord.Color.red(),
                    timestamp=message.created_at
                )
                embed.add_field(name="User", value=f"{message.author.mention} ({message.author.display_name})", inline=True)
                embed.add_field(name="Channel", value=f"{message.channel.mention} ({message.channel.name})", inline=True)
                embed.add_field(name="Server", value=message.guild.name, inline=True)
                embed.add_field(name="Original Message", value=message.content[:1000] + ("..." if len(message.content) > 1000 else ""), inline=False)
                embed.add_field(name="Jump to Message", value=f"[Click here]({message.jump_url})", inline=False)
                embed.add_field(name="Resources Channel", value=f"<#{self.resources_channel_id}>", inline=False)
                
                await staff_user.send(embed=embed)
                logger.warning(f"Crisis escalation DM sent to staff for {message.author} in {message.channel}")
                
            except discord.NotFound:
                logger.error(f"Staff user ID {self.staff_ping_user} not found")
            except discord.Forbidden:
                logger.error(f"Cannot send DM to staff user - DMs may be disabled")
            except Exception as e:
                logger.error(f"Error sending crisis DM to staff: {e}")
        
        # Ping crisis response team in dedicated crisis channel
        crisis_channel = self.get_channel(self.crisis_response_channel_id)
        if crisis_channel and self.crisis_response_role_id:
            try:
                role_mention = f"<@&{self.crisis_response_role_id}>"
                
                alert_embed = discord.Embed(
                    title="🚨 Crisis Response Team Alert",
                    description=f"High-crisis situation detected requiring team response",
                    color=discord.Color.red(),
                    timestamp=message.created_at
                )
                alert_embed.add_field(name="Location", value=f"{message.channel.mention} in {message.guild.name}", inline=True)
                alert_embed.add_field(name="User", value=message.author.mention, inline=True)
                alert_embed.add_field(name="Action Needed", value="Please respond to provide crisis support", inline=False)
                alert_embed.add_field(name="Jump to Message", value=f"[Click here]({message.jump_url})", inline=False)
                
                await crisis_channel.send(f"{role_mention}", embed=alert_embed)
                logger.warning(f"Crisis response team alerted for {message.author} in {message.channel}")
                
            except Exception as e:
                logger.error(f"Error pinging crisis response team: {e}")
        else:
            logger.warning("Crisis response team role not configured or crisis response channel not found")
            
        logger.warning(f"Full crisis escalation completed for {message.author} in {message.channel}")
    
    async def handle_medium_crisis(self, message, ash_response):
        """Handle medium-crisis situations with team notification (no staff DM)"""
        
        # Send Ash's response
        await message.reply(ash_response)
        
        # Ping crisis response team in dedicated crisis channel (no staff DM for medium)
        crisis_channel = self.get_channel(self.crisis_response_channel_id)
        if crisis_channel and self.crisis_response_role_id:
            try:
                role_mention = f"<@&{self.crisis_response_role_id}>"
                
                alert_embed = discord.Embed(
                    title="⚠️ Medium Crisis Alert",
                    description=f"Significant distress detected - team awareness needed",
                    color=discord.Color.orange(),
                    timestamp=message.created_at
                )
                alert_embed.add_field(name="Location", value=f"{message.channel.mention} in {message.guild.name}", inline=True)
                alert_embed.add_field(name="User", value=message.author.mention, inline=True)
                alert_embed.add_field(name="Crisis Level", value="Medium - Monitor situation", inline=True)
                alert_embed.add_field(name="Jump to Message", value=f"[Click here]({message.jump_url})", inline=False)
                
                await crisis_channel.send(f"{role_mention}", embed=alert_embed)
                logger.info(f"Medium crisis team alert sent for {message.author} in {message.channel}")
                
            except Exception as e:
                logger.error(f"Error sending medium crisis alert: {e}")
        else:
            logger.warning("Crisis response team role not configured or crisis response channel not found")
            
        logger.info(f"Medium crisis handling completed for {message.author} in {message.channel}")

    async def close(self):
        """Clean shutdown of bot and API connections"""
        await self.nlp_client.close()
        await self.claude_api.close()
        await super().close()
        logger.info("Bot shutdown complete - all connections closed")
    
    async def check_rate_limits(self, user_id):
        """Check if user is within rate limits"""
        # Instead of: current_time = asyncio.get_event_loop().time()
        current_time = time.time()
        rate_limit = int(os.getenv('RATE_LIMIT_PER_USER', 10))
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
            
        # Remove old timestamps (older than 1 hour)
        self.user_cooldowns[user_id] = [
            timestamp for timestamp in self.user_cooldowns[user_id]
            if current_time - timestamp < 3600
        ]
        
        # Check if under rate limit
        if len(self.user_cooldowns[user_id]) >= rate_limit:
            return False
            
        # Add current timestamp
        self.user_cooldowns[user_id].append(current_time)
        return True
    
    def start_conversation_tracking(self, user_id, crisis_level, channel_id):
        """Start tracking a conversation for follow-up responses"""
        self.active_conversations[user_id] = {
            'start_time': time.time(),
            'crisis_level': crisis_level,
            'channel_id': channel_id
        }
        logger.info(f"Started conversation tracking for user {user_id} (crisis: {crisis_level})")
    
    def cleanup_expired_conversations(self):
        """Remove expired conversations (older than 5 minutes)"""
        current_time = time.time()
        expired_users = []
        
        for user_id, conv_data in self.active_conversations.items():
            if current_time - conv_data['start_time'] > self.conversation_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.active_conversations[user_id]
            logger.info(f"Conversation tracking expired for user {user_id}")
    
    async def handle_conversation_followup(self, message):
        """Handle follow-up messages in active conversations"""
        user_id = message.author.id
        conv_data = self.active_conversations[user_id]
        
        # Only respond in the same channel where conversation started
        if message.channel.id != conv_data['channel_id']:
            return
        
        # Double-check channel restrictions for follow-ups too
        if self.allowed_channels and message.channel.id not in self.allowed_channels:
            return
        
        # Check if crisis level has escalated in this follow-up message
        keyword_result = self.keyword_detector.check_message(message.content)
        current_crisis_level = conv_data['crisis_level']
        new_crisis_level = keyword_result.get('crisis_level', 'none')
        
        # Determine if we need to escalate
        crisis_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        if crisis_hierarchy.get(new_crisis_level, 0) > crisis_hierarchy.get(current_crisis_level, 0):
            # Crisis has escalated - update conversation and handle escalation
            conv_data['crisis_level'] = new_crisis_level
            logger.warning(f"Crisis escalated from {current_crisis_level} to {new_crisis_level} for user {user_id}")
            
            # Use the new higher crisis level for response
            effective_crisis_level = new_crisis_level
        else:
            # No escalation - continue with original crisis level
            effective_crisis_level = current_crisis_level
        
        # Rate limiting check for follow-ups too
        if not await self.check_rate_limits(user_id):
            return
            
        # Daily call limit check
        if self.daily_call_count >= self.max_daily_calls:
            logger.warning("Daily API call limit reached")
            return
            
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Get response from Claude as Ash
                response = await self.claude_api.get_ash_response(
                    message.content,
                    effective_crisis_level,
                    message.author.display_name
                )
                
                # Handle escalated crisis responses
                if new_crisis_level == 'high' and current_crisis_level != 'high':
                    await self.handle_crisis_escalation(message, response)
                elif new_crisis_level == 'medium' and current_crisis_level == 'low':
                    await self.handle_medium_crisis(message, response)
                else:
                    await message.reply(response)
                
                # Don't reset conversation timer - let it expire naturally after 5 minutes from start
                
                self.daily_call_count += 1
                logger.info(f"Follow-up response to {message.author} (crisis: {effective_crisis_level})")
                
        except Exception as e:
            logger.error(f"Error handling conversation follow-up: {e}")
            await message.add_reaction('❌')

# Run the bot
if __name__ == "__main__":
    bot = AshBot()
    
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")