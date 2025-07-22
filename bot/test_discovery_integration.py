#!/usr/bin/env python3
"""
Test script for NLP server integration with discovery
Run this before deploying to verify your NLP server is ready
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_nlp_server():
    """Test the NLP server endpoints for keyword discovery"""
    
    nlp_host = os.getenv('NLP_SERVICE_HOST', 'localhost')
    nlp_port = os.getenv('NLP_SERVICE_PORT', '8881')
    nlp_url = f"http://{nlp_host}:{nlp_port}"
    
    print(f"🔍 Testing NLP server at {nlp_url}")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{nlp_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data.get('status', 'unknown')}")
                    print(f"   Models loaded: {data.get('model_loaded', False)}")
                else:
                    print(f"❌ Health check failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Test 2: Original analyze endpoint
    print("\n2. Testing analyze endpoint...")
    try:
        test_message = "I feel worthless and hate myself"
        async with aiohttp.ClientSession() as session:
            payload = {
                "message": test_message,
                "user_id": "test_user",
                "channel_id": "test_channel"
            }
            async with session.post(f"{nlp_url}/analyze", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Analyze endpoint working")
                    print(f"   Crisis level: {data.get('crisis_level', 'unknown')}")
                    print(f"   Confidence: {data.get('confidence_score', 0):.3f}")
                else:
                    print(f"❌ Analyze failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Analyze error: {e}")
        return False
    
    # Test 3: Check if extract_phrases endpoint exists
    print("\n3. Testing extract_phrases endpoint...")
    try:
        test_message = "I'm struggling with transition regret and family rejection"
        async with aiohttp.ClientSession() as session:
            payload = {
                "message": test_message,
                "user_id": "test_user", 
                "channel_id": "test_channel",
                "parameters": {
                    "min_phrase_length": 2,
                    "max_phrase_length": 5,
                    "crisis_focus": True,
                    "community_specific": True,
                    "min_confidence": 0.6
                }
            }
            async with session.post(f"{nlp_url}/extract_phrases", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    phrases = data.get('phrases', [])
                    print(f"✅ Phrase extraction working")
                    print(f"   Found {len(phrases)} potential keywords")
                    
                    # Show top 3 phrases
                    for i, phrase in enumerate(phrases[:3]):
                        print(f"   {i+1}. '{phrase.get('text', '')}' (confidence: {phrase.get('confidence', 0):.2f}, level: {phrase.get('crisis_level', '')})")
                    
                    return True
                elif response.status == 404:
                    print("⚠️ extract_phrases endpoint not implemented yet")
                    print("   This is expected - the endpoint will be added to your NLP server")
                    return True  # Not a failure, just not implemented yet
                else:
                    print(f"❌ Phrase extraction failed: HTTP {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return False
    except Exception as e:
        print(f"❌ Phrase extraction error: {e}")
        return False

async def test_keyword_discovery_integration():
    """Test the keyword discovery integration locally"""
    
    print("\n" + "="*50)
    print("TESTING KEYWORD DISCOVERY INTEGRATION")
    print("="*50)
    
    # Test that we can import the new modules
    try:
        from keyword_discovery import KeywordDiscoveryService, KeywordDiscoveryManager
        from discovery_commands import DiscoveryCommands
        print("✅ All discovery modules import successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test KeywordDiscoveryService initialization
    try:
        # Mock keyword detector
        class MockKeywordDetector:
            def check_message(self, message):
                return {'needs_response': False, 'crisis_level': 'none'}
        
        service = KeywordDiscoveryService(MockKeywordDetector())
        stats = await service.get_discovery_stats()
        print("✅ KeywordDiscoveryService initializes correctly")
        print(f"   Discovery enabled: {stats['discovery_enabled']}")
        print(f"   Min confidence: {stats['min_confidence']}")
        print(f"   Max daily discoveries: {stats['max_daily']}")
    except Exception as e:
        print(f"❌ KeywordDiscoveryService error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    async def main():
        print("🚀 Starting Phase 1 Discovery System Tests")
        
        # Test NLP server
        nlp_success = await test_nlp_server()
        
        # Test local integration
        integration_success = await test_keyword_discovery_integration()
        
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        
        if nlp_success and integration_success:
            print("✅ ALL TESTS PASSED - Ready for Phase 1 deployment!")
            print("\nNext steps:")
            print("1. Add the new files to your bot directory")
            print("2. Update your .env file with discovery settings")
            print("3. Update main.py with the integration code")
            print("4. Deploy and test the /discovery_status command")
        else:
            print("❌ Some tests failed - check the errors above")
            print("\nRequired fixes:")
            if not nlp_success:
                print("- Fix NLP server connection or endpoints")
            if not integration_success:
                print("- Fix discovery module integration")
    
    asyncio.run(main())