"""
Crisis Handler - Your existing crisis escalation logic extracted
Copy this to: ash/bot/handlers/crisis_handler.py
"""

import logging
import discord
from discord import Message

logger = logging.getLogger(__name__)

class CrisisHandler:
    """Handles crisis escalation using your existing alert logic"""
    
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        
        # Your existing configuration
        self.resources_channel_id = config.get_int('RESOURCES_CHANNEL_ID')
        self.crisis_response_channel_id = config.get_int('CRISIS_RESPONSE_CHANNEL_ID')
        self.crisis_response_role_id = config.get_int('CRISIS_RESPONSE_ROLE_ID')
        self.staff_ping_user_id = config.get_int('STAFF_PING_USER')
        
        logger.info("🚨 Crisis handler initialized with your existing alert logic")
    
    async def handle_high_crisis(self, message: Message, ash_response: str):
        """
        Your existing handle_crisis_escalation logic
        """
        logger.warning(f"🚨 HIGH CRISIS detected for {message.author} in {message.channel}")
        
        # Send Ash's response first
        await message.reply(ash_response)
        
        # Send staff DM (your existing logic)
        await self._send_staff_dm(message)
        
        # Alert crisis response team (your existing logic)
        await self._send_crisis_team_alert(message, "HIGH")
        
        logger.warning(f"✅ Full high crisis escalation completed for {message.author}")
    
    async def handle_medium_crisis(self, message: Message, ash_response: str):
        """
        Your existing handle_medium_crisis logic
        """
        logger.info(f"⚠️ MEDIUM CRISIS detected for {message.author} in {message.channel}")
        
        # Send Ash's response
        await message.reply(ash_response)
        
        # Alert crisis response team (no staff DM for medium)
        await self._send_crisis_team_alert(message, "MEDIUM")
        
        logger.info(f"✅ Medium crisis handling completed for {message.author}")
    
    async def _send_staff_dm(self, message: Message):
        """Your existing staff DM logic"""
        try:
            staff_user = await self.bot.fetch_user(self.staff_ping_user_id)
            
            embed = discord.Embed(
                title="🚨 Crisis Support Needed - URGENT",
                description="High-crisis keywords detected requiring immediate attention",
                color=discord.Color.red(),
                timestamp=message.created_at
            )
            
            embed.add_field(
                name="User", 
                value=f"{message.author.mention} ({message.author.display_name})", 
                inline=True
            )
            embed.add_field(
                name="Channel", 
                value=f"{message.channel.mention} ({message.channel.name})", 
                inline=True
            )
            embed.add_field(
                name="Server", 
                value=message.guild.name, 
                inline=True
            )
            
            # Truncate message if too long
            message_content = message.content
            if len(message_content) > 1000:
                message_content = message_content[:1000] + "..."
            
            embed.add_field(
                name="Original Message", 
                value=message_content, 
                inline=False
            )
            embed.add_field(
                name="Jump to Message", 
                value=f"[Click here]({message.jump_url})", 
                inline=False
            )
            embed.add_field(
                name="Resources Channel", 
                value=f"<#{self.resources_channel_id}>", 
                inline=False
            )
            
            await staff_user.send(embed=embed)
            logger.warning(f"📧 Crisis escalation DM sent to staff for {message.author}")
            
        except discord.NotFound:
            logger.error(f"❌ Staff user ID {self.staff_ping_user_id} not found")
        except discord.Forbidden:
            logger.error(f"❌ Cannot send DM to staff user - DMs may be disabled")
        except Exception as e:
            logger.error(f"❌ Error sending crisis DM to staff: {e}")
    
    async def _send_crisis_team_alert(self, message: Message, crisis_level: str):
        """Your existing crisis team alert logic"""
        try:
            crisis_channel = self.bot.get_channel(self.crisis_response_channel_id)
            if not crisis_channel:
                logger.error(f"❌ Crisis response channel {self.crisis_response_channel_id} not found")
                return
            
            # Create appropriate embed based on crisis level
            if crisis_level == "HIGH":
                color = discord.Color.red()
                title = "🚨 Crisis Response Team Alert"
                description = "High-crisis situation detected requiring team response"
                action_text = "Please respond to provide crisis support"
            else:  # MEDIUM
                color = discord.Color.orange()
                title = "⚠️ Medium Crisis Alert"
                description = "Significant distress detected - team awareness needed"
                action_text = "Monitor situation - intervention may be needed"
            
            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=message.created_at
            )
            
            embed.add_field(
                name="Location", 
                value=f"{message.channel.mention} in {message.guild.name}", 
                inline=True
            )
            embed.add_field(
                name="User", 
                value=message.author.mention, 
                inline=True
            )
            embed.add_field(
                name="Crisis Level", 
                value=f"{crisis_level} - {action_text}", 
                inline=True
            )
            embed.add_field(
                name="Jump to Message", 
                value=f"[Click here]({message.jump_url})", 
                inline=False
            )
            
            # Ping crisis response team
            role_mention = f"<@&{self.crisis_response_role_id}>"
            await crisis_channel.send(role_mention, embed=embed)
            
            logger.info(f"📢 {crisis_level} crisis team alert sent for {message.author}")
            
        except Exception as e:
            logger.error(f"❌ Error sending crisis team alert: {e}")