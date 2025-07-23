"""
Enhanced False Positive & Negative Learning System - Discord Slash Commands
Replace: ash/bot/commands/false_positive_commands.py with this enhanced version
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

class EnhancedLearningCommands(commands.Cog):
    """Slash commands for reporting and learning from both false positives AND false negatives"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('CRISIS_RESPONSE_ROLE_ID', '0'))
        self.learning_data_file = './data/learning_data.json'
        self.nlp_client = getattr(bot, 'nlp_client', None)
        
        # Ensure learning data file exists
        self._ensure_learning_data_file()
        
        logger.info("🧠 Enhanced learning commands loaded (false positives + false negatives)")
    
    def _ensure_learning_data_file(self):
        """Create enhanced learning data file if it doesn't exist"""
        if not os.path.exists(self.learning_data_file):
            os.makedirs('./data', exist_ok=True)
            
            initial_data = {
                'false_positives': [],
                'false_negatives': [],  # NEW: Track missed crises
                'learning_patterns': {
                    'common_false_positive_phrases': [],
                    'missed_crisis_patterns': [],  # NEW: Patterns we missed
                    'context_indicators': [],
                    'sentiment_overrides': []
                },
                'statistics': {
                    'total_false_positives': 0,
                    'total_false_negatives': 0,  # NEW: Track missed crises
                    'false_positives_by_level': {'high': 0, 'medium': 0, 'low': 0},
                    'false_negatives_by_level': {'high': 0, 'medium': 0, 'low': 0},  # NEW
                    'patterns_learned': 0,
                    'last_analysis': None,
                    'detection_improvements': 0  # NEW: Track how many improvements made
                }
            }
            
            with open(self.learning_data_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
            
            logger.info(f"Created enhanced learning data file: {self.learning_data_file}")
    
    async def _check_crisis_role(self, interaction: discord.Interaction) -> bool:
        """Check if user has crisis response role"""
        try:
            user_role_ids = [role.id for role in interaction.user.roles]
            
            if self.crisis_response_role_id not in user_role_ids:
                await interaction.response.send_message(
                    "❌ You need the Crisis Response role to use learning commands", 
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
        """Report a false positive detection for learning (EXISTING - Enhanced)"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        # Validate that this is actually a false positive
        if detected_level == correct_level:
            await interaction.response.send_message(
                "❌ This isn't a false positive - detected and correct levels are the same",
                ephemeral=True
            )
            return
        
        # Validate that detected level is higher than correct (true false positive)
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        if level_hierarchy[detected_level] <= level_hierarchy[correct_level]:
            await interaction.response.send_message(
                "❌ This appears to be a false negative (missed crisis). Use `/report_missed_crisis` instead.",
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
            'type': 'false_positive',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reported_by': {
                'user_id': interaction.user.id,
                'username': interaction.user.display_name
            },
            'message_details': message_details,
            'detection_error': {
                'detected_level': detected_level,
                'correct_level': correct_level,
                'severity_score': self._calculate_false_positive_severity(detected_level, correct_level),
                'error_type': 'over_detection'
            },
            'context': context or "No additional context provided",
            'learning_status': 'pending'
        }
        
        # Save false positive
        self._save_learning_record(false_positive_record, 'false_positive')
        
        # Trigger immediate learning analysis
        learning_result = await self._trigger_learning_analysis(false_positive_record)
        
        # Create response embed
        embed = discord.Embed(
            title="✅ False Positive Reported",
            description="Thank you for reporting this over-detection. The system will learn to be less sensitive.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="📊 Over-Detection Error",
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
                value=f"**Patterns Learned:** {learning_result['patterns_discovered']}\n"
                      f"**Sensitivity Reduced:** {learning_result['confidence_adjustments']}\n"
                      f"**Status:** {learning_result['status']}",
                inline=True
            )
        
        embed.add_field(
            name="📈 Impact",
            value="This helps prevent similar over-reactions to non-crisis messages.",
            inline=False
        )
        
        embed.set_footer(text=f"Report ID: {false_positive_record['id']}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log the false positive report
        logger.warning(f"False positive reported by {interaction.user}: {detected_level} → {correct_level}")
        
        # Send learning update to NLP server if available
        if self.nlp_client:
            try:
                await self._send_learning_update_to_nlp(false_positive_record)
            except Exception as e:
                logger.error(f"Failed to send learning update to NLP server: {e}")
    
    @app_commands.command(name="report_missed_crisis", description="Report a crisis that was missed by detection")
    @app_commands.describe(
        message_link="Link to the Discord message that should have been flagged as a crisis",
        missed_level="What crisis level should have been detected",
        actual_detected="What level was actually detected (if any)",
        context="Additional context about why this was a crisis and why it was missed"
    )
    @app_commands.choices(
        missed_level=[
            app_commands.Choice(name="High Crisis", value="high"),
            app_commands.Choice(name="Medium Crisis", value="medium"),
            app_commands.Choice(name="Low Crisis", value="low")
        ],
        actual_detected=[
            app_commands.Choice(name="None (Not Flagged)", value="none"),
            app_commands.Choice(name="Low Crisis", value="low"),
            app_commands.Choice(name="Medium Crisis", value="medium")
        ]
    )
    async def report_missed_crisis(
        self, 
        interaction: discord.Interaction,
        message_link: str,
        missed_level: str,
        actual_detected: str = "none",
        context: str = None
    ):
        """NEW: Report a missed crisis (false negative) for learning"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        # Validate that this is actually a false negative
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        if level_hierarchy[missed_level] <= level_hierarchy[actual_detected]:
            await interaction.response.send_message(
                "❌ This doesn't appear to be a missed crisis. The detected level is equal or higher than expected.",
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
        
        # Create false negative record
        false_negative_record = {
            'id': f"fn_{int(datetime.now(timezone.utc).timestamp())}",
            'type': 'false_negative',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reported_by': {
                'user_id': interaction.user.id,
                'username': interaction.user.display_name
            },
            'message_details': message_details,
            'detection_error': {
                'should_detect_level': missed_level,
                'actually_detected': actual_detected,
                'severity_score': self._calculate_false_negative_severity(missed_level, actual_detected),
                'error_type': 'under_detection'
            },
            'context': context or "No additional context provided",
            'learning_status': 'pending'
        }
        
        # Save false negative
        self._save_learning_record(false_negative_record, 'false_negative')
        
        # Trigger immediate learning analysis
        learning_result = await self._trigger_learning_analysis(false_negative_record)
        
        # Create response embed
        embed = discord.Embed(
            title="🚨 Missed Crisis Reported",
            description="Thank you for reporting this missed detection. The system will learn to be more sensitive.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="📊 Under-Detection Error",
            value=f"**Should Detect:** {missed_level.title()} Crisis\n"
                  f"**Actually Detected:** {actual_detected.title() if actual_detected != 'none' else 'None'}\n"
                  f"**Severity:** {false_negative_record['detection_error']['severity_score']}/10",
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
                value=f"**New Crisis Patterns:** {learning_result['patterns_discovered']}\n"
                      f"**Sensitivity Increased:** {learning_result['confidence_adjustments']}\n"
                      f"**Status:** {learning_result['status']}",
                inline=True
            )
        
        embed.add_field(
            name="📈 Impact",
            value="This helps detect similar crisis patterns in the future.",
            inline=False
        )
        
        embed.set_footer(text=f"Report ID: {false_negative_record['id']}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log the false negative report
        logger.error(f"False negative (missed crisis) reported by {interaction.user}: {actual_detected} → {missed_level}")
        
        # Send learning update to NLP server if available
        if self.nlp_client:
            try:
                await self._send_learning_update_to_nlp(false_negative_record)
            except Exception as e:
                logger.error(f"Failed to send learning update to NLP server: {e}")
    
    @app_commands.command(name="learning_stats", description="View comprehensive learning statistics")
    async def learning_stats(self, interaction: discord.Interaction):
        """Enhanced statistics showing both false positives and false negatives"""
        
        if not await self._check_crisis_role(interaction):
            return
        
        try:
            with open(self.learning_data_file, 'r') as f:
                data = json.load(f)
            
            stats = data['statistics']
            false_positives = data['false_positives']
            false_negatives = data['false_negatives']
            
            # Calculate recent stats (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            
            recent_fps = [
                fp for fp in false_positives
                if datetime.fromisoformat(fp['timestamp'].replace('Z', '+00:00')) > thirty_days_ago
            ]
            
            recent_fns = [
                fn for fn in false_negatives
                if datetime.fromisoformat(fn['timestamp'].replace('Z', '+00:00')) > thirty_days_ago
            ]
            
            embed = discord.Embed(
                title="🧠 Comprehensive Learning Statistics",
                description="System learning from both over-detection and under-detection errors",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="📈 Overall Learning Progress",
                value=f"**False Positives:** {stats['total_false_positives']}\n"
                      f"**Missed Crises:** {stats['total_false_negatives']}\n"
                      f"**Total Reports:** {stats['total_false_positives'] + stats['total_false_negatives']}\n"
                      f"**Improvements Made:** {stats.get('detection_improvements', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="🚨 False Positives (Over-Detection)",
                value=f"**High:** {stats['false_positives_by_level']['high']}\n"
                      f"**Medium:** {stats['false_positives_by_level']['medium']}\n"
                      f"**Low:** {stats['false_positives_by_level']['low']}\n"
                      f"**Recent (30d):** {len(recent_fps)}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 False Negatives (Missed Crises)",
                value=f"**High:** {stats['false_negatives_by_level']['high']}\n"
                      f"**Medium:** {stats['false_negatives_by_level']['medium']}\n"
                      f"**Low:** {stats['false_negatives_by_level']['low']}\n"
                      f"**Recent (30d):** {len(recent_fns)}",
                inline=True
            )
            
            # Calculate learning effectiveness
            total_reports = len(recent_fps) + len(recent_fns)
            if total_reports > 0:
                fp_rate = len(recent_fps) / total_reports * 100
                fn_rate = len(recent_fns) / total_reports * 100
                
                embed.add_field(
                    name="📉 Recent Trends (30 Days)",
                    value=f"**Over-Detection Rate:** {fp_rate:.1f}%\n"
                          f"**Under-Detection Rate:** {fn_rate:.1f}%\n"
                          f"**Learning Rate:** {total_reports / 30:.1f} reports/day\n"
                          f"**Balance:** {'Over-sensitive' if fp_rate > fn_rate else 'Under-sensitive' if fn_rate > fp_rate else 'Balanced'}",
                    inline=True
                )
            
            # NLP server status
            nlp_status = "✅ Connected" if self.nlp_client else "❌ Disconnected"
            embed.add_field(
                name="🤖 Learning System Status",
                value=f"**NLP Server:** {nlp_status}\n"
                      f"**Real-time Learning:** {'Enabled' if self.nlp_client else 'Disabled'}\n"
                      f"**Last Analysis:** {stats.get('last_analysis', 'Never')[:10] if stats.get('last_analysis') else 'Never'}\n"
                      f"**Patterns Learned:** {stats.get('patterns_learned', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="💡 Most Common Issues",
                value=f"**False Positives:** {self._get_most_common_error_type(recent_fps, 'false_positive')}\n"
                      f"**Missed Crises:** {self._get_most_common_error_type(recent_fns, 'false_negative')}",
                inline=False
            )
            
            embed.set_footer(text="Use /report_false_positive and /report_missed_crisis to improve detection")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error getting learning stats: {e}")
            await interaction.response.send_message(
                "❌ Error retrieving learning statistics",
                ephemeral=True
            )
    
    # Helper methods
    
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
    
    def _calculate_false_positive_severity(self, detected_level: str, correct_level: str) -> int:
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
    
    def _calculate_false_negative_severity(self, should_detect: str, actually_detected: str) -> int:
        """Calculate severity score for false negative (1-10, higher = worse)"""
        level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        should_score = level_hierarchy.get(should_detect, 0)
        actual_score = level_hierarchy.get(actually_detected, 0)
        
        # Higher missed level = worse false negative
        difference = should_score - actual_score
        
        if difference == 3:  # None → High (completely missed high crisis)
            return 10
        elif difference == 2:  # Low → High or None → Medium
            return 7
        elif difference == 1:  # Any single level missed
            return 4
        else:
            return 1
    
    def _save_learning_record(self, record: Dict, record_type: str):
        """Save learning record to file"""
        try:
            with open(self.learning_data_file, 'r') as f:
                data = json.load(f)
            
            if record_type == 'false_positive':
                data['false_positives'].append(record)
                data['statistics']['total_false_positives'] += 1
                data['statistics']['false_positives_by_level'][record['detection_error']['detected_level']] += 1
            elif record_type == 'false_negative':
                data['false_negatives'].append(record)
                data['statistics']['total_false_negatives'] += 1
                data['statistics']['false_negatives_by_level'][record['detection_error']['should_detect_level']] += 1
            
            with open(self.learning_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {record_type} record: {record['id']}")
            
        except Exception as e:
            logger.error(f"Error saving {record_type}: {e}")
    
    async def _trigger_learning_analysis(self, record: Dict) -> Dict:
        """Trigger immediate learning analysis on the NLP server"""
        try:
            if not self.nlp_client:
                return {'status': 'no_nlp_server', 'patterns_discovered': 0, 'confidence_adjustments': 0}
            
            # Send to NLP server for pattern analysis
            nlp_host = os.getenv('NLP_SERVICE_HOST', '10.20.30.16')
            nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
            
            # Choose endpoint based on record type
            if record['type'] == 'false_positive':
                endpoint = "/analyze_false_positive"
                payload = {
                    'message': record['message_details']['content'],
                    'detected_level': record['detection_error']['detected_level'],
                    'correct_level': record['detection_error']['correct_level'],
                    'context': record['context'],
                    'severity_score': record['detection_error']['severity_score']
                }
            else:  # false_negative
                endpoint = "/analyze_false_negative"
                payload = {
                    'message': record['message_details']['content'],
                    'should_detect_level': record['detection_error']['should_detect_level'],
                    'actually_detected': record['detection_error']['actually_detected'],
                    'context': record['context'],
                    'severity_score': record['detection_error']['severity_score']
                }
            
            nlp_url = f"http://{nlp_host}:{nlp_port}{endpoint}"
            
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
                'learning_record_id': record['id'],
                'record_type': record['type'],
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
    
    def _get_most_common_error_type(self, records: List[Dict], error_type: str) -> str:
        """Get the most common type of error"""
        error_types = {}
        
        for record in records:
            if error_type == 'false_positive':
                detected = record['detection_error']['detected_level']
                correct = record['detection_error']['correct_level']
                error_key = f"{detected} → {correct}"
            else:  # false_negative
                should = record['detection_error']['should_detect_level']
                actual = record['detection_error']['actually_detected']
                error_key = f"{actual} → {should}"
            
            error_types[error_key] = error_types.get(error_key, 0) + 1
        
        if not error_types:
            return "None"
        
        most_common = max(error_types.items(), key=lambda x: x[1])
        return f"{most_common[0]} ({most_common[1]}x)"
    
    # Keep existing test_message_analysis command but enhance it
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
                level_hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
                
                embed.add_field(
                    name="✅ Expected vs Actual",
                    value=f"**Expected:** {expected_level.title()}\n"
                          f"**Actual:** {final_level.title()}\n"
                          f"**Match:** {'✅ Correct' if is_correct else '❌ Mismatch'}",
                    inline=True
                )
                
                if not is_correct:
                    if level_hierarchy[final_level] > level_hierarchy[expected_level]:
                        suggestion = "Consider using `/report_false_positive` if this over-detection is problematic."
                    else:
                        suggestion = "Consider using `/report_missed_crisis` if this under-detection is problematic."
                    
                    embed.add_field(
                        name="💡 Suggestion",
                        value=suggestion,
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
    """Setup function for the enhanced learning commands cog"""
    await bot.add_cog(EnhancedLearningCommands(bot))
    logger.info("✅ Enhanced learning commands cog loaded (false positives + false negatives)")