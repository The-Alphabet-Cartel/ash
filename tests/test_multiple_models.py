#!/usr/bin/env python3
"""
Multi-Model Crisis Detection Test
Test multiple models to find the best one for crisis detection
Optimized for Debian 12 Linux Server with RTX 3060, 64GB RAM, Ryzen 7 5800X
"""

import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification, 
    pipeline, AutoModel
)
from sentence_transformers import SentenceTransformer
from huggingface_hub import login
import numpy as np
import time
import json
import psutil
from datetime import datetime
import sys
import os
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Mean of empty slice")
warnings.filterwarnings("ignore", category=RuntimeWarning, message="invalid value encountered in divide")

# Set up Hugging Face authentication (optional)
HF_TOKEN = "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"
USE_AUTH_TOKEN = None  # Will be set during authentication attempt

# Set up proper CUDA environment
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True

class MultiModelTester:
    def __init__(self, use_gpu=True):
        """Initialize multiple crisis detection models"""
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = torch.device('cuda' if self.use_gpu else 'cpu')
        
        print("🔄 Initializing Multi-Model Crisis Detection Tester...")
        print(f"🖥️  Device: {self.device}")
        
        # Authenticate with Hugging Face (optional)
        global USE_AUTH_TOKEN
        try:
            print("🔐 Attempting Hugging Face authentication...")
            login(token=HF_TOKEN, add_to_git_credential=False)
            USE_AUTH_TOKEN = HF_TOKEN
            print("✅ Hugging Face authentication successful")
        except Exception as e:
            print(f"⚠️  Hugging Face authentication failed: {e}")
            print("⚠️  Continuing without authentication - public models only")
            USE_AUTH_TOKEN = None
        
        if self.use_gpu:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"🎮 GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        
        # Define models to test
        self.model_configs = {
            # Mental Health Specific Models
            "mental_roberta": {
                "model_name": "martin-ha/toxic-comment-model",
                "type": "classification",
                "description": "Toxic comment detection (alternative to unitary/toxic-bert)"
            },
            
            # Emotion and Mental Health Models
            "emotion_roberta": {
                "model_name": "j-hartmann/emotion-english-distilroberta-base",
                "type": "classification", 
                "description": "Emotion detection - may catch distress patterns"
            },
            
            "depression_specific": {
                "model_name": "rafalposwiata/deproberta-large-depression",
                "type": "classification",
                "description": "Current depression model (for comparison)"
            },
            
            # Suicide-Specific Models
            "suicide_detection": {
                "model_name": "yanyankangkang/bert-base-uncased-suicidal-detection",
                "type": "classification",
                "description": "Specifically trained for suicide detection"
            },
            
            # Mental Health Classification
            "mental_health_classifier": {
                "model_name": "dkolety/mental-health-data-distilbert",
                "type": "classification", 
                "description": "Mental health condition classifier"
            },
            
            # Semantic Similarity Models (for pattern matching)
            "sentence_transformer": {
                "model_name": "all-MiniLM-L6-v2",
                "type": "similarity",
                "description": "Semantic similarity for crisis pattern matching"
            },
            
            # Alternative Approaches
            "hate_speech_detector": {
                "model_name": "unitary/unbiased-toxic-roberta",
                "type": "classification",
                "description": "Unbiased toxic detection (may work better than toxic-bert)"
            }
        }
        
        # Crisis patterns for semantic similarity testing
        self.crisis_patterns = [
            "everyone would be happier without me",
            "nobody would miss me if i was gone", 
            "world would be better without me",
            "i want to kill myself",
            "i want to die",
            "i want to end my life",
            "i'm going to hurt myself", 
            "i can't take it anymore",
            "i want to disappear forever",
            "life isn't worth living",
            "i'm a burden to everyone",
            "people would be better off without me",
            "i should just end it all",
            "i'm tired of living",
            "i hate being alive"
        ]
        
    def load_model(self, model_key):
        """Load a specific model"""
        config = self.model_configs[model_key]
        model_name = config["model_name"]
        model_type = config["type"]
        
        print(f"📦 Loading {model_key}: {config['description']}")
        
        try:
            if model_type == "similarity":
                # Sentence transformer model
                model = SentenceTransformer(model_name, device=self.device, use_auth_token=USE_AUTH_TOKEN)
                self.models[model_key] = model
                print(f"✅ Loaded sentence transformer: {model_key}")
                
            elif model_type == "classification":
                # Classification model with better precision handling
                tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=USE_AUTH_TOKEN)
                
                if self.use_gpu:
                    try:
                        # Try float16 first for speed
                        model = AutoModelForSequenceClassification.from_pretrained(
                            model_name, 
                            torch_dtype=torch.float16,
                            use_auth_token=USE_AUTH_TOKEN
                        ).to(self.device)
                        # Test if float16 works with a dummy input
                        test_input = tokenizer("test", return_tensors="pt", padding=True, truncation=True)
                        test_input = {k: v.to(self.device) for k, v in test_input.items()}
                        with torch.no_grad():
                            _ = model(**test_input)
                        print(f"✅ Using float16 precision for {model_key}")
                    except Exception as e:
                        print(f"⚠️  Float16 failed for {model_key}, falling back to float32: {e}")
                        # Fallback to float32
                        model = AutoModelForSequenceClassification.from_pretrained(
                            model_name, 
                            torch_dtype=torch.float32,
                            use_auth_token=USE_AUTH_TOKEN
                        ).to(self.device)
                else:
                    model = AutoModelForSequenceClassification.from_pretrained(
                        model_name,
                        torch_dtype=torch.float32,
                        use_auth_token=USE_AUTH_TOKEN
                    )
                    model = model.to(self.device)
                
                model.eval()
                self.models[model_key] = model
                self.tokenizers[model_key] = tokenizer
                print(f"✅ Loaded classification model: {model_key}")
                
        except Exception as e:
            print(f"❌ Failed to load {model_key}: {e}")
            return False
        
        return True
    
    def analyze_with_classification_model(self, text, model_key):
        """Analyze text with a classification model"""
        if model_key not in self.models:
            return {"error": f"Model {model_key} not loaded"}
        
        start_time = time.time()
        
        try:
            model = self.models[model_key]
            tokenizer = self.tokenizers[model_key]
            
            # Tokenize
            inputs = tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                if self.use_gpu:
                    torch.cuda.synchronize()
                    
                outputs = model(**inputs)
                logits = outputs.logits.squeeze()
                
                if self.use_gpu:
                    torch.cuda.synchronize()
                    logits = logits.cpu()
                    
            # Get probabilities with precision handling
            if len(logits.shape) == 0:  # Single output
                try:
                    probabilities = torch.sigmoid(logits).numpy()
                except RuntimeError as e:
                    if "Half" in str(e):
                        # Convert to float32 for operations not supported in float16
                        logits = logits.float()
                        probabilities = torch.sigmoid(logits).numpy()
                    else:
                        raise e
                labels = ["crisis"]
            else:  # Multiple outputs
                try:
                    probabilities = torch.softmax(logits, dim=-1).numpy()
                except RuntimeError as e:
                    if "Half" in str(e):
                        # Convert to float32 for operations not supported in float16
                        logits = logits.float()
                        probabilities = torch.softmax(logits, dim=-1).numpy()
                    else:
                        raise e
                # Try to get label names from model config
                try:
                    labels = model.config.id2label
                    if isinstance(labels, dict):
                        labels = [labels[i] for i in range(len(probabilities))]
                    else:
                        labels = [f"label_{i}" for i in range(len(probabilities))]
                except:
                    labels = [f"label_{i}" for i in range(len(probabilities))]
            
            processing_time = (time.time() - start_time) * 1000
            
            # Create results
            if isinstance(probabilities, np.ndarray) and len(probabilities) > 1:
                results = dict(zip(labels, probabilities.tolist()))
                max_score = float(max(probabilities))
                max_label = labels[np.argmax(probabilities)]
            else:
                score = float(probabilities) if not isinstance(probabilities, np.ndarray) else float(probabilities[0])
                results = {labels[0]: score}
                max_score = score
                max_label = labels[0]
            
            results.update({
                'processing_time_ms': processing_time,
                'max_score': max_score,
                'max_label': max_label,
                'model_type': 'classification'
            })
            
            return results
            
        except Exception as e:
            return {"error": str(e), "processing_time_ms": (time.time() - start_time) * 1000}
    
    def analyze_with_similarity_model(self, text, model_key):
        """Analyze text using semantic similarity to crisis patterns"""
        if model_key not in self.models:
            return {"error": f"Model {model_key} not loaded"}
        
        start_time = time.time()
        
        try:
            model = self.models[model_key]
            
            # Get embeddings
            text_embedding = model.encode([text])
            pattern_embeddings = model.encode(self.crisis_patterns)
            
            # Calculate similarities
            similarities = cosine_similarity(text_embedding, pattern_embeddings)[0]
            
            processing_time = (time.time() - start_time) * 1000
            
            # Find best matches
            best_match_idx = np.argmax(similarities)
            best_similarity = float(similarities[best_match_idx])
            best_pattern = self.crisis_patterns[best_match_idx]
            
            # Calculate overall crisis score (handle empty arrays)
            relevant_similarities = similarities[similarities > 0.3]
            if len(relevant_similarities) > 0:
                crisis_score = float(np.mean(relevant_similarities))  # Average of relevant similarities
            else:
                crisis_score = float(best_similarity)  # Fallback to best match if no relevant ones
            
            results = {
                'crisis_score': crisis_score,
                'best_similarity': best_similarity,
                'best_pattern': best_pattern,
                'all_similarities': similarities.tolist(),
                'processing_time_ms': processing_time,
                'max_score': crisis_score,
                'model_type': 'similarity'
            }
            
            return results
            
        except Exception as e:
            return {"error": str(e), "processing_time_ms": (time.time() - start_time) * 1000}
    
    def analyze_text(self, text, model_key):
        """Analyze text with the specified model"""
        config = self.model_configs[model_key]
        
        if config["type"] == "similarity":
            return self.analyze_with_similarity_model(text, model_key)
        else:
            return self.analyze_with_classification_model(text, model_key)

def get_system_info():
    """Get system information"""
    info = {
        'cpu_count': psutil.cpu_count(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_total_gb': psutil.virtual_memory().total / 1024**3,
        'memory_available_gb': psutil.virtual_memory().available / 1024**3,
        'memory_percent': psutil.virtual_memory().percent,
    }
    
    if torch.cuda.is_available():
        info['gpu_available'] = True
        info['gpu_name'] = torch.cuda.get_device_name(0)
        info['gpu_memory_total_gb'] = torch.cuda.get_device_properties(0).total_memory / 1024**3
    else:
        info['gpu_available'] = False
        
    return info

def test_multiple_models():
    """Test multiple models on crisis detection phrases"""
    
    # Display system information
    print("="*80)
    print("🖥️  SYSTEM INFORMATION")
    print("="*80)
    
    sys_info = get_system_info()
    print(f"CPU: {sys_info['cpu_count']} cores @ {sys_info['cpu_percent']:.1f}% usage")
    print(f"RAM: {sys_info['memory_available_gb']:.1f}GB available / {sys_info['memory_total_gb']:.1f}GB total ({sys_info['memory_percent']:.1f}% used)")
    
    if sys_info['gpu_available']:
        print(f"GPU: {sys_info['gpu_name']} ({sys_info['gpu_memory_total_gb']:.1f}GB)")
    else:
        print("GPU: Not available (CPU-only mode)")
    
    print()
    
    # Initialize tester
    tester = MultiModelTester()
    
    # Test phrases (same as before)
    test_phrases = [
        {
            'phrase': 'Everyone would be happier without me',
            'expected': 'high',
            'current_result': 'none (failed)',
            'type': 'burden ideation',
            'description': 'Classic suicidal ideation expressing worthlessness'
        },
        {
            'phrase': 'I want to drive my car off a cliff',
            'expected': 'high', 
            'current_result': 'none (failed)',
            'type': 'suicide method',
            'description': 'Specific suicide method - should trigger high alert'
        },
        {
            'phrase': "I'm going to stop eating until I die",
            'expected': 'high',
            'current_result': 'none (failed)', 
            'type': 'self-harm method',
            'description': 'Self-harm through starvation - serious crisis indicator'
        },
        {
            'phrase': 'I want to kill myself',
            'expected': 'high',
            'current_result': 'high (passes)',
            'type': 'direct suicide language',
            'description': 'Direct suicide statement - currently detected correctly'
        },
        {
            'phrase': 'Going to the store later',
            'expected': 'none',
            'current_result': 'none (correct)',
            'type': 'normal conversation',
            'description': 'Normal daily activity - should not trigger alerts'
        },
        {
            'phrase': 'This game boss is making me want to die',
            'expected': 'none',
            'current_result': 'unknown',
            'type': 'gaming context (potential false positive)',
            'description': 'Gaming frustration - should not trigger crisis alert'
        }
    ]
    
    print("="*80)
    print("🧪 MULTI-MODEL CRISIS DETECTION TEST")
    print("="*80)
    print(f"Testing {len(test_phrases)} phrases across multiple models")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test each model
    all_results = {}
    
    for model_key, config in tester.model_configs.items():
        print(f"🔄 Testing Model: {model_key}")
        print(f"📝 Description: {config['description']}")
        
        # Try to load the model
        if not tester.load_model(model_key):
            print(f"⚠️  Skipping {model_key} due to loading error")
            print("-" * 60)
            continue
        
        model_results = []
        
        for i, test_case in enumerate(test_phrases, 1):
            phrase = test_case['phrase'] 
            expected = test_case['expected']
            phrase_type = test_case['type']
            
            print(f"  Test {i}/{len(test_phrases)}: {phrase_type}")
            print(f"  📝 \"{phrase}\"")
            
            # Analyze with current model
            result = tester.analyze_text(phrase, model_key)
            
            if 'error' in result:
                print(f"  ❌ Error: {result['error']}")
                model_results.append({
                    'phrase': phrase,
                    'expected': expected,
                    'type': phrase_type,
                    'error': result['error'],
                    'processing_time': result.get('processing_time_ms', 0)
                })
            else:
                score = result.get('max_score', 0)
                processing_time = result.get('processing_time_ms', 0)
                
                print(f"  ⚡ Time: {processing_time:.1f}ms | Score: {score:.3f}")
                
                # Determine if this would catch the crisis
                if expected == 'high':
                    threshold = 0.4
                    would_catch = score > threshold
                    status = "✅ CATCH" if would_catch else "❌ MISS"
                elif expected == 'none':
                    threshold = 0.4
                    would_false_positive = score > threshold
                    status = "❌ FALSE+" if would_false_positive else "✅ CORRECT"
                else:
                    status = "📊 ANALYZE"
                
                print(f"  🔍 {status}")
                
                model_results.append({
                    'phrase': phrase,
                    'expected': expected,
                    'type': phrase_type,
                    'score': score,
                    'processing_time': processing_time,
                    'would_catch': would_catch if expected == 'high' else not would_false_positive if expected == 'none' else None,
                    'full_result': result
                })
            
            print()
        
        # Calculate model performance
        successful_tests = [r for r in model_results if 'error' not in r]
        if successful_tests:
            avg_time = np.mean([r['processing_time'] for r in successful_tests])
            
            # Count improvements for currently failing phrases
            improvements = 0
            for r in successful_tests:
                # Find the matching test case
                matching_test = next((t for t in test_phrases if t['phrase'] == r['phrase']), None)
                if matching_test and matching_test['current_result'].endswith('(failed)'):
                    if r.get('would_catch', False):
                        improvements += 1
            
            total_failed = len([t for t in test_phrases if t['current_result'].endswith('(failed)')])
            
            print(f"📊 Model Performance Summary:")
            print(f"   ⚡ Avg Processing Time: {avg_time:.1f}ms")
            print(f"   📈 Would Fix: {improvements}/{total_failed} failing phrases")
        
        all_results[model_key] = model_results
        
        # Clear GPU memory between models
        if tester.use_gpu:
            torch.cuda.empty_cache()
        
        print("-" * 60)
        print()
    
    # Overall analysis
    print("="*80)
    print("📋 OVERALL ANALYSIS")
    print("="*80)
    
    # Find best performing models
    model_scores = {}
    for model_key, results in all_results.items():
        if not results or 'error' in results[0]:
            continue
            
        successful_results = [r for r in results if 'error' not in r]
        failed_improvements = 0
        false_positives = 0
        avg_time = 0
        
        if successful_results:
            avg_time = np.mean([r['processing_time'] for r in successful_results])
            
            for r in successful_results:
                # Check if this fixes a currently failing phrase
                matching_test = next((t for t in test_phrases if t['phrase'] == r['phrase']), None)
                if matching_test and matching_test['current_result'].endswith('(failed)'):
                    if r.get('would_catch', False):
                        failed_improvements += 1
                
                # Check for false positives
                if r['expected'] == 'none' and not r.get('would_catch', True):
                    false_positives += 1
        
        total_failed = len([t for t in test_phrases if t['current_result'].endswith('(failed)')])
        improvement_rate = failed_improvements / max(total_failed, 1)
        
        model_scores[model_key] = {
            'improvement_rate': improvement_rate,
            'failed_improvements': failed_improvements,
            'false_positives': false_positives,
            'avg_time': avg_time,
            'total_tests': len(successful_results)
        }
    
    # Rank models
    ranked_models = sorted(
        model_scores.items(), 
        key=lambda x: (x[1]['improvement_rate'], -x[1]['false_positives'], -x[1]['avg_time']),
        reverse=True
    )
    
    print("🏆 Model Rankings (by improvement potential):")
    for i, (model_key, scores) in enumerate(ranked_models[:5], 1):
        config = tester.model_configs[model_key]
        print(f"{i}. {model_key}")
        print(f"   📝 {config['description']}")
        print(f"   📈 Improvements: {scores['failed_improvements']}/{len([t for t in test_phrases if t['current_result'].endswith('(failed)')])} ({scores['improvement_rate']:.1%})")
        print(f"   ⚡ Avg Time: {scores['avg_time']:.1f}ms")
        print(f"   ❌ False Positives: {scores['false_positives']}")
        print()
    
    # Save detailed results
    results_file = f"multi_model_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'system_info': sys_info,
                'model_configs': tester.model_configs,
                'test_results': all_results,
                'model_scores': model_scores,
                'ranked_models': ranked_models
            }, f, indent=2, default=str)
        print(f"💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️  Could not save results file: {e}")
    
    return all_results, ranked_models

if __name__ == "__main__":
    try:
        print("🔧 Ash Crisis Detection - Multi-Model Evaluation")
        print("🖥️  Optimized for Debian 12 + RTX 3060 + 64GB RAM")
        print()
        
        results, rankings = test_multiple_models()
        print("\n✅ Multi-model testing complete!")
        
        if rankings:
            best_model = rankings[0][0]
            print(f"\n🏆 Best performing model: {best_model}")
            print("📝 Check detailed results above for implementation guidance")
        
        # Cleanup GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("💡 Make sure you have the required dependencies:")
        print("   pip install sentence-transformers scikit-learn")
        
    input("\nPress Enter to exit...")