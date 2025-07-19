"""
Claude API Integration for Ash Bot
Handles communication with Anthropic's Claude API
"""

import asyncio
import logging
import os
from typing import Optional
import aiohttp
import json
from ash_character import format_ash_prompt, get_crisis_addition, RESPONSE_TEMPLATES

logger = logging.getLogger(__name__)

class ClaudeAPI:
    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"  # Latest Sonnet model
        self.max_tokens = 300  # Keep responses concise
        self.session = None
        
        # Rate limiting
        self.calls_today = 0
        self.last_call_time = 0
        self.min_call_interval = 1.0  # Minimum seconds between calls
        
        if not self.api_key:
            logger.error("CLAUDE_API_KEY not found in environment variables")
            raise ValueError("Claude API key is required")
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def get_ash_response(self, user_message: str, crisis_level: str = 'low', username: str = 'friend') -> str:
        """
        Get response from Claude as Ash character
        
        Args:
            user_message (str): The user's message
            crisis_level (str): Crisis level from keyword detector
            username (str): Discord username for personalization
            
        Returns:
            str: Ash's response
        """
        
        try:
            # Rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_call_time
            if time_since_last < self.min_call_interval:
                await asyncio.sleep(self.min_call_interval - time_since_last)
            
            # Format the prompt with Ash's character
            prompt = format_ash_prompt(user_message, crisis_level, username)
            
            # Prepare API request
            session = await self._get_session()
            
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,  # Slight randomness for natural responses
                "top_p": 0.9
            }
            
            logger.info(f"Sending request to Claude API for {username} (crisis: {crisis_level})")
            
            async with session.post(self.base_url, json=payload) as response:
                self.last_call_time = asyncio.get_event_loop().time()
                self.calls_today += 1
                
                if response.status == 200:
                    data = await response.json()
                    ash_response = data['content'][0]['text'].strip()
                    
                    # Add crisis-level specific additions
                    crisis_addition = get_crisis_addition(crisis_level)
                    final_response = ash_response + crisis_addition
                    
                    # Ensure response isn't too long for Discord
                    if len(final_response) > 2000:
                        final_response = final_response[:1997] + "..."
                    
                    logger.info(f"Successfully got response from Claude ({len(final_response)} chars)")
                    return final_response
                    
                elif response.status == 429:
                    logger.warning("Claude API rate limit hit")
                    return RESPONSE_TEMPLATES['rate_limited']
                    
                elif response.status == 401:
                    logger.error("Claude API authentication failed")
                    return RESPONSE_TEMPLATES['api_error']
                    
                else:
                    error_text = await response.text()
                    logger.error(f"Claude API error {response.status}: {error_text}")
                    return RESPONSE_TEMPLATES['api_error']
                    
        except asyncio.TimeoutError:
            logger.error("Claude API request timed out")
            return RESPONSE_TEMPLATES['api_error']
            
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling Claude API: {e}")
            return RESPONSE_TEMPLATES['api_error']
            
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            return RESPONSE_TEMPLATES['api_error']
            
        except Exception as e:
            logger.error(f"Unexpected error in Claude API call: {e}")
            return RESPONSE_TEMPLATES['api_error']
    
    async def test_connection(self) -> bool:
        """
        Test connection to Claude API
        
        Returns:
            bool: True if connection successful
        """
        
        try:
            test_response = await self.get_ash_response(
                "Hello, can you hear me?", 
                "low", 
                "test_user"
            )
            
            if test_response == RESPONSE_TEMPLATES['api_error']:
                return False
                
            logger.info("Claude API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Claude API connection test failed: {e}")
            return False
    
    async def get_usage_stats(self) -> dict:
        """
        Get usage statistics for monitoring
        
        Returns:
            dict: Usage statistics
        """
        
        return {
            'calls_today': self.calls_today,
            'last_call_time': self.last_call_time,
            'session_active': self.session is not None and not self.session.closed
        }
    
    async def reset_daily_counter(self):
        """Reset daily call counter (call this daily via scheduled task)"""
        old_count = self.calls_today
        self.calls_today = 0
        logger.info(f"Reset daily counter from {old_count} to 0")
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Claude API session closed")

class ClaudeAPIError(Exception):
    """Custom exception for Claude API errors"""
    pass

# Async context manager for proper session handling
class AsyncClaudeAPI:
    def __init__(self):
        self.api = ClaudeAPI()
    
    async def __aenter__(self):
        return self.api
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.api.close()