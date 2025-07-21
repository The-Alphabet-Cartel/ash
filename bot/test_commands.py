# Create a simple test file: test_commands.py
# Put this in your ash/bot/ directory alongside crisis_commands.py

import discord
from discord import app_commands
from discord.ext import commands
import logging
import os

logger = logging.getLogger(__name__)

class TestCommands(commands.Cog):
    """Simple test commands to verify slash command functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.crisis_response_role_id = int(os.getenv('CRISIS_RESPONSE_ROLE_ID', '0'))
        logger.info(f"🧪 Test commands cog initialized with role ID: {self.crisis_response_role_id}")
    
    def _has_crisis_response_role(self, interaction: discord.Interaction) -> bool:
        """Check if user has CrisisResponse role"""
        if not interaction.user.roles:
            return False
        return any(role.id == self.crisis_response_role_id for role in interaction.user.roles)
    
    @app_commands.command(name="test_ping", description="Simple test command for crisis response team")
    async def test_ping(self, interaction: discord.Interaction):
        """Simple test command"""
        
        if not self._has_crisis_response_role(interaction):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="This command is restricted to Crisis Response team members.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ Test Successful",
            description="Ash slash commands are working!",
            color=discord.Color.green()
        )
        embed.add_field(name="User", value=interaction.user.mention, inline=True)
        embed.add_field(name="Guild", value=interaction.guild.name, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Test command used by {interaction.user}")

async def setup(bot):
    """Setup function for the test cog"""
    await bot.add_cog(TestCommands(bot))