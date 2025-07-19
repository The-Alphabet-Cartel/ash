import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv
from keyword_detector import KeywordDetector
from claude_api import ClaudeAPI
from ash_character import ASH_CHARACTER_PROMPT

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/ash.log'),
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
        self.guild_id = int(os.getenv('GUILD_ID'))
        self.resources_channel_id = int(os.getenv('RESOURCES_CHANNEL_ID'))
        self.staff_ping_user = os.getenv('STAFF_PING_USER')
        
        # Rate limiting
        self.user_cooldowns = {}
        self.daily_call_count = 0
        self.max_daily_calls = int(os.getenv('MAX_DAILY_CALLS', 1000))
        
    async def on_ready(self):
        logger.info(f'{self.user} has awakened in The Alphabet Cartel')
        guild = discord.utils.get(self.guilds, id=self.guild_id)
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
        else:
            logger.error(f'Could not find guild with ID: {self.guild_id}')

    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
            
        # Only respond in the configured guild
        if not message.guild or message.guild.id != self.guild_id:
            return
            
        # Check for keywords that indicate need for support
        keyword_result = self.keyword_detector.check_message(message.content)
        
        if keyword_result['needs_response']:
            await self.handle_support_message(message, keyword_result)
            
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
                else:
                    await message.reply(response)
                    
                self.daily_call_count += 1
                logger.info(f"Responded to {message.author} - Crisis level: {keyword_result['crisis_level']}")
                
        except Exception as e:
            logger.error(f"Error handling support message: {e}")
            await message.add_reaction('❌')
    
    async def handle_crisis_escalation(self, message, ash_response):
        """Handle high-crisis situations with staff notification"""
        
        # Send Ash's response
        await message.reply(ash_response)
        
        # Ping resources channel and staff
        resources_channel = self.get_channel(self.resources_channel_id)
        if resources_channel:
            staff_mention = f"<@{self.staff_ping_user}>" if self.staff_ping_user else "@Staff"
            
            embed = discord.Embed(
                title="🚨 Crisis Support Needed",
                description=f"High-crisis keywords detected in <#{message.channel.id}>",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Message Link", value=f"[Jump to message]({message.jump_url})", inline=False)
            
            await resources_channel.send(f"{staff_mention}", embed=embed)
            
        logger.warning(f"Crisis escalation triggered for {message.author} in {message.channel}")
    
    async def check_rate_limits(self, user_id):
        """Check if user is within rate limits"""
        current_time = asyncio.get_event_loop().time()
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

# Run the bot
if __name__ == "__main__":
    bot = AshBot()
    
    try:
        bot.run(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")