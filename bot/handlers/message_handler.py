"""
Message Handler - Processes incoming messages (your existing logic extracted)
Copy this to: ash/bot/handlers/message_handler.py
"""

import logging
import asyncio
import time
from discord import Message

logger = logging.getLogger(__name__)

class MessageHandler:
    """Handles message processing using your existing logic"""
    
    def __init__(self, bot, detection_service, config):
        self.bot = bot
        self.detection_service = detection_service
        self.config = config
        
        # Your existing conversation tracking (extracted from main.py)
        self.active_conversations = {}
        self.conversation_timeout = 300  # 5 minutes
        
        # Your existing rate limiting (extracted from main.py)
        self.user_cooldowns = {}
        self.daily_call_count = 0
        self.max_daily_calls = config.get_int('MAX_DAILY_CALLS', 1000)
        self.rate_limit_per_user = config.get_int('RATE_LIMIT_PER_USER', 10)
        
        self.guild_id = config.get_int('GUILD_ID')
        
        logger.info("📨 Message handler initialized with your existing logic")
    
    async def handle_message(self, message: Message):
        """Main message handling - your existing on_message logic"""
        
        # Your existing early filters
        if not self._should_process_message(message):
            return
        
        # Clean up expired conversations (your existing logic)
        self.cleanup_expired_conversations()
        
        # Check if user is in conversation (your existing logic)
        user_id = message.author.id
        if user_id in self.active_conversations:
            await self._handle_conversation_followup(message)
            return
        
        # Check for crisis indicators (your existing logic)
        await self._handle_potential_crisis(message)
    
    def _should_process_message(self, message: Message) -> bool:
        """Your existing message filtering logic"""
        if message.author.bot:
            return False
        
        if not message.guild or message.guild.id != self.guild_id:
            return False
        
        if not self.config.is_channel_allowed(message.channel.id):
            return False
        
        return True
    
    async def _handle_potential_crisis(self, message: Message):
        """Your existing crisis detection and response logic"""
        try:
            # Your existing rate limiting check
            if not await self.check_rate_limits(message.author.id):
                return
            
            if self.daily_call_count >= self.max_daily_calls:
                logger.warning("Daily API call limit reached")
                return
            
            # Use detection service (your existing hybrid_crisis_detection logic)
            detection_result = await self.detection_service.detect_crisis(message)
            
            if detection_result['needs_response']:
                await self._handle_crisis_response(message, detection_result)
        
        except Exception as e:
            logger.error(f"Error handling potential crisis: {e}")
            await message.add_reaction('❌')
    
    async def _handle_crisis_response(self, message: Message, detection_result: dict):
        """Your existing crisis response logic"""
        try:
            async with message.channel.typing():
                # Get response using detection service
                response = await self.detection_service.get_crisis_response(message, detection_result)
                
                # Your existing crisis handling logic
                crisis_level = detection_result['crisis_level']
                
                if crisis_level == 'high':
                    await self._handle_high_crisis(message, response)
                elif crisis_level == 'medium':
                    await self._handle_medium_crisis(message, response)
                else:
                    await message.reply(response)
                
                # Your existing conversation tracking
                self.start_conversation_tracking(message.author.id, crisis_level, message.channel.id)
                
                # Update counters
                self.daily_call_count += 1
                await self.record_api_call(message.author.id)
                
                logger.info(f"Responded to {message.author} - Crisis level: {crisis_level}")
        
        except Exception as e:
            logger.error(f"Error handling crisis response: {e}")
            await message.add_reaction('❌')
    
    async def _handle_conversation_followup(self, message: Message):
        """Your existing conversation follow-up logic"""
        user_id = message.author.id
        conversation = self.active_conversations[user_id]
        
        # Only respond in same channel
        if message.channel.id != conversation['channel_id']:
            return
        
        # Check for escalation (your existing logic)
        detection_result = await self.detection_service.detect_crisis(message)
        new_level = detection_result.get('crisis_level', 'none')
        current_level = conversation['crisis_level']
        
        if self._is_escalation(current_level, new_level):
            conversation['crisis_level'] = new_level
            logger.warning(f"Crisis escalated from {current_level} to {new_level} for user {user_id}")
            effective_level = new_level
        else:
            effective_level = current_level
        
        # Rate limiting for follow-ups
        if not await self.check_rate_limits(user_id):
            return
        
        if self.daily_call_count >= self.max_daily_calls:
            return
        
        # Generate response
        try:
            async with message.channel.typing():
                response = await self.detection_service.get_crisis_response(
                    message, {'crisis_level': effective_level}
                )
                
                # Handle escalated responses
                if new_level == 'high' and current_level != 'high':
                    await self._handle_high_crisis(message, response)
                elif new_level == 'medium' and current_level == 'low':
                    await self._handle_medium_crisis(message, response)
                else:
                    await message.reply(response)
                
                self.daily_call_count += 1
                await self.record_api_call(user_id)
                
                logger.info(f"Follow-up response to {message.author} (crisis: {effective_level})")
        
        except Exception as e:
            logger.error(f"Error handling conversation follow-up: {e}")
            await message.add_reaction('❌')
    
    # Your existing utility methods (extracted from main.py)
    
    def _is_escalation(self, current_level: str, new_level: str) -> bool:
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        return hierarchy.get(new_level, 0) > hierarchy.get(current_level, 0)
    
    async def check_rate_limits(self, user_id):
        """Your existing rate limiting logic"""
        current_time = asyncio.get_event_loop().time()
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        # Remove old timestamps
        self.user_cooldowns[user_id] = [
            timestamp for timestamp in self.user_cooldowns[user_id]
            if current_time - timestamp < 3600
        ]
        
        if len(self.user_cooldowns[user_id]) >= self.rate_limit_per_user:
            return False
        
        return True
    
    async def record_api_call(self, user_id):
        """Your existing API call recording"""
        current_time = asyncio.get_event_loop().time()
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        self.user_cooldowns[user_id].append(current_time)
    
    def start_conversation_tracking(self, user_id, crisis_level, channel_id):
        """Your existing conversation tracking"""
        self.active_conversations[user_id] = {
            'start_time': time.time(),
            'crisis_level': crisis_level,
            'channel_id': channel_id
        }
        logger.info(f"Started conversation tracking for user {user_id} (crisis: {crisis_level})")
    
    def cleanup_expired_conversations(self):
        """Your existing cleanup logic"""
        current_time = time.time()
        expired_users = []
        
        for user_id, conv_data in self.active_conversations.items():
            if current_time - conv_data['start_time'] > self.conversation_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.active_conversations[user_id]
            logger.debug(f"Conversation tracking expired for user {user_id}")
    
    # Crisis handling methods - now delegate to crisis handler
    async def _handle_high_crisis(self, message, response):
        """Handle high crisis using crisis handler"""
        if hasattr(self.bot, 'crisis_handler'):
            await self.bot.crisis_handler.handle_high_crisis(message, response)
        else:
            # Fallback if crisis handler not initialized yet
            await message.reply(response)
            logger.warning(f"🚨 HIGH CRISIS: {message.author} - crisis handler not available")
    
    async def _handle_medium_crisis(self, message, response):
        """Handle medium crisis using crisis handler"""
        if hasattr(self.bot, 'crisis_handler'):
            await self.bot.crisis_handler.handle_medium_crisis(message, response)
        else:
            # Fallback if crisis handler not initialized yet
            await message.reply(response)
            logger.info(f"⚠️ MEDIUM CRISIS: {message.author} - crisis handler not available")