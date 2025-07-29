#!/usr/bin/env python3
"""
Test script to evaluate unitary/toxic-bert on crisis detection phrases
Optimized for Debian 12 Linux Server with RTX 3060, 64GB RAM, Ryzen 7 5800X
Compare against current sentiment analysis approach
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import time
import json
import psutil
from datetime import datetime
import sys
import os

# Set up proper CUDA environment
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True  # Optimize for consistent input sizes
    torch.backends.cuda.matmul.allow_tf32 = True  # Allow TF32 for faster inference

class ToxicBertTester:
    def __init__(self, use_gpu=True):
        """Initialize toxic-bert model and tokenizer"""
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = torch.device('cuda' if self.use_gpu else 'cpu')
        
        print("🔄 Loading unitary/toxic-bert model...")
        print(f"🖥️  Device: {self.device}")
        
        if self.use_gpu:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"🎮 GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        
        self.model_name = "unitary/toxic-bert" 
        
        # Load with device mapping for optimal GPU usage
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.use_gpu else torch.float32,  # Use half precision on GPU
                device_map="auto" if self.use_gpu else None
            )
            
            if not self.use_gpu:
                self.model = self.model.to(self.device)
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Trying fallback loading method...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model = self.model.to(self.device)
        
        self.model.eval()  # Set to evaluation mode
        
        # Toxic-bert output labels
        self.labels = [
            'toxicity', 'severe_toxicity', 'obscene', 'threat', 'insult', 'identity_attack'
        ]
        
        print("✅ Model loaded successfully!")
        
        # Warm up the model for accurate timing
        if self.use_gpu:
            print("🔥 Warming up GPU...")
            self._warmup()
        
    def _warmup(self):
        """Warm up the model for consistent timing"""
        warmup_text = "This is a warmup text for the model."
        for _ in range(3):
            self.analyze_toxicity(warmup_text, verbose=False)
        torch.cuda.synchronize()  # Ensure all operations complete
        
    def analyze_toxicity(self, text, verbose=True):
        """Analyze text for toxicity using toxic-bert"""
        start_time = time.time()
        
        # Tokenize and predict
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            if self.use_gpu:
                torch.cuda.synchronize()  # Ensure accurate timing
                
            outputs = self.model(**inputs)
            scores = outputs.logits.squeeze()
            
            if self.use_gpu:
                torch.cuda.synchronize()
                scores = scores.cpu()  # Move to CPU for numpy operations
                
        # Apply sigmoid to get probabilities (toxic-bert uses sigmoid, not softmax)
        scores_np = scores.numpy()
        probabilities = 1 / (1 + np.exp(-scores_np))
        
        processing_time = (time.time() - start_time) * 1000
        
        # Create results dictionary
        results = {}
        for label, prob in zip(self.labels, probabilities):
            results[label] = float(prob)
            
        results['processing_time_ms'] = processing_time
        results['max_toxicity'] = float(max(probabilities))
        results['crisis_relevant_score'] = max(results['threat'], results['severe_toxicity'])
        
        if verbose and self.use_gpu:
            # Add GPU memory usage
            memory_used = torch.cuda.memory_allocated() / 1024**2  # MB
            results['gpu_memory_mb'] = memory_used
        
        return results
    
    def analyze_batch(self, texts, batch_size=8):
        """Analyze multiple texts in batches for efficiency"""
        print(f"🔄 Processing {len(texts)} texts in batches of {batch_size}...")
        
        all_results = []
        start_time = time.time()
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_results = []
            
            for text in batch:
                result = self.analyze_toxicity(text, verbose=False)
                batch_results.append(result)
            
            all_results.extend(batch_results)
            
            if self.use_gpu:
                torch.cuda.empty_cache()  # Clear GPU cache between batches
        
        total_time = (time.time() - start_time) * 1000
        avg_time = total_time / len(texts)
        
        print(f"⚡ Batch processing complete: {avg_time:.1f}ms per text average")
        return all_results

def get_system_info():
    """Get system information for performance context"""
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
        info['gpu_memory_allocated_mb'] = torch.cuda.memory_allocated() / 1024**2
    else:
        info['gpu_available'] = False
        
    return info

def test_crisis_phrases():
    """Test toxic-bert on the phrases that are currently failing"""
    
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
    tester = ToxicBertTester()
    
    # Test phrases from ash-thrash failures
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
        # Add some comparison phrases
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
        },
        # Additional test cases
        {
            'phrase': 'Nobody would miss me if I was gone',
            'expected': 'high',
            'current_result': 'unknown',
            'type': 'burden ideation',
            'description': 'Another form of burden ideation'
        },
        {
            'phrase': 'I hate myself so much',
            'expected': 'medium',
            'current_result': 'unknown', 
            'type': 'self-hatred',
            'description': 'Self-hatred expression - concerning but not immediate crisis'
        }
    ]
    
    print("="*80)
    print("🧪 TOXIC-BERT CRISIS DETECTION TEST")
    print("="*80)
    print(f"Testing {len(test_phrases)} phrases to evaluate toxic-bert performance")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results_summary = []
    
    for i, test_case in enumerate(test_phrases, 1):
        phrase = test_case['phrase']
        expected = test_case['expected']
        current = test_case['current_result']
        phrase_type = test_case['type']
        description = test_case['description']
        
        print(f"Test {i}/{len(test_phrases)}: {phrase_type}")
        print(f"📝 Phrase: \"{phrase}\"")
        print(f"📖 Context: {description}")
        print(f"🎯 Expected: {expected} | Current System: {current}")
        
        # Analyze with toxic-bert
        toxicity_results = tester.analyze_toxicity(phrase)
        
        # Display results
        print(f"⚡ Processing Time: {toxicity_results['processing_time_ms']:.1f}ms")
        if 'gpu_memory_mb' in toxicity_results:
            print(f"🎮 GPU Memory: {toxicity_results['gpu_memory_mb']:.1f}MB")
            
        print("📊 Toxic-BERT Scores:")
        
        for label, score in toxicity_results.items():
            if label not in ['processing_time_ms', 'max_toxicity', 'crisis_relevant_score', 'gpu_memory_mb']:
                if score > 0.7:
                    status = "🔴"  # High
                elif score > 0.4:
                    status = "🟡"  # Medium  
                elif score > 0.2:
                    status = "🟠"  # Low-medium
                else:
                    status = "🟢"  # Low
                print(f"   {status} {label.replace('_', ' ').title()}: {score:.3f}")
        
        print(f"🎯 Crisis Relevant Score: {toxicity_results['crisis_relevant_score']:.3f}")
        print(f"📈 Max Toxicity: {toxicity_results['max_toxicity']:.3f}")
        
        # Determine if toxic-bert would catch this
        crisis_score = toxicity_results['crisis_relevant_score']
        max_score = toxicity_results['max_toxicity']
        
        # Use adaptive thresholds based on expected level
        if expected == 'high':
            threshold = 0.4  # Lower threshold for high-priority phrases
            would_catch = crisis_score > threshold or max_score > 0.6
            status = "✅ WOULD CATCH" if would_catch else "❌ WOULD MISS"
            print(f"🔍 Analysis: {status} (crisis threshold: {threshold})")
        elif expected == 'medium':
            threshold = 0.3
            would_catch = crisis_score > threshold or max_score > 0.4
            status = "✅ WOULD CATCH" if would_catch else "❌ WOULD MISS"
            print(f"🔍 Analysis: {status} (medium threshold: {threshold})")
        elif expected == 'none':
            threshold = 0.4
            would_false_positive = crisis_score > threshold
            status = "❌ FALSE POSITIVE" if would_false_positive else "✅ CORRECT NEGATIVE"
            print(f"🔍 Analysis: {status} (false positive threshold: {threshold})")
            
        # Determine improvement status
        is_improvement = False
        if expected in ['high', 'medium'] and current.endswith('(failed)'):
            is_improvement = would_catch
        elif expected == 'none':
            is_improvement = not would_false_positive
            
        results_summary.append({
            'phrase': phrase,
            'type': phrase_type,
            'expected': expected,
            'current': current,
            'toxic_bert_score': crisis_score,
            'max_toxicity': max_score,
            'would_improve': is_improvement,
            'processing_time': toxicity_results['processing_time_ms'],
            'scores': {label: toxicity_results[label] for label in tester.labels}
        })
        
        print("-" * 60)
        print()
    
    # Summary analysis
    print("="*80)
    print("📋 SUMMARY ANALYSIS")
    print("="*80)
    
    improvements = sum(1 for r in results_summary if r['would_improve'] and r['current'].endswith('(failed)'))
    total_failed = sum(1 for r in results_summary if r['current'].endswith('(failed)'))
    avg_processing_time = np.mean([r['processing_time'] for r in results_summary])
    
    print(f"📈 Potential Improvements: {improvements}/{total_failed} currently failing phrases")
    print(f"⚡ Average Processing Time: {avg_processing_time:.1f}ms per phrase")
    
    if tester.use_gpu:
        print(f"🎮 GPU Acceleration: Enabled ({torch.cuda.get_device_name(0)})")
    else:
        print("🖥️  GPU Acceleration: Disabled (CPU-only)")
    
    print("\n🔍 Detailed Results:")
    for result in results_summary:
        improvement_status = "✅ IMPROVEMENT" if result['would_improve'] and result['current'].endswith('(failed)') else "📊 ANALYSIS"
        phrase_short = result['phrase'][:45] + "..." if len(result['phrase']) > 45 else result['phrase']
        print(f"   {improvement_status}: {phrase_short} (Score: {result['toxic_bert_score']:.3f}, Time: {result['processing_time']:.1f}ms)")
    
    # Performance analysis
    print(f"\n⚡ Performance Analysis:")
    if avg_processing_time < 50:
        print("   🚀 EXCELLENT: Very fast processing suitable for real-time use")
    elif avg_processing_time < 100:
        print("   ✅ GOOD: Fast processing acceptable for production")
    elif avg_processing_time < 200:
        print("   🟡 MODERATE: Acceptable processing speed")
    else:
        print("   ⚠️  SLOW: May need optimization for production use")
    
    # Final recommendation
    print(f"\n💡 Recommendation:")
    improvement_rate = improvements / max(total_failed, 1)
    
    if improvement_rate >= 0.8:  # 80% improvement
        print("   🎯 HIGHLY RECOMMENDED: Toxic-BERT shows significant improvement")
        print("   📝 Next Step: Implement as Model 2 in your ensemble")
        print("   🔧 Suggested threshold: 0.4 for crisis_relevant_score")
    elif improvement_rate >= 0.5:  # 50% improvement  
        print("   ✅ RECOMMENDED: Toxic-BERT shows moderate improvement")
        print("   📝 Next Step: Consider implementing with adjusted thresholds")
        print("   🔧 Suggested threshold: 0.3 for crisis_relevant_score")
    else:
        print("   ⚠️  LIMITED BENEFIT: Toxic-BERT may not significantly improve detection")
        print("   📝 Next Step: Consider other model options or approach")
        
    # Save detailed results
    results_file = f"toxic_bert_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'system_info': sys_info,
                'test_results': results_summary,
                'summary': {
                    'improvements': improvements,
                    'total_failed': total_failed,
                    'improvement_rate': improvement_rate,
                    'avg_processing_time': avg_processing_time
                }
            }, f, indent=2)
        print(f"\n💾 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save results file: {e}")
        
    return results_summary

if __name__ == "__main__":
    try:
        print("🔧 Ash Crisis Detection - Toxic-BERT Evaluation")
        print("🖥️  Optimized for Debian 12 + RTX 3060 + 64GB RAM")
        print()
        
        results = test_crisis_phrases()
        print("\n✅ Testing complete! Check results above.")
        
        # Cleanup GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("💡 Make sure you have the required dependencies:")
        print("   pip install torch transformers numpy psutil")
        print("   Or run: pip install -r requirements.txt")
        
    input("\nPress Enter to exit...")