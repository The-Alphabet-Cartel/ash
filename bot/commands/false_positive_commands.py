"""
False Positive Learning System - Discord Slash Commands
Create as: ash/bot/commands/false_positive_commands.py
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

class FalsePositiveLearningCommands(commands.Cog):
    """Slash commands for reporting and learning from false positives"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('CRISIS_RESPONSE_ROLE_ID', '0'))
        self.false_positives_file = './data/false_positives.json'
        self.nlp_client = getattr(bot, 'nlp_client', None)
        
        # Ensure false positives file exists
        self._ensure_false_positives_file()
        
        logger.info("🔍 False positive learning commands loaded")
    
    def _ensure_false_positives_file(self):
        """Create false positives file if it doesn't exist"""
        if not os.path.exists(self.false_positives_file):
            os.makedirs('./data', exist_ok=True)
            
            initial_data = {
                'false_positives': [],
                'learning_patterns': {
                    'common_phrases': [],
                    'context_indicators': [],
                    'sentiment_overrides': []
                },
                'statistics': {
                    'total_reported': 0,
                    'by_crisis_level': {'high': 0, 'medium': 0, 'low': 0},
                    'patterns_learned': 0,
                    'last_analysis': None
                }
            }
            
            with open(self.false_positives_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
            
            logger.info(f"Created false positives file: {self.false_positives_file}")
    
    async def _check_crisis_role(self, interaction: discord.Interaction) -> bool:
        """Check if user has crisis response role"""
        try:
            user_role_ids = [role.id for role in interaction.user.roles]
            
            if self.crisis_response_role_id not in user_role_ids:
                await interaction.response.send_message(
                    "❌ You need the Crisis Response role to use false positive commands", 
                    ephemeral=True
                )
                return False
            return True
            
        except Exception as e:
            logger.error(f"Role check error: {e}")
            await interaction.response.send_message(
                "❌ Error checking permissions", 
                ephemeral=True
            )
            return False
    
    @app_commands.command(name="report_false_positive", description="Report a false positive crisis detection")
    @app_commands.describe(
        message_link="Link to the Discord message that was incorrectly flagged",
        detected_level="What crisis level was incorrectly detected",
        correct_level="What the correct crisis level should have been",
        context="Additional context about why this was a false positive"
    )
    @app_commands.choices(
        detected_level=[
            app_commands.Choice(name="High Crisis", value="high"),
            app_commands.Choice(name="Medium Crisis", value="medium"),
            app_commands.Choice(name="Low Crisis", value="low")
        ],
        correct_level=[
            app_commands.Choice(name="None (No Crisis)", value="none"),
            app_commands.Choice(name="Low Crisis", value="low"),
            app_commands.Choice(name="Medium Crisis", value="medium")
        ]
    )
    async def report_false_positive(
        self, 
        interaction: discord.Interaction,
        message_link: str,
        detected_level: str,
        correct_level: str,
        context: str = None
    ):
        """Report a false positive detection for learning"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        # Validate that this is actually a false positive
        if detected_level == correct_level:
            await interaction.response.send_message(
                "❌ This isn't a false positive - detected and correct levels are the same",
                ephemeral=True
            )
            return
        
        # Extract message details from link
        try:
            message_details = await self._extract_message_from_link(message_link)
            if not message_details:
                await interaction.response.send_message(
                    "❌ Could not extract message from link. Please ensure it's a valid Discord message link",
                    ephemeral=True
                )
                return
        except Exception as e:
            logger.error(f"Error extracting message: {e}")
            await interaction.response.send_message(
                "❌ Error processing message link",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Create false positive record
        false_positive_record = {
            'id': f"fp_{int(datetime.now(timezone.utc).timestamp())}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reported_by': {
                'user_id': interaction.user.id,
                'username': interaction.user.display_name
            },
            'message_details': message_details,
            'detection_error': {
                'detected_level': detected_level,
                'correct_level': correct_level,
                'severity_score': self._calculate_severity_score(detected_level, correct_level)
            },
            'context': context or "No additional context provided",
            'learning_status': 'pending'
        }
        
        # Save false positive
        self._save_false_positive(false_positive_record)
        
        # Trigger immediate learning analysis
        learning_result = await self._trigger_learning_analysis(false_positive_record)
        
        # Create response embed
        embed = discord.Embed(
            title="✅ False Positive Reported",
            description="Thank you for reporting this detection error. The system will learn from this.",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Detection Error",
            value=f"**Detected:** {detected_level.title()} Crisis\n"
                  f"**Should be:** {correct_level.title() if correct_level != 'none' else 'None'}\n"
                  f"**Severity:** {false_positive_record['detection_error']['severity_score']}/10",
            inline=True
        )
        
        embed.add_field(
            name="📝 Message Preview",
            value=f"```{message_details['content'][:100]}{'...' if len(message_details['content']) > 100 else ''}```",
            inline=False
        )
        
        if learning_result['patterns_discovered'] > 0:
            embed.add_field(
                name="🧠 Learning Results",
                value=f"**New Patterns:** {learning_result['patterns_discovered']}\n"
                      f"**Confidence Adjustments:** {learning_result['confidence_adjustments']}\n"
                      f"**Status:** {learning_result['status']}",
                inline=True
            )
        
        embed.add_field(
            name="📈 Impact",
            value="This report helps improve detection accuracy for similar messages in the future.",
            inline=False
        )
        
        embed.set_footer(text=f"Report ID: {false_positive_record['id']}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log the false positive report
        logger.warning(f"False positive reported by {interaction.user}: {detected_level} → {correct_level}")
        
        # Send learning notification to NLP server if available
        if self.nlp_client:
            try:
                await self._send_learning_update_to_nlp(false_positive_record)
            except Exception as e:
                logger.error(f"Failed to send learning update to NLP server: {e}")
    
    async def _extract_message_from_link(self, message_link: str) -> Optional[Dict]:
        """Extract message content and details from Discord message link"""
        try:
            # Parse Discord message link format:
            # https://discord.com/channels/GUILD_ID/CHANNEL_ID/MESSAGE_ID
            parts = message_link.split('/')
            if len(parts) < 7 or 'discord.com' not in message_link:
                return None
            
            guild_id = int(parts[-3])
            channel_id = int(parts[-2])
            message_id = int(parts[-1])
            
            # Get the message
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return None
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return None
            
            message = await channel.fetch_message(message_id)
            if not message:
                return None
            
            return {
                'content': message.content,
                'author_id': message.author.id,
                'author_name': message.author.display_name,
                'channel_id': channel_id,
                'guild_id': guild_id,
                'message_id': message_id,
                'timestamp': message.created_at.isoformat(),
                'link': message_link
            }
            
        except Exception as e:
            logger.error(f"Error extracting message from link: {e}")
            return None
    
    def _calculate_severity_score(self, detected_level: str, correct_level: str) -> int:
        """Calculate severity score for false positive (1-10, higher = worse)"""
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        detected_score = level_hierarchy.get(detected_level, 0)
        correct_score = level_hierarchy.get(correct_level, 0)
        
        # Higher difference = worse false positive
        difference = detected_score - correct_score
        
        if difference == 3:  # High → None
            return 10
        elif difference == 2:  # High → Low or Medium → None
            return 7
        elif difference == 1:  # Any single level difference
            return 4
        else:
            return 1
    
    def _save_false_positive(self, record: Dict):
        """Save false positive record to file"""
        try:
            with open(self.false_positives_file, 'r') as f:
                data = json.load(f)
            
            data['false_positives'].append(record)
            data['statistics']['total_reported'] += 1
            data['statistics']['by_crisis_level'][record['detection_error']['detected_level']] += 1
            
            with open(self.false_positives_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved false positive record: {record['id']}")
            
        except Exception as e:
            logger.error(f"Error saving false positive: {e}")
    
    async def _trigger_learning_analysis(self, record: Dict) -> Dict:
        """Trigger immediate learning analysis on the NLP server"""
        try:
            if not self.nlp_client:
                return {'status': 'no_nlp_server', 'patterns_discovered': 0, 'confidence_adjustments': 0}
            
            # Send to NLP server for pattern analysis
            nlp_host = os.getenv('NLP_SERVICE_HOST', '10.20.30.16')
            nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
            nlp_url = f"http://{nlp_host}:{nlp_port}/analyze_false_positive"
            
            payload = {
                'message': record['message_details']['content'],
                'detected_level': record['detection_error']['detected_level'],
                'correct_level': record['detection_error']['correct_level'],
                'context': record['context'],
                'severity_score': record['detection_error']['severity_score']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(nlp_url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'status': 'success',
                            'patterns_discovered': result.get('patterns_discovered', 0),
                            'confidence_adjustments': result.get('confidence_adjustments', 0),
                            'learning_applied': result.get('learning_applied', False)
                        }
                    else:
                        logger.warning(f"NLP learning analysis failed: {response.status}")
                        return {'status': 'nlp_error', 'patterns_discovered': 0, 'confidence_adjustments': 0}
        
        except Exception as e:
            logger.error(f"Error in learning analysis: {e}")
            return {'status': 'error', 'patterns_discovered': 0, 'confidence_adjustments': 0}
    
    async def _send_learning_update_to_nlp(self, record: Dict):
        """Send learning update to NLP server for model adjustment"""
        try:
            nlp_host = os.getenv('NLP_SERVICE_HOST', '10.20.30.16')
            nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
            nlp_url = f"http://{nlp_host}:{nlp_port}/update_learning_model"
            
            payload = {
                'false_positive_id': record['id'],
                'message_data': record['message_details'],
                'correction_data': record['detection_error'],
                'context_data': record['context'],
                'timestamp': record['timestamp']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(nlp_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent learning update to NLP server")
                    else:
                        logger.warning(f"NLP learning update failed: {response.status}")
        
        except Exception as e:
            logger.error(f"Error sending learning update to NLP: {e}")
    
    @app_commands.command(name="false_positive_stats", description="View false positive statistics and learning progress")
    async def false_positive_stats(self, interaction: discord.Interaction):
        """View false positive statistics"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            with open(self.false_positives_file, 'r') as f:
                data = json.load(f)
            
            stats = data['statistics']
            false_positives = data['false_positives']
            
            # Calculate recent stats (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            recent_fps = [
                fp for fp in false_positives
                if datetime.fromisoformat(fp['timestamp'].replace('Z', '+00:00')) > thirty_days_ago
            ]
            
            embed = discord.Embed(
                title="📊 False Positive Learning Statistics",
                description="System learning progress from reported detection errors",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📈 Overall Statistics",
                value=f"**Total Reported:** {stats['total_reported']}\n"
                      f"**Patterns Learned:** {stats.get('patterns_learned', 0)}\n"
                      f"**Last 30 Days:** {len(recent_fps)}",
                inline=True
            )
            
            embed.add_field(
                name="🚨 By Crisis Level",
                value=f"**High:** {stats['by_crisis_level']['high']}\n"
                      f"**Medium:** {stats['by_crisis_level']['medium']}\n"
                      f"**Low:** {stats['by_crisis_level']['low']}",
                inline=True
            )
            
            if recent_fps:
                # Calculate severity distribution
                severity_scores = [fp['detection_error']['severity_score'] for fp in recent_fps]
                avg_severity = sum(severity_scores) / len(severity_scores)
                
                embed.add_field(
                    name="📉 Recent Trends (30 Days)",
                    value=f"**Average Severity:** {avg_severity:.1f}/10\n"
                          f"**Most Common:** {self._get_most_common_error_type(recent_fps)}\n"
                          f"**Learning Rate:** {len(recent_fps) / 30:.1f} per day",
                    inline=True
                )
            
            # NLP server status
            nlp_status = "✅ Connected" if self.nlp_client else "❌ Disconnected"
            embed.add_field(
                name="🤖 Learning System",
                value=f"**NLP Server:** {nlp_status}\n"
                      f"**Real-time Learning:** {'Enabled' if self.nlp_client else 'Disabled'}\n"
                      f"**Last Analysis:** {stats.get('last_analysis', 'Never')[:10] if stats.get('last_analysis') else 'Never'}",
                inline=False
            )
            
            embed.set_footer(text="Use /report_false_positive to help improve detection accuracy")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error getting false positive stats: {e}")
            await interaction.response.send_message(
                "❌ Error retrieving statistics",
                ephemeral=True
            )
    
    def _get_most_common_error_type(self, false_positives: List[Dict]) -> str:
        """Get the most common type of false positive error"""
        error_types = {}
        
        for fp in false_positives:
            detected = fp['detection_error']['detected_level']
            correct = fp['detection_error']['correct_level']
            error_type = f"{detected} → {correct}"
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if not error_types:
            return "None"
        
        most_common = max(error_types.items(), key=lambda x: x[1])
        return f"{most_common[0]} ({most_common[1]}x)"
    
    @app_commands.command(name="test_message_analysis", description="Test how a message would be analyzed by current system")
    @app_commands.describe(
        test_message="Message text to analyze",
        expected_level="What crisis level you expect this should be"
    )
    @app_commands.choices(
        expected_level=[
            app_commands.Choice(name="None (No Crisis)", value="none"),
            app_commands.Choice(name="Low Crisis", value="low"),
            app_commands.Choice(name="Medium Crisis", value="medium"),
            app_commands.Choice(name="High Crisis", value="high")
        ]
    )
    async def test_message_analysis(
        self,
        interaction: discord.Interaction,
        test_message: str,
        expected_level: str = None
    ):
        """Test message analysis against current detection system"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Test with keyword detector
            keyword_result = self.bot.keyword_detector.check_message(test_message)
            
            # Test with NLP if available
            nlp_result = None
            if self.nlp_client:
                try:
                    nlp_result = await self.nlp_client.analyze_message(
                        test_message,
                        str(interaction.user.id),
                        str(interaction.channel.id)
                    )
                except Exception as e:
                    logger.error(f"NLP analysis error: {e}")
            
            # Create analysis embed
            embed = discord.Embed(
                title="🔍 Message Analysis Test",
                description="Current system analysis of the test message",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="📝 Test Message",
                value=f"```{test_message[:200]}{'...' if len(test_message) > 200 else ''}```",
                inline=False
            )
            
            embed.add_field(
                name="🔤 Keyword Detection",
                value=f"**Level:** {keyword_result['crisis_level'].title()}\n"
                      f"**Triggered:** {'Yes' if keyword_result['needs_response'] else 'No'}\n"
                      f"**Categories:** {', '.join(keyword_result['detected_categories']) if keyword_result['detected_categories'] else 'None'}",
                inline=True
            )
            
            if nlp_result:
                embed.add_field(
                    name="🧠 NLP Analysis",
                    value=f"**Level:** {nlp_result['crisis_level'].title()}\n"
                          f"**Confidence:** {nlp_result['confidence_score']:.2f}\n"
                          f"**Method:** {nlp_result.get('method', 'unknown')}",
                    inline=True
                )
                
                # Determine final result (using hybrid logic)
                final_level = self._determine_hybrid_result(keyword_result, nlp_result)
            else:
                embed.add_field(
                    name="🧠 NLP Analysis",
                    value="❌ NLP Server unavailable",
                    inline=True
                )
                final_level = keyword_result['crisis_level']
            
            embed.add_field(
                name="⚖️ Final Decision",
                value=f"**Crisis Level:** {final_level.title()}\n"
                      f"**Would Trigger Response:** {'Yes' if final_level != 'none' else 'No'}",
                inline=False
            )
            
            if expected_level:
                is_correct = final_level == expected_level
                embed.add_field(
                    name="✅ Expected vs Actual",
                    value=f"**Expected:** {expected_level.title()}\n"
                          f"**Actual:** {final_level.title()}\n"
                          f"**Match:** {'✅ Correct' if is_correct else '❌ Mismatch'}",
                    inline=True
                )
                
                if not is_correct:
                    embed.add_field(
                        name="💡 Suggestion",
                        value="If this is incorrect, consider using `/report_false_positive` on a real message to help the system learn.",
                        inline=False
                    )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in test analysis: {e}")
            await interaction.followup.send(
                "❌ Error performing analysis test",
                ephemeral=True
            )
    
    def _determine_hybrid_result(self, keyword_result: Dict, nlp_result: Dict) -> str:
        """Determine final result using hybrid logic (matches your existing logic)"""
        keyword_level = keyword_result['crisis_level']
        nlp_level = nlp_result.get('crisis_level', 'none')
        
        # Crisis level hierarchy
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        # Use the higher of the two crisis levels (safety-first)
        if hierarchy[keyword_level] >= hierarchy[nlp_level]:
            return keyword_level
        else:
            return nlp_level

async def setup(bot):
    """Setup function for the false positive learning commands cog"""
    await bot.add_cog(FalsePositiveLearningCommands(bot))
    logger.info("✅ False positive learning commands cog loaded")