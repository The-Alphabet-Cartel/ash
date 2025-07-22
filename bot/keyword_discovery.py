# ash/bot/keyword_discovery.py
"""
Keyword Discovery Integration for Ash Bot
Integrates with NLP server to discover new crisis keywords automatically
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import os
from keyword_detector import KeywordDetector
from claude_api import ClaudeAPI

logger = logging.getLogger(__name__)

class KeywordDiscoveryService:
    """Discovers new crisis keywords using the NLP server"""
    
    def __init__(self, keyword_detector: KeywordDetector):
        self.keyword_detector = keyword_detector
        self.nlp_host = os.getenv('NLP_SERVICE_HOST', '192.168.1.100')
        self.nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
        self.nlp_url = f"http://{self.nlp_host}:{self.nlp_port}"
        
        # Discovery settings
        self.min_confidence = float(os.getenv('DISCOVERY_MIN_CONFIDENCE', '0.6'))
        self.max_daily_discoveries = int(os.getenv('MAX_DAILY_DISCOVERIES', '10'))
        self.discovery_enabled = os.getenv('ENABLE_KEYWORD_DISCOVERY', 'true').lower() == 'true'
        
        # Tracking
        self.daily_discovery_count = 0
        self.last_discovery_date = None
        self.discovered_keywords = set()
        
        logger.info(f"🔍 Keyword Discovery Service initialized: {self.nlp_url}")
        logger.info(f"📊 Min confidence: {self.min_confidence}, Max daily: {self.max_daily_discoveries}")
    
    async def analyze_missed_crisis(self, message: str, user_id: str, channel_id: str) -> Optional[Dict]:
        """
        Analyze a message that might be a missed crisis for keyword discovery
        Called when human intervention suggests we missed something
        """
        if not self.discovery_enabled:
            return None
            
        try:
            # Call NLP server for phrase extraction
            async with aiohttp.ClientSession() as session:
                payload = {
                    "message": message,
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "parameters": {
                        "min_phrase_length": 2,
                        "max_phrase_length": 5,
                        "crisis_focus": True,
                        "community_specific": True,
                        "min_confidence": self.min_confidence
                    }
                }
                
                # Set longer timeout for manual discovery (user expects delay)
                timeout = aiohttp.ClientTimeout(total=10.0)
                async with session.post(f"{self.nlp_url}/extract_phrases", json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_extracted_phrases(data, message)
                    else:
                        logger.warning(f"NLP server error {response.status} for phrase extraction")
                        return None
                        
        except asyncio.TimeoutError:
            logger.warning("NLP phrase extraction timed out (manual discovery)")
            return None
        except Exception as e:
            logger.error(f"Error in missed crisis analysis: {e}")
            return None
    
    async def analyze_for_background_learning(self, message: str, user_id: str, channel_id: str, crisis_level: str):
        """
        BACKGROUND ANALYSIS - Does not block real-time responses
        Analyzes messages that triggered responses to learn patterns
        """
        if not self.discovery_enabled:
            return
        
        try:
            # Very short timeout - if NLP server is slow, skip silently
            async with aiohttp.ClientSession() as session:
                payload = {
                    "message": message,
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "parameters": {
                        "min_phrase_length": 2,
                        "max_phrase_length": 4,  # Shorter phrases for background
                        "crisis_focus": True,
                        "community_specific": True,
                        "min_confidence": max(0.7, self.min_confidence)  # Higher threshold for background
                    }
                }
                
                # Very short timeout for background analysis
                timeout = aiohttp.ClientTimeout(total=3.0)
                async with session.post(f"{self.nlp_url}/extract_phrases", json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = await self._process_extracted_phrases(data, message)
                        
                        if result and result.get('discovered_keywords'):
                            # Only log high-confidence background discoveries
                            high_conf_keywords = [
                                kw for kw in result['discovered_keywords'] 
                                if kw.get('confidence', 0) > 0.75
                            ]
                            if high_conf_keywords:
                                logger.info(f"🔍 Background discovery found {len(high_conf_keywords)} high-confidence keywords")
                                
                                # Add to pending suggestions with background flag
                                for kw in high_conf_keywords:
                                    kw['source'] = 'background_learning'
                                    kw['background'] = True
                                
                                return result
                    else:
                        # Don't log errors for background analysis - NLP server might be busy
                        return None
                        
        except asyncio.TimeoutError:
            # Expected - NLP server taking too long, skip silently
            logger.debug("Background discovery skipped - NLP server timeout")
            return None
        except Exception as e:
            # Log but don't fail
            logger.debug(f"Background discovery error (non-critical): {e}")
            return None
    
    async def discover_from_conversation_batch(self, messages: List[Dict]) -> List[Dict]:
        """
        Analyze a batch of recent conversations to discover patterns
        Called periodically (daily) to learn from community usage
        """
        if not self.discovery_enabled or not messages:
            return []
            
        try:
            # Reset daily counter if new day
            self._reset_daily_counter_if_needed()
            
            if self.daily_discovery_count >= self.max_daily_discoveries:
                logger.info("Daily discovery limit reached")
                return []
            
            # Prepare batch for pattern learning
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": messages,
                    "analysis_type": "community_crisis_patterns",
                    "time_window_days": 7
                }
                
                async with session.post(f"{self.nlp_url}/learn_patterns", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_learned_patterns(data)
                    else:
                        logger.warning(f"NLP server error {response.status} for pattern learning")
                        return []
                        
        except Exception as e:
            logger.error(f"Error in batch discovery: {e}")
            return []
    
    async def semantic_analysis_discovery(self, message: str, context_hints: List[str]) -> Optional[Dict]:
        """
        Use semantic analysis to discover contextual crisis patterns
        Called when regular detection is uncertain
        """
        if not self.discovery_enabled:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "message": message,
                    "community_vocabulary": [
                        "trans", "gay", "lesbian", "bi", "queer", "dysphoria", 
                        "transition", "coming out", "family rejection", "internalized",
                        "chosen family", "pride", "closeted", "misgendered"
                    ],
                    "context_hints": context_hints
                }
                
                async with session.post(f"{self.nlp_url}/semantic_analysis", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return await self._process_semantic_analysis(data, message)
                    else:
                        logger.warning(f"NLP server error {response.status} for semantic analysis")
                        return None
                        
        except Exception as e:
            logger.error(f"Error in semantic discovery: {e}")
            return None
    
    async def _process_extracted_phrases(self, extraction_data: Dict, original_message: str) -> Dict:
        """Process phrases extracted from NLP server"""
        phrases = extraction_data.get('phrases', [])
        
        discovered_keywords = []
        for phrase_data in phrases:
            phrase_text = phrase_data.get('text', '').strip()
            crisis_level = phrase_data.get('crisis_level', 'low')
            confidence = phrase_data.get('confidence', 0.0)
            
            # Skip if already discovered or exists
            if (phrase_text in self.discovered_keywords or 
                self._keyword_already_exists(phrase_text)):
                continue
                
            # Skip if confidence too low
            if confidence < self.min_confidence:
                continue
                
            # Add to discoveries
            discovered_keywords.append({
                'keyword': phrase_text,
                'crisis_level': crisis_level,
                'confidence': confidence,
                'source': 'phrase_extraction',
                'original_message': original_message[:100] + "...",
                'reasoning': phrase_data.get('reasoning', 'NLP model analysis'),
                'discovered_at': datetime.now().isoformat()
            })
            
            self.discovered_keywords.add(phrase_text)
            self.daily_discovery_count += 1
            
            if self.daily_discovery_count >= self.max_daily_discoveries:
                break
        
        logger.info(f"🔍 Discovered {len(discovered_keywords)} new keywords from phrase extraction")
        return {
            'discovered_keywords': discovered_keywords,
            'extraction_stats': {
                'total_phrases': len(phrases),
                'high_confidence': len([p for p in phrases if p.get('confidence', 0) > 0.7]),
                'processing_time': extraction_data.get('processing_time_ms', 0)
            }
        }
    
    async def _process_learned_patterns(self, pattern_data: Dict) -> List[Dict]:
        """Process patterns learned from batch analysis"""
        # This would be implemented when pattern_learner.py is completed
        # For now, return empty list
        logger.info("Pattern learning processing not yet implemented")
        return []
    
    async def _process_semantic_analysis(self, semantic_data: Dict, original_message: str) -> Dict:
        """Process semantic analysis results"""
        # This would be implemented when semantic_analyzer.py is completed
        # For now, return basic structure
        logger.info("Semantic analysis processing not yet implemented")
        return {'discovered_keywords': []}
    
    def _keyword_already_exists(self, keyword: str) -> bool:
        """Check if keyword already exists in current detection system"""
        # Check built-in keywords
        from keywords import get_all_crisis_keywords
        all_keywords = get_all_crisis_keywords()
        
        for crisis_level, categories in all_keywords.items():
            for category, keywords in categories.items():
                if keyword.lower() in [kw.lower() for kw in keywords]:
                    return True
        
        # Check custom keywords (would need to load from data/custom_keywords.json)
        try:
            with open('./data/custom_keywords.json', 'r') as f:
                custom_keywords = json.load(f)
                for level_data in custom_keywords.values():
                    for category_keywords in level_data.values():
                        if keyword.lower() in [kw.lower() for kw in category_keywords]:
                            return True
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # No custom keywords file yet
            
        return False
    
    def _reset_daily_counter_if_needed(self):
        """Reset daily counter if it's a new day"""
        today = datetime.now().date()
        if self.last_discovery_date != today:
            self.daily_discovery_count = 0
            self.last_discovery_date = today
            logger.info(f"🔄 Reset daily discovery counter for {today}")
    
    async def get_discovery_stats(self) -> Dict:
        """Get keyword discovery statistics"""
        return {
            'discovery_enabled': self.discovery_enabled,
            'daily_discoveries': self.daily_discovery_count,
            'max_daily': self.max_daily_discoveries,
            'min_confidence': self.min_confidence,
            'total_discovered_today': len(self.discovered_keywords),
            'nlp_server': f"{self.nlp_host}:{self.nlp_port}",
            'last_discovery_date': self.last_discovery_date.isoformat() if self.last_discovery_date else None
        }


class KeywordDiscoveryManager:
    """Manages the integration between bot and keyword discovery"""
    
    def __init__(self, bot):
        self.bot = bot
        self.discovery_service = KeywordDiscoveryService(bot.keyword_detector)
        self.pending_suggestions = []  # Keywords waiting for team review
        
        # Background task management
        self.background_tasks = set()  # Track background tasks
        self.max_background_tasks = 5  # Limit concurrent background analysis
        
    async def on_crisis_response_given(self, message, response_type: str, human_responded: bool = False):
        """
        Called after Ash responds to a crisis - ASYNC background learning
        """
        # If there are manual interventions, prioritize those for immediate analysis
        if human_responded and response_type in ['medium', 'high']:
            # Manual intervention - run immediately (user tolerates delay)
            discovery_result = await self.discovery_service.analyze_missed_crisis(
                message.content, 
                str(message.author.id), 
                str(message.channel.id)
            )
            
            if discovery_result and discovery_result.get('discovered_keywords'):
                await self._handle_urgent_discoveries(discovery_result['discovered_keywords'], message.channel)
        else:
            # Regular bot response - queue background analysis (don't block)
            await self._queue_background_analysis(message, response_type)
    
    async def _queue_background_analysis(self, message, crisis_level: str):
        """Queue background analysis without blocking real-time responses"""
        
        # Limit concurrent background tasks
        if len(self.background_tasks) >= self.max_background_tasks:
            logger.debug("Skipping background analysis - too many concurrent tasks")
            return
        
        # Create background task
        task = asyncio.create_task(
            self._run_background_analysis(message, crisis_level)
        )
        
        # Track the task
        self.background_tasks.add(task)
        
        # Clean up when done
        task.add_done_callback(self.background_tasks.discard)
    
    async def _run_background_analysis(self, message, crisis_level: str):
        """Run background analysis in separate task"""
        try:
            discovery_result = await self.discovery_service.analyze_for_background_learning(
                message.content,
                str(message.author.id), 
                str(message.channel.id),
                crisis_level
            )
            
            if discovery_result and discovery_result.get('discovered_keywords'):
                await self._handle_background_discoveries(discovery_result['discovered_keywords'])
                
        except Exception as e:
            # Background errors shouldn't affect bot operation
            logger.debug(f"Background analysis error (non-critical): {e}")
    
    async def _handle_background_discoveries(self, keywords: List[Dict]):
        """Handle keywords discovered in background analysis"""
        # Only keep high-confidence background discoveries
        high_confidence_keywords = [
            kw for kw in keywords 
            if kw.get('confidence', 0) > 0.75
        ]
        
        if high_confidence_keywords:
            # Add to pending suggestions silently
            for keyword in high_confidence_keywords:
                keyword['source'] = 'background_learning'
                keyword['priority'] = 'low'  # Background discoveries are lower priority
                
            self.pending_suggestions.extend(high_confidence_keywords)
            
            # Only notify if we found multiple high-confidence keywords
            if len(high_confidence_keywords) >= 3:
                await self._send_background_discovery_notification(high_confidence_keywords)
    
    async def _send_background_discovery_notification(self, keywords: List[Dict]):
        """Send low-priority notification for background discoveries"""
        crisis_channel = self.bot.get_channel(self.bot.crisis_response_channel_id)
        if not crisis_channel:
            return
            
        import discord
        embed = discord.Embed(
            title="🔍 Background Learning Update",
            description=f"Discovered {len(keywords)} potential keywords from recent conversations",
            color=discord.Color.blue()
        )
        
        keyword_preview = [kw['keyword'] for kw in keywords[:3]]
        embed.add_field(
            name="Sample Keywords",
            value=", ".join(f"`{kw}`" for kw in keyword_preview),
            inline=False
        )
        
        embed.add_field(
            name="Review",
            value="Use `/discovery_suggestions` to review all pending keywords",
            inline=False
        )
        
        # Send as low-priority message (no ping)
        await crisis_channel.send(embed=embed)
        logger.info(f"📢 Sent background discovery notification: {len(keywords)} keywords")
    
    async def on_manual_crisis_intervention(self, message, crisis_level: str):
        """
        Called when crisis team manually intervenes on a message Ash missed
        This is a strong signal for keyword discovery
        """
        logger.warning(f"🚨 Manual intervention on missed crisis: {crisis_level}")
        
        discovery_result = await self.discovery_service.analyze_missed_crisis(
            message.content,
            str(message.author.id), 
            str(message.channel.id)
        )
        
        if discovery_result and discovery_result.get('discovered_keywords'):
            # High priority - these are confirmed misses
            await self._handle_urgent_discoveries(discovery_result['discovered_keywords'], message.channel)
    
    async def daily_pattern_discovery(self):
        """
        Run daily pattern discovery from recent conversations
        Called by a scheduled task
        """
        try:
            # Collect recent messages that triggered responses
            recent_messages = await self._collect_recent_crisis_messages()
            
            if recent_messages:
                discoveries = await self.discovery_service.discover_from_conversation_batch(recent_messages)
                
                if discoveries:
                    # Send to crisis response channel for review
                    crisis_channel = self.bot.get_channel(self.bot.crisis_response_channel_id)
                    if crisis_channel:
                        await self._send_daily_discovery_report(crisis_channel, discoveries)
                        
        except Exception as e:
            logger.error(f"Error in daily pattern discovery: {e}")
    
    async def _handle_new_discoveries(self, keywords: List[Dict], channel):
        """Handle new keyword discoveries"""
        self.pending_suggestions.extend(keywords)
        
        # If enough keywords or high confidence, notify team
        high_confidence_keywords = [kw for kw in keywords if kw['confidence'] > 0.8]
        
        if high_confidence_keywords:
            await self._notify_team_of_discoveries(high_confidence_keywords, channel, urgency='normal')
    
    async def _handle_urgent_discoveries(self, keywords: List[Dict], channel):
        """Handle urgent keyword discoveries from manual interventions"""
        # Add urgent flag
        for keyword in keywords:
            keyword['urgent'] = True
            keyword['source'] = 'manual_intervention'
        
        self.pending_suggestions.extend(keywords)
        await self._notify_team_of_discoveries(keywords, channel, urgency='high')
    
    async def _notify_team_of_discoveries(self, keywords: List[Dict], channel, urgency: str = 'normal'):
        """Notify crisis response team of new keyword discoveries"""
        crisis_channel = self.bot.get_channel(self.bot.crisis_response_channel_id)
        if not crisis_channel:
            return
            
        emoji = "🚨" if urgency == 'high' else "🔍"
        title = "Urgent Keyword Discovery" if urgency == 'high' else "New Keywords Discovered"
        
        import discord
        embed = discord.Embed(
            title=f"{emoji} {title}",
            description=f"NLP analysis suggests {len(keywords)} new crisis keywords",
            color=discord.Color.red() if urgency == 'high' else discord.Color.blue()
        )
        
        for i, keyword in enumerate(keywords[:5]):  # Show first 5
            embed.add_field(
                name=f"Keyword {i+1}: '{keyword['keyword']}'",
                value=f"Level: {keyword['crisis_level'].title()}\n"
                     f"Confidence: {keyword['confidence']:.2f}\n"
                     f"Source: {keyword['source']}",
                inline=True
            )
        
        if len(keywords) > 5:
            embed.add_field(
                name="Additional Keywords",
                value=f"...and {len(keywords) - 5} more keywords discovered",
                inline=False
            )
        
        embed.add_field(
            name="Review Actions",
            value="Use `/add_keyword` to add promising keywords\n"
                 "Use `/keyword_stats` to see current counts",
            inline=False
        )
        
        # Ping crisis response team for urgent discoveries
        if urgency == 'high' and self.bot.crisis_response_role_id:
            await crisis_channel.send(f"<@&{self.bot.crisis_response_role_id}>", embed=embed)
        else:
            await crisis_channel.send(embed=embed)
        
        logger.info(f"📢 Notified team of {len(keywords)} discovered keywords ({urgency} priority)")
    
    async def _collect_recent_crisis_messages(self) -> List[Dict]:
        """Collect recent messages that triggered crisis responses"""
        # This would collect from bot's conversation history
        # For now, return empty list - would need to implement conversation logging
        return []
    
    async def _send_daily_discovery_report(self, channel, discoveries: List[Dict]):
        """Send daily discovery report to crisis team"""
        if not discoveries:
            return
            
        import discord
        embed = discord.Embed(
            title="📊 Daily Keyword Discovery Report",
            description=f"Analysis of community patterns found {len(discoveries)} potential keywords",
            color=discord.Color.green()
        )
        
        # Group by crisis level
        by_level = {}
        for discovery in discoveries:
            level = discovery.get('crisis_level', 'unknown')
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(discovery)
        
        for level, keywords in by_level.items():
            keyword_list = [f"• {kw['keyword']} (conf: {kw['confidence']:.2f})" for kw in keywords[:3]]
            if len(keywords) > 3:
                keyword_list.append(f"• ...and {len(keywords) - 3} more")
                
            embed.add_field(
                name=f"{level.title()} Crisis Keywords ({len(keywords)})",
                value="\n".join(keyword_list),
                inline=True
            )
        
        await channel.send(embed=embed)


# Integration with main bot
async def integrate_keyword_discovery(bot):
    """Add keyword discovery to the main bot"""
    bot.keyword_discovery = KeywordDiscoveryManager(bot)
    
    # Add to existing message handler
    original_handle_support = bot.handle_support_message
    
    async def enhanced_handle_support_message(message, keyword_result):
        # Call original handler
        await original_handle_support(message, keyword_result)
        
        # Add discovery tracking
        await bot.keyword_discovery.on_crisis_response_given(
            message, 
            keyword_result['crisis_level'],
            human_responded=False  # Would track if human also responded
        )
    
    # Replace handler
    bot.handle_support_message = enhanced_handle_support_message
    
    logger.info("✅ Keyword discovery integration complete")