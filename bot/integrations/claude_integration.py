"""
Claude Integration - Simple wrapper around your existing Claude API
Copy this to: ash/bot/integrations/claude_integration.py
"""

import logging
from claude_api import ClaudeAPI

logger = logging.getLogger(__name__)

class ClaudeIntegration:
    """Simple wrapper around your existing ClaudeAPI"""
    
    def __init__(self, config):
        self.config = config
        self.claude_api = ClaudeAPI()  # Your existing API class
        
        logger.info("🧠 Claude integration initialized (wrapper)")
    
    async def get_ash_response(self, message: str, crisis_level: str, username: str) -> str:
        """Get response from Claude as Ash character"""
        return await self.claude_api.get_ash_response(message, crisis_level, username)
    
    async def test_connection(self) -> bool:
        """Test connection to Claude API"""
        return await self.claude_api.test_connection()
    
    async def close(self):
        """Clean shutdown"""
        await self.claude_api.close()
    
    def get_stats(self) -> dict:
        """Get statistics"""
        stats = self.claude_api.get_usage_stats()
        stats['component'] = 'ClaudeIntegration'
        return stats