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
from core.ash_character import format_ash_prompt, get_crisis_addition, get_response_templates

logger = logging.getLogger(__name__)

class ClaudeAPI:
    def __init__(self):
        self.model = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.max_tokens = 300
        self.session = None
        self._session_lock = asyncio.Lock()
        
        # Rate limiting
        self.calls_today = 0
        self.last_call_time = 0
        self.min_call_interval = 1.0
        
        if not self.api_key:
            logger.error("CLAUDE_API_KEY not found in environment variables")
            raise ValueError("Claude API key is required")

        logger.info(f"🤖 Claude API initialized with model: {self.model}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with thread-safe initialization"""
        async with self._session_lock:
            if self.session is None or self.session.closed:
                connector = aiohttp.TCPConnector(
                    limit=10,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    enable_cleanup_closed=True,
                    keepalive_timeout=30,
                    force_close=True
                )
                
                self.session = aiohttp.ClientSession(
                    connector=connector,
                    headers={
                        'Content-Type': 'application/json',
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01'
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                )
                logger.debug("Created new Claude API session")
            return self.session

    @asynccontextmanager
    async def _request_context(self):
        """Context manager for API requests with proper error handling"""
        session = None
        try:
            session = await self._get_session()
            yield session
        except Exception as e:
            logger.error(f"Session error: {e}")
            # Force session recreation on next request
            if self.session:
                await self._force_close_session()
            raise
        finally:
            # Session cleanup is handled by the close() method
            pass

    async def _force_close_session(self):
        """Force close session in case of errors"""
        async with self._session_lock:
            if self.session and not self.session.closed:
                try:
                    await self.session.close()
                except Exception as e:
                    logger.debug(f"Error force-closing session: {e}")
                finally:
                    self.session = None

    async def get_ash_response(self, user_message: str, crisis_level: str = 'low', username: str = 'friend') -> str:
        """
        Get response from Claude as Ash character with improved error handling
        """
        
        try:
            # Rate limiting
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_call_time
            if time_since_last < self.min_call_interval:
                await asyncio.sleep(self.min_call_interval - time_since_last)

            # Format the prompt
            prompt = format_ash_prompt(user_message, crisis_level, username)
            
            # Prepare payload
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            logger.info(f"Sending request to Claude API for {username} (crisis: {crisis_level})")
            
            # Make request with proper session management
            async with self._request_context() as session:
                async with session.post(self.base_url, json=payload) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    self.calls_today += 1
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        data = json.loads(response_text)
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
                        return get_response_templates()['rate_limited']
                    
                    elif response.status == 529:
                        logger.warning("Claude API temporarily overloaded")
                        return "I'm having trouble connecting right now due to high demand. Please try again in a moment."
                        
                    elif response.status == 401:
                        logger.error("Claude API authentication failed")
                        return get_response_templates()['api_error']
                        
                    else:
                        logger.error(f"Claude API error {response.status}: {response_text}")
                        return get_response_templates()['api_error']
                    
        except asyncio.TimeoutError:
            logger.error("Claude API request timed out")
            return get_response_templates()['api_error']
            
        except aiohttp.ClientError as e:
            logger.error(f"Network error calling Claude API: {e}")
            return get_response_templates()['api_error']
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Claude API: {e}")
            return get_response_templates()['api_error']
            
        except Exception as e:
            logger.error(f"Unexpected error in Claude API call: {e}")
            return get_response_templates()['api_error']

    async def test_connection(self) -> bool:
        """Test connection to Claude API"""
        try:
            test_response = await self.get_ash_response(
                "Hello, can you hear me?", 
                "low", 
                "test_user"
            )
            
            if test_response == get_response_templates()['api_error']:
                return False
                
            logger.info("Claude API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Claude API connection test failed: {e}")
            return False

    async def get_usage_stats(self) -> dict:
        """Get usage statistics for monitoring"""
        return {
            'calls_today': self.calls_today,
            'last_call_time': self.last_call_time,
            'session_active': self.session is not None and not self.session.closed,
            'model': self.model
        }

    async def reset_daily_counter(self):
        """Reset daily call counter (call this daily via scheduled task)"""
        old_count = self.calls_today
        self.calls_today = 0
        logger.info(f"Reset daily counter from {old_count} to 0")
    
    async def close(self):
        """Properly close all connections and clean up resources"""
        async with self._session_lock:
            if self.session and not self.session.closed:
                try:
                    # Get connector reference before closing
                    connector = self.session.connector
                    
                    # Close session
                    await self.session.close()
                    
                    # Wait for all connections to close
                    if connector and not connector.closed:
                        await connector.close()
                    
                    # Small delay to allow cleanup
                    await asyncio.sleep(0.1)
                    
                    logger.info("Claude API session closed properly")
                    
                except Exception as e:
                    logger.warning(f"Error during Claude API cleanup: {e}")
                finally:
                    self.session = None

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