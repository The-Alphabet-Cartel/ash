"""
NLP Integration - Simple wrapper around your existing NLP client
Copy this to: ash/bot/integrations/nlp_integration.py
"""

import logging
from nlp_integration import RemoteNLPClient

logger = logging.getLogger(__name__)

class NLPIntegration:
    """Simple wrapper around your existing RemoteNLPClient"""
    
    def __init__(self, config):
        self.config = config
        self.nlp_client = RemoteNLPClient()  # Your existing NLP client
        
        logger.info("🌐 NLP integration initialized (wrapper)")
    
    async def analyze_message(self, message: str, user_id: str, channel_id: str) -> dict:
        """Analyze message using NLP service"""
        return await self.nlp_client.analyze_message(message, user_id, channel_id)
    
    async def test_connection(self) -> bool:
        """Test connection to NLP service"""
        return await self.nlp_client.test_connection()
    
    async def close(self):
        """Clean shutdown"""
        # Your existing NLP client might not have close method
        pass
    
    def get_stats(self) -> dict:
        """Get statistics"""
        return {
            'component': 'NLPIntegration',
            'nlp_url': f"http://{self.nlp_client.nlp_host}:{self.nlp_client.nlp_port}",
            'service_healthy': self.nlp_client.service_healthy
        }