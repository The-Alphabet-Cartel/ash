"""
Keyword Detection System for Ash Bot
Identifies when messages indicate need for mental health support
"""

import re
import logging

logger = logging.getLogger(__name__)

class KeywordDetector:
    def __init__(self):
        # High-crisis keywords requiring immediate staff notification
        self.high_crisis_keywords = {
            'suicidal_ideation': [
                'kill myself', 'end it all', 'want to die', 'suicide', 'suicidal',
                'better off dead', 'can\'t go on', 'no point living', 'end my life',
                'not worth living', 'want to disappear forever', 'ready to die'
            ],
            'self_harm': [
                'cut myself', 'hurt myself', 'self harm', 'want to cut', 'need to cut',
                'deserve pain', 'cutting again', 'relapsed cutting', 'razor blade',
                'cutting myself'
            ],
            'immediate_danger': [
                'have a plan', 'goodbye everyone', 'this is goodbye', 'final message',
                'pills ready', 'bridge tonight', 'gun loaded', 'rope tied'
            ]
        }
        
        # Medium-crisis keywords indicating significant distress
        self.medium_crisis_keywords = {
            'severe_depression': [
                'can\'t take it anymore', 'everything hurts', 'so much pain',
                'completely broken', 'lost all hope', 'nothing matters',
                'why bother', 'give up', 'can\'t handle this', 'too much pain'
            ],
            'panic_anxiety': [
                'panic attack', 'can\'t breathe', 'heart racing', 'losing control',
                'going crazy', 'feel like dying', 'can\'t calm down', 'hyperventilating'
            ],
            'dissociation': [
                'not real', 'floating away', 'watching myself', 'not in my body',
                'everything feels fake', 'disconnected', 'out of body', 'depersonalization'
            ],
            'trauma_flashbacks': [
                'happening again', 'back there', 'can\'t escape', 'reliving it',
                'flashback', 'triggered', 'ptsd episode', 'memory won\'t stop'
            ]
        }
        
        # Low-crisis keywords indicating need for support
        self.low_crisis_keywords = {
            'depression_symptoms': [
                'feel worthless', 'hate myself', 'feel empty', 'so tired',
                'can\'t sleep', 'no energy', 'feel numb', 'so lonely',
                'nobody cares', 'feel invisible', 'exhausted', 'hopeless'
            ],
            'anxiety_symptoms': [
                'so anxious', 'worried about everything', 'overthinking',
                'can\'t stop worrying', 'feel on edge', 'restless', 'nervous'
            ],
            'identity_struggles': [
                'don\'t know who i am', 'feel fake', 'pretending', 'imposter',
                'not good enough', 'don\'t belong', 'questioning everything',
                'identity crisis', 'feel lost', 'confused about myself'
            ],
            'relationship_trauma': [
                'feel betrayed', 'used me', 'feel unlovable', 'trust issues',
                'abandoned again', 'nobody understands', 'rejected', 'alone'
            ],
            'lgbtq_struggles': [
                'coming out', 'family rejected me', 'not accepted', 'dysphoria',
                'internalized homophobia', 'feel different', 'closeted',
                'transition struggles', 'pronouns ignored', 'deadnamed'
            ],
            'failure_feelings': [
                'such a failure', 'disappointed everyone', 'screwed up again',
                'can\'t do anything right', 'let everyone down', 'failed at life'
            ]
        }
        
        # Compile regex patterns for efficient matching
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile keyword patterns into regex for efficient matching"""
        self.high_crisis_patterns = []
        self.medium_crisis_patterns = []
        self.low_crisis_patterns = []
        
        # High crisis patterns
        for category, keywords in self.high_crisis_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                self.high_crisis_patterns.append((pattern, category))
                
        # Medium crisis patterns
        for category, keywords in self.medium_crisis_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                self.medium_crisis_patterns.append((pattern, category))
                
        # Low crisis patterns
        for category, keywords in self.low_crisis_keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                self.low_crisis_patterns.append((pattern, category))
    
    def check_message(self, message_content):
        """
        Analyze message for keywords indicating need for support
        
        Args:
            message_content (str): The message to analyze
            
        Returns:
            dict: {
                'needs_response': bool,
                'crisis_level': str,  # 'high', 'medium', 'low'
                'detected_categories': list,
                'matched_keywords': list
            }
        """
        
        if not message_content:
            return self._no_response_result()
            
        message_lower = message_content.lower()
        detected_categories = []
        matched_keywords = []
        
        # Check for high crisis first
        for pattern, category in self.high_crisis_patterns:
            if re.search(pattern, message_lower):
                detected_categories.append(category)
                matched_keywords.append(pattern)
                logger.warning(f"High crisis keyword detected: {category}")
                return {
                    'needs_response': True,
                    'crisis_level': 'high',
                    'detected_categories': detected_categories,
                    'matched_keywords': matched_keywords
                }
        
        # Check for medium crisis
        for pattern, category in self.medium_crisis_patterns:
            if re.search(pattern, message_lower):
                detected_categories.append(category)
                matched_keywords.append(pattern)
                
        if detected_categories:
            logger.info(f"Medium crisis keywords detected: {detected_categories}")
            return {
                'needs_response': True,
                'crisis_level': 'medium',
                'detected_categories': detected_categories,
                'matched_keywords': matched_keywords
            }
        
        # Check for low crisis
        for pattern, category in self.low_crisis_patterns:
            if re.search(pattern, message_lower):
                detected_categories.append(category)
                matched_keywords.append(pattern)
                
        if detected_categories:
            logger.info(f"Low crisis keywords detected: {detected_categories}")
            return {
                'needs_response': True,
                'crisis_level': 'low',
                'detected_categories': detected_categories,
                'matched_keywords': matched_keywords
            }
        
        return self._no_response_result()
    
    def _no_response_result(self):
        """Return result structure for no response needed"""
        return {
            'needs_response': False,
            'crisis_level': 'none',
            'detected_categories': [],
            'matched_keywords': []
        }
    
    def add_custom_keywords(self, crisis_level, category, keywords):
        """
        Add custom keywords for specific server needs
        
        Args:
            crisis_level (str): 'high', 'medium', or 'low'
            category (str): Category name for the keywords
            keywords (list): List of keyword strings to add
        """
        
        if crisis_level == 'high':
            if category not in self.high_crisis_keywords:
                self.high_crisis_keywords[category] = []
            self.high_crisis_keywords[category].extend(keywords)
            
        elif crisis_level == 'medium':
            if category not in self.medium_crisis_keywords:
                self.medium_crisis_keywords[category] = []
            self.medium_crisis_keywords[category].extend(keywords)
            
        elif crisis_level == 'low':
            if category not in self.low_crisis_keywords:
                self.low_crisis_keywords[category] = []
            self.low_crisis_keywords[category].extend(keywords)
        
        # Recompile patterns after adding keywords
        self._compile_patterns()
        logger.info(f"Added {len(keywords)} keywords to {crisis_level} crisis level, category: {category}")
    
    def get_keyword_stats(self):
        """Get statistics about loaded keywords"""
        high_count = sum(len(keywords) for keywords in self.high_crisis_keywords.values())
        medium_count = sum(len(keywords) for keywords in self.medium_crisis_keywords.values())
        low_count = sum(len(keywords) for keywords in self.low_crisis_keywords.values())
        
        return {
            'high_crisis': high_count,
            'medium_crisis': medium_count,
            'low_crisis': low_count,
            'total': high_count + medium_count + low_count
        }