"""
Enhanced Crisis Handler - Extract and enhance your existing crisis escalation logic
Copy this to: ash/bot/handlers/crisis_handler.py
"""

import logging
import discord
from discord import Message

logger = logging.getLogger(__name__)

class CrisisHandler:
    """Enhanced crisis escalation handler with your existing alert logic"""
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        
        # Your existing configuration
        self.resources_channel_id = config.get_int('RESOURCES_CHANNEL_ID')
        self.crisis_response_channel_id = config.get_int('CRISIS_RESPONSE_CHANNEL_ID')
        self.crisis_response_role_id = config.get_int('CRISIS_RESPONSE_ROLE_ID')
        self.staff_ping_user_id = config.get_int('STAFF_PING_USER')
        
        # Enhanced statistics tracking
        self.crisis_stats = {
            'high_crisis_count': 0,
            'medium_crisis_count': 0,
            'low_crisis_count': 0,
            'staff_dms_sent': 0,
            'team_alerts_sent': 0,
            'escalation_errors': 0
        }
        
        logger.info(f"🚨 Enhanced crisis handler initialized")
        logger.info(f"   📧 Staff DM user: {self.staff_ping_user_id}")
        logger.info(f"   📢 Crisis channel: {self.crisis_response_channel_id}")
        logger.info(f"   👥 Crisis role: {self.crisis_response_role_id}")
    
    async def handle_crisis_response(self, message: Message, crisis_level: str, ash_response: str):
        """
        Enhanced crisis response dispatcher
        Routes to appropriate handler based on crisis level
        """
        
        # Update statistics
        self.crisis_stats[f'{crisis_level}_crisis_count'] += 1
        
        # Route to appropriate handler
        if crisis_level == 'high':
            await self.handle_high_crisis(message, ash_response)
        elif crisis_level == 'medium':
            await self.handle_medium_crisis(message, ash_response)
        else:  # low
            await self.handle_low_crisis(message, ash_response)
    
    async def handle_high_crisis(self, message: Message, ash_response: str):
        """
        Enhanced high crisis handling with full escalation
        - Send Ash's response
        - DM staff member directly  
        - Alert crisis team with role ping
        - Log comprehensive details
        """
        
        logger.warning(f"🚨 HIGH CRISIS detected for {message.author} in {message.channel}")
        
        try:
            # Send Ash's response first
            await message.reply(ash_response)
            
            # Send staff DM (your existing logic enhanced)
            dm_success = await self._send_staff_dm(message, "HIGH")
            
            # Alert crisis response team (your existing logic enhanced)
            alert_success = await self._send_crisis_team_alert(message, "HIGH")
            
            # Enhanced logging
            logger.warning(f"✅ High crisis escalation completed for {message.author}:")
            logger.warning(f"   📧 Staff DM: {'✅ Sent' if dm_success else '❌ Failed'}")
            logger.warning(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.warning(f"   📊 Total high crises today: {self.crisis_stats['high_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in high crisis handling: {e}")
    
    async def handle_medium_crisis(self, message: Message, ash_response: str):
        """
        Enhanced medium crisis handling with team notification
        - Send Ash's response
        - Alert crisis team (no staff DM)
        - Enhanced monitoring logs
        """
        
        logger.info(f"⚠️ MEDIUM CRISIS detected for {message.author} in {message.channel}")
        
        try:
            # Send Ash's response
            await message.reply(ash_response)
            
            # Alert crisis response team (no staff DM for medium)
            alert_success = await self._send_crisis_team_alert(message, "MEDIUM")
            
            # Enhanced logging
            logger.info(f"✅ Medium crisis handling completed for {message.author}:")
            logger.info(f"   📢 Team Alert: {'✅ Sent' if alert_success else '❌ Failed'}")
            logger.info(f"   📊 Total medium crises today: {self.crisis_stats['medium_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in medium crisis handling: {e}")
    
    async def handle_low_crisis(self, message: Message, ash_response: str):
        """
        Enhanced low crisis handling - supportive response only
        - Send Ash's response
        - Log for monitoring trends
        """
        
        logger.info(f"ℹ️ LOW CRISIS support for {message.author} in {message.channel}")
        
        try:
            # Send Ash's response
            await message.reply(ash_response)
            
            # Enhanced logging for trend analysis
            logger.info(f"✅ Low crisis support provided to {message.author}")
            logger.info(f"   📊 Total low crisis responses today: {self.crisis_stats['low_crisis_count']}")
            
        except Exception as e:
            self.crisis_stats['escalation_errors'] += 1
            logger.error(f"❌ Error in low crisis handling: {e}")
    
    async def _send_staff_dm(self, message: Message, crisis_level: str) -> bool:
        """Enhanced staff DM with better error handling and formatting"""
        
        try:
            staff_user = await self.bot.fetch_user(self.staff_ping_user_id)
            
            # Enhanced embed with more details
            embed = discord.Embed(
                title="🚨 Crisis Support Needed - URGENT",
                description="High-crisis keywords detected requiring immediate attention",
                color=discord.Color.red(),
                timestamp=message.created_at
            )
            
            # User information
            embed.add_field(
                name="👤 User Details", 
                value=f"**Name:** {message.author.display_name}\n"
                     f"**Mention:** {message.author.mention}\n"
                     f"**ID:** {message.author.id}", 
                inline=True
            )
            
            # Location information
            embed.add_field(
                name="📍 Location", 
                value=f"**Channel:** {message.channel.mention}\n"
                     f"**Server:** {message.guild.name}\n"
                     f"**Channel ID:** {message.channel.id}", 
                inline=True
            )
            
            # Crisis information
            embed.add_field(
                name="🚨 Crisis Info", 
                value=f"**Level:** {crisis_level}\n"
                     f"**Time:** {message.created_at.strftime('%H:%M:%S')}\n"
                     f"**Method:** Keyword Detection", 
                inline=True
            )
            
            # Message content (truncated if needed)
            message_content = message.content
            if len(message_content) > 1000:
                message_content = message_content[:1000] + "..."
            
            embed.add_field(
                name="💬 Original Message", 
                value=f"```{message_content}```", 
                inline=False
            )
            
            # Quick action links
            embed.add_field(
                name="🔗 Quick Actions", 
                value=f"[Jump to Message]({message.jump_url}) | "
                     f"[Resources Channel](<https://discord.com/channels/{message.guild.id}/{self.resources_channel_id}>) | "
                     f"[Crisis Channel](<https://discord.com/channels/{message.guild.id}/{self.crisis_response_channel_id}>)", 
                inline=False
            )
            
            # Statistics footer
            embed.set_footer(
                text=f"High Crisis #{self.crisis_stats['high_crisis_count']} today | Ash v2.0 Modular"
            )
            
            await staff_user.send(embed=embed)
            
            self.crisis_stats['staff_dms_sent'] += 1
            logger.warning(f"📧 Enhanced crisis DM sent to staff for {message.author}")
            
            return True
            
        except discord.NotFound:
            logger.error(f"❌ Staff user ID {self.staff_ping_user_id} not found")
            return False
        except discord.Forbidden:
            logger.error(f"❌ Cannot send DM to staff user - DMs may be disabled")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending crisis DM to staff: {e}")
            return False
    
    async def _send_crisis_team_alert(self, message: Message, crisis_level: str) -> bool:
        """Enhanced crisis team alert with better formatting and context"""
        
        try:
            crisis_channel = self.bot.get_channel(self.crisis_response_channel_id)
            if not crisis_channel:
                logger.error(f"❌ Crisis response channel {self.crisis_response_channel_id} not found")
                return False
            
            # Enhanced embed based on crisis level
            if crisis_level == "HIGH":
                color = discord.Color.red()
                emoji = "🚨"
                title = "Crisis Response Team Alert"
                description = "**HIGH-PRIORITY:** Immediate team response required"
                action_text = "🎯 **ACTION NEEDED:** Direct intervention required"
                urgency_field = "**URGENT** - Respond immediately"
            else:  # MEDIUM
                color = discord.Color.orange()
                emoji = "⚠️"
                title = "Medium Crisis Alert"
                description = "**MEDIUM-PRIORITY:** Team awareness and monitoring needed"
                action_text = "👀 **MONITOR:** Watch for escalation"
                urgency_field = "**MODERATE** - Monitor and assess"
            
            embed = discord.Embed(
                title=f"{emoji} {title}",
                description=description,
                color=color,
                timestamp=message.created_at
            )
            
            # Location and user info
            embed.add_field(
                name="📍 Location & User", 
                value=f"**Channel:** {message.channel.mention}\n"
                     f"**User:** {message.author.mention} (`{message.author.display_name}`)\n"
                     f"**Server:** {message.guild.name}", 
                inline=True
            )
            
            # Crisis details
            embed.add_field(
                name="🚨 Crisis Details", 
                value=f"**Level:** {crisis_level}\n"
                     f"**Priority:** {urgency_field}\n"
                     f"**Detection:** Keyword System", 
                inline=True
            )
            
            # Quick stats
            total_today = self.crisis_stats['high_crisis_count'] + self.crisis_stats['medium_crisis_count']
            embed.add_field(
                name="📊 Today's Stats", 
                value=f"**Total Crises:** {total_today}\n"
                     f"**High:** {self.crisis_stats['high_crisis_count']}\n"
                     f"**Medium:** {self.crisis_stats['medium_crisis_count']}", 
                inline=True
            )
            
            # Action needed
            embed.add_field(
                name="🎯 Required Action", 
                value=action_text, 
                inline=False
            )
            
            # Quick links
            embed.add_field(
                name="🔗 Quick Access", 
                value=f"[Jump to Message]({message.jump_url}) | [Resources Channel](<https://discord.com/channels/{message.guild.id}/{self.resources_channel_id}>)", 
                inline=False
            )
            
            # Footer with helpful info
            embed.set_footer(
                text=f"Crisis #{total_today} today | Use /keyword_stats for detection info | Ash v2.0"
            )
            
            # Send with appropriate mention
            role_mention = f"<@&{self.crisis_response_role_id}>"
            
            # Add reaction buttons for quick response tracking
            sent_message = await crisis_channel.send(role_mention, embed=embed)
            
            # Add quick reaction options for team coordination
            await sent_message.add_reaction("👀")  # Monitoring
            await sent_message.add_reaction("🏃")  # Responding
            await sent_message.add_reaction("✅")  # Handled
            
            self.crisis_stats['team_alerts_sent'] += 1
            logger.info(f"📢 Enhanced {crisis_level} crisis team alert sent for {message.author}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending crisis team alert: {e}")
            return False
    
    def get_crisis_stats(self) -> dict:
        """Get comprehensive crisis handling statistics"""
        return {
            'component': 'EnhancedCrisisHandler',
            **self.crisis_stats,
            'success_rate': self._calculate_success_rate(),
            'configuration': {
                'staff_dm_enabled': self.staff_ping_user_id is not None,
                'team_alerts_enabled': self.crisis_response_channel_id is not None,
                'crisis_role_configured': self.crisis_response_role_id is not None
            }
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate escalation success rate"""
        total_attempts = (self.crisis_stats['staff_dms_sent'] + 
                         self.crisis_stats['team_alerts_sent'] + 
                         self.crisis_stats['escalation_errors'])
        
        if total_attempts == 0:
            return 100.0
        
        successful = self.crisis_stats['staff_dms_sent'] + self.crisis_stats['team_alerts_sent']
        return round((successful / total_attempts) * 100, 2)
    
    async def send_manual_intervention_log(self, message: Message, crisis_level: str, staff_member):
        """Enhanced manual intervention logging"""
        try:
            crisis_channel = self.bot.get_channel(self.crisis_response_channel_id)
            if not crisis_channel:
                return
            
            embed = discord.Embed(
                title="📝 Manual Crisis Intervention Logged",
                description="Staff member identified a crisis that automated detection missed",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="👤 Staff Member", 
                value=f"{staff_member.mention} (`{staff_member.display_name}`)", 
                inline=True
            )
            embed.add_field(
                name="🚨 Crisis Level Identified", 
                value=crisis_level.upper(), 
                inline=True
            )
            embed.add_field(
                name="🎯 Impact", 
                value="This helps improve Ash's detection accuracy", 
                inline=True
            )
            
            embed.add_field(
                name="📍 Message Location", 
                value=f"[Jump to original message]({message.jump_url})", 
                inline=False
            )
            
            embed.set_footer(text="Manual interventions help train better automated detection")
            
            await crisis_channel.send(embed=embed)
            logger.info(f"📝 Enhanced manual intervention logged: {staff_member} -> {crisis_level}")
            
        except Exception as e:
            logger.error(f"Error logging manual intervention: {e}")