"""
Enhanced Message Handler - Extract and enhance your existing message processing logic
Copy this to: ash/bot/handlers/message_handler.py
"""

import logging
import asyncio
import time
from discord import Message
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MessageHandler:
    """Enhanced message processing with your existing logic + improvements"""
    
    def __init__(self, bot, claude_api, nlp_client, keyword_detector, crisis_handler, config):
        self.bot = bot
        self.claude_api = claude_api
        self.nlp_client = nlp_client
        self.keyword_detector = keyword_detector
        self.crisis_handler = crisis_handler
        self.config = config
        
        # Your existing conversation tracking (enhanced)
        self.active_conversations = {}
        self.conversation_timeout = 300  # 5 minutes
        
        # Your existing rate limiting (enhanced)
        self.user_cooldowns = {}
        self.daily_call_count = 0
        self.max_daily_calls = config.get_int('MAX_DAILY_CALLS', 1000)
        self.rate_limit_per_user = config.get_int('RATE_LIMIT_PER_USER', 10)
        
        # Enhanced statistics
        self.message_stats = {
            'total_messages_processed': 0,
            'crisis_responses_given': 0,
            'conversations_started': 0,
            'follow_ups_handled': 0,
            'rate_limits_hit': 0,
            'daily_limits_hit': 0,
            'detection_method_breakdown': {
                'keyword_only': 0,
                'nlp_primary': 0,
                'hybrid_detection': 0
            }
        }
        
        self.guild_id = config.get_int('GUILD_ID')
        
        logger.info("📨 Enhanced message handler initialized")
        logger.info(f"   🎯 Guild ID: {self.guild_id}")
        logger.info(f"   📊 Rate limits: {self.rate_limit_per_user}/hour per user, {self.max_daily_calls}/day total")
        logger.info(f"   💬 Conversation timeout: {self.conversation_timeout}s")
    
    async def handle_message(self, message: Message):
        """Enhanced main message handling with comprehensive logging"""
        
        self.message_stats['total_messages_processed'] += 1
        
        # Your existing early filters (enhanced)
        if not self._should_process_message(message):
            return
        
        # Clean up expired conversations (your existing logic)
        self.cleanup_expired_conversations()
        
        # Check if user is in conversation (your existing logic enhanced)
        user_id = message.author.id
        if user_id in self.active_conversations:
            await self._handle_conversation_followup(message)
            return
        
        # Check for crisis indicators (your existing logic enhanced)
        await self._handle_potential_crisis(message)
    
    def _should_process_message(self, message: Message) -> bool:
        """Enhanced message filtering with detailed logging"""
        
        # Your existing filters
        if message.author.bot:
            logger.debug(f"🤖 Ignored bot message from {message.author}")
            return False
        
        if not message.guild or message.guild.id != self.guild_id:
            logger.debug(f"🚫 Ignored message from wrong guild: {message.guild.id if message.guild else 'DM'}")
            return False
        
        if not self.config.is_channel_allowed(message.channel.id):
            logger.debug(f"🚫 Ignored message from restricted channel: {message.channel.id}")
            return False
        
        # Enhanced logging for processed messages
        logger.debug(f"📨 Processing message from {message.author} in {message.channel}: {message.content[:50]}...")
        return True
    
    async def _handle_potential_crisis(self, message: Message):
        """Enhanced crisis detection with hybrid approach and comprehensive logging"""
        
        try:
            # Your existing rate limiting check (enhanced)
            if not await self.check_rate_limits(message.author.id):
                self.message_stats['rate_limits_hit'] += 1
                logger.debug(f"🚫 Rate limit hit for user {message.author.id}")
                return
            
            if self.daily_call_count >= self.max_daily_calls:
                self.message_stats['daily_limits_hit'] += 1
                logger.warning("🚫 Daily API call limit reached")
                return
            
            # Enhanced hybrid detection (your existing logic improved)
            detection_result = await self._perform_hybrid_detection(message)
            
            if detection_result['needs_response']:
                await self._handle_crisis_response(message, detection_result)
        
        except Exception as e:
            logger.error(f"❌ Error handling potential crisis: {e}")
            await message.add_reaction('❌')
    
    async def _perform_hybrid_detection(self, message: Message) -> Dict:
        """Enhanced hybrid detection with your existing logic"""
        
        # Method 1: Your existing keyword detection (always runs)
        keyword_result = self.keyword_detector.check_message(message.content)
        
        # Method 2: Your existing NLP analysis (if available)
        nlp_result = None
        try:
            nlp_result = await self.nlp_client.analyze_message(
                message.content,
                str(message.author.id),
                str(message.channel.id)
            )
        except Exception as e:
            logger.debug(f"NLP analysis failed (non-critical): {e}")
        
        # Your existing hybrid decision logic (enhanced)
        final_result = self._combine_detection_results(keyword_result, nlp_result)
        
        # Enhanced logging
        self._log_detection_decision(message, keyword_result, nlp_result, final_result)
        
        # Update statistics
        method = final_result.get('method', 'unknown')
        if method in self.message_stats['detection_method_breakdown']:
            self.message_stats['detection_method_breakdown'][method] += 1
        
        return final_result
    
    def _combine_detection_results(self, keyword_result: Dict, nlp_result: Optional[Dict]) -> Dict:
        """Your existing hybrid decision logic with enhanced statistics"""
        
        # If NLP unavailable, use keywords only
        if not nlp_result:
            self.message_stats['detection_method_breakdown']['keyword_only'] += 1
            return {
                'needs_response': keyword_result['needs_response'],
                'crisis_level': keyword_result['crisis_level'],
                'method': 'keyword_only',
                'confidence': 0.9 if keyword_result['needs_response'] else 0.0,
                'detected_categories': keyword_result['detected_categories']
            }
        
        # Both methods available - your existing hybrid logic
        keyword_level = keyword_result['crisis_level']
        nlp_level = nlp_result.get('crisis_level', 'none')
        
        # Crisis level hierarchy
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        # Use the higher of the two crisis levels (safety-first)
        if hierarchy[keyword_level] >= hierarchy[nlp_level]:
            final_level = keyword_level
            method = 'keyword_primary'
            confidence = 0.9 if keyword_result['needs_response'] else 0.0
        else:
            final_level = nlp_level
            method = 'nlp_primary'
            confidence = nlp_result.get('confidence_score', 0.5)
        
        self.message_stats['detection_method_breakdown']['hybrid_detection'] += 1
        
        return {
            'needs_response': final_level != 'none',
            'crisis_level': final_level,
            'method': method,
            'confidence': confidence,
            'detected_categories': keyword_result['detected_categories'] + nlp_result.get('detected_categories', []),
            'keyword_result': keyword_level,
            'nlp_result': nlp_level
        }
    
    async def _handle_crisis_response(self, message: Message, detection_result: dict):
        """Enhanced crisis response with comprehensive logging and error handling"""
        
        try:
            async with message.channel.typing():
                # Get response using your existing Claude API
                crisis_level = detection_result['crisis_level']
                response = await self.claude_api.get_ash_response(
                    message.content,
                    crisis_level,
                    message.author.display_name
                )
                
                # Use enhanced crisis handler
                await self.crisis_handler.handle_crisis_response(message, crisis_level, response)
                
                # Your existing conversation tracking (enhanced)
                self.start_conversation_tracking(message.author.id, crisis_level, message.channel.id)
                
                # Update counters
                self.daily_call_count += 1
                await self.record_api_call(message.author.id)
                self.message_stats['crisis_responses_given'] += 1
                
                # Enhanced logging
                logger.info(f"✅ Crisis response completed:")
                logger.info(f"   👤 User: {message.author} ({message.author.id})")
                logger.info(f"   🚨 Level: {crisis_level}")
                logger.info(f"   🔍 Method: {detection_result.get('method', 'unknown')}")
                logger.info(f"   📊 Confidence: {detection_result.get('confidence', 0):.2f}")
                logger.info(f"   📈 Total responses today: {self.message_stats['crisis_responses_given']}")
        
        except Exception as e:
            logger.error(f"❌ Error handling crisis response: {e}")
            await message.add_reaction('❌')
    
    async def _handle_conversation_followup(self, message: Message):
        """Enhanced conversation follow-up with escalation detection"""
        
        user_id = message.author.id
        conversation = self.active_conversations[user_id]
        
        # Only respond in same channel
        if message.channel.id != conversation['channel_id']:
            return
        
        self.message_stats['follow_ups_handled'] += 1
        
        try:
            # Check for escalation (your existing logic enhanced)
            detection_result = await self._perform_hybrid_detection(message)
            new_level = detection_result.get('crisis_level', 'none')
            current_level = conversation['crisis_level']
            
            if self._is_escalation(current_level, new_level):
                conversation['crisis_level'] = new_level
                conversation['escalations'] = conversation.get('escalations', 0) + 1
                logger.warning(f"🚨 Crisis ESCALATED: {current_level} → {new_level} for user {user_id}")
                effective_level = new_level
            else:
                effective_level = current_level
            
            # Rate limiting for follow-ups
            if not await self.check_rate_limits(user_id):
                self.message_stats['rate_limits_hit'] += 1
                return
            
            if self.daily_call_count >= self.max_daily_calls:
                self.message_stats['daily_limits_hit'] += 1
                return
            
            # Generate response
            async with message.channel.typing():
                response = await self.claude_api.get_ash_response(
                    message.content,
                    effective_level,
                    message.author.display_name
                )
                
                # Handle escalated responses using crisis handler
                await self.crisis_handler.handle_crisis_response(message, effective_level, response)
                
                self.daily_call_count += 1
                await self.record_api_call(user_id)
                
                # Update conversation stats
                conversation['follow_up_count'] = conversation.get('follow_up_count', 0) + 1
                
                logger.info(f"✅ Follow-up response: {message.author} (crisis: {effective_level}, follow-up #{conversation['follow_up_count']})")
        
        except Exception as e:
            logger.error(f"❌ Error handling conversation follow-up: {e}")
            await message.add_reaction('❌')
    
    # Your existing utility methods (enhanced)
    
    def _is_escalation(self, current_level: str, new_level: str) -> bool:
        """Check if crisis level has escalated"""
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        return hierarchy.get(new_level, 0) > hierarchy.get(current_level, 0)
    
    async def check_rate_limits(self, user_id: int) -> bool:
        """Enhanced rate limiting with better tracking"""
        current_time = asyncio.get_event_loop().time()
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        # Remove old timestamps
        self.user_cooldowns[user_id] = [
            timestamp for timestamp in self.user_cooldowns[user_id]
            if current_time - timestamp < 3600
        ]
        
        if len(self.user_cooldowns[user_id]) >= self.rate_limit_per_user:
            logger.debug(f"🚫 Rate limit exceeded for user {user_id}: {len(self.user_cooldowns[user_id])}/{self.rate_limit_per_user}")
            return False
        
        return True
    
    async def record_api_call(self, user_id: int):
        """Enhanced API call recording"""
        current_time = asyncio.get_event_loop().time()
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        self.user_cooldowns[user_id].append(current_time)
        
        logger.debug(f"📊 API call recorded: user {user_id} ({len(self.user_cooldowns[user_id])}/{self.rate_limit_per_user}) daily: {self.daily_call_count}/{self.max_daily_calls}")
    
    def start_conversation_tracking(self, user_id: int, crisis_level: str, channel_id: int):
        """Enhanced conversation tracking with more details"""
        self.active_conversations[user_id] = {
            'start_time': time.time(),
            'crisis_level': crisis_level,
            'channel_id': channel_id,
            'follow_up_count': 0,
            'escalations': 0,
            'initial_crisis_level': crisis_level
        }
        
        self.message_stats['conversations_started'] += 1
        logger.info(f"💬 Started enhanced conversation tracking:")
        logger.info(f"   👤 User: {user_id}")
        logger.info(f"   🚨 Crisis level: {crisis_level}")
        logger.info(f"   📍 Channel: {channel_id}")
        logger.info(f"   📊 Total conversations today: {self.message_stats['conversations_started']}")
    
    def cleanup_expired_conversations(self):
        """Enhanced conversation cleanup with detailed logging"""
        current_time = time.time()
        expired_users = []
        
        for user_id, conv_data in self.active_conversations.items():
            if current_time - conv_data['start_time'] > self.conversation_timeout:
                expired_users.append(user_id)
        
        # Enhanced cleanup logging
        for user_id in expired_users:
            conv = self.active_conversations[user_id]
            duration = current_time - conv['start_time']
            
            logger.info(f"💬 Conversation expired for user {user_id}:")
            logger.info(f"   ⏱️ Duration: {duration:.1f}s")
            logger.info(f"   💬 Follow-ups: {conv.get('follow_up_count', 0)}")
            logger.info(f"   🚨 Escalations: {conv.get('escalations', 0)}")
            logger.info(f"   📈 Level progression: {conv.get('initial_crisis_level', 'unknown')} → {conv['crisis_level']}")
            
            del self.active_conversations[user_id]
    
    def _log_detection_decision(self, message: Message, keyword_result: Dict, 
                              nlp_result: Optional[Dict], final_result: Dict):
        """Enhanced detection decision logging"""
        
        message_preview = message.content[:30] + "..." if len(message.content) > 30 else message.content
        
        if nlp_result:
            logger.info(f"🔍 Hybrid Detection Results:")
            logger.info(f"   📝 Message: '{message_preview}'")
            logger.info(f"   🔤 Keywords: {keyword_result['crisis_level']}")
            logger.info(f"   🧠 NLP: {nlp_result.get('crisis_level', 'none')} (conf: {nlp_result.get('confidence_score', 0):.2f})")
            logger.info(f"   ⚖️ Final: {final_result['crisis_level']} (method: {final_result['method']})")
        else:
            logger.info(f"🔍 Keyword-Only Detection:")
            logger.info(f"   📝 Message: '{message_preview}'")
            logger.info(f"   🔤 Result: {final_result['crisis_level']} (NLP unavailable)")
    
    def get_message_handler_stats(self) -> dict:
        """Get comprehensive message handler statistics"""
        
        # Calculate active conversations stats
        active_convs = len(self.active_conversations)
        total_follow_ups = sum(conv.get('follow_up_count', 0) for conv in self.active_conversations.values())
        total_escalations = sum(conv.get('escalations', 0) for conv in self.active_conversations.values())
        
        # Calculate success rates
        total_rate_limit_checks = self.message_stats['crisis_responses_given'] + self.message_stats['rate_limits_hit']
        rate_limit_success_rate = 0 if total_rate_limit_checks == 0 else ((total_rate_limit_checks - self.message_stats['rate_limits_hit']) / total_rate_limit_checks) * 100
        
        return {
            'component': 'EnhancedMessageHandler',
            'message_processing': self.message_stats,
            'conversation_tracking': {
                'active_conversations': active_convs,
                'conversation_timeout_seconds': self.conversation_timeout,
                'total_follow_ups_active': total_follow_ups,
                'total_escalations_active': total_escalations
            },
            'rate_limiting': {
                'rate_limit_per_user': self.rate_limit_per_user,
                'max_daily_calls': self.max_daily_calls,
                'current_daily_calls': self.daily_call_count,
                'success_rate_percent': round(rate_limit_success_rate, 2),
                'active_users_tracked': len(self.user_cooldowns)
            },
            'detection_breakdown': self.message_stats['detection_method_breakdown']
        }
    
    async def get_user_conversation_status(self, user_id: int) -> Optional[Dict]:
        """Get detailed conversation status for a specific user"""
        
        if user_id not in self.active_conversations:
            return None
        
        conv = self.active_conversations[user_id]
        current_time = time.time()
        duration = current_time - conv['start_time']
        time_remaining = max(0, self.conversation_timeout - duration)
        
        return {
            'user_id': user_id,
            'active': True,
            'crisis_level': conv['crisis_level'],
            'initial_crisis_level': conv.get('initial_crisis_level', 'unknown'),
            'channel_id': conv['channel_id'],
            'duration_seconds': round(duration, 1),
            'time_remaining_seconds': round(time_remaining, 1),
            'follow_up_count': conv.get('follow_up_count', 0),
            'escalations': conv.get('escalations', 0),
            'is_expired': time_remaining <= 0
        }