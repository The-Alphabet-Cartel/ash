#!/bin/bash
# Debug script to check NLP server status and imports

echo "🔍 ASH-NLP DEBUG SCRIPT"
echo "======================="

echo "1. Checking if containers are running..."
docker ps --filter "name=ash" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n2. Checking recent container logs for import errors..."
docker logs ash-nlp --tail 50 | grep -E "(import|error|Error|Exception|failed|Failed)"

echo -e "\n3. Testing if we can access the Python environment..."
docker exec ash-nlp python -c "
try:
    from utils.scoring_helpers import extract_depression_score
    print('✅ extract_depression_score imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    
try:
    from utils.scoring_helpers import apply_comprehensive_false_positive_reduction
    print('✅ apply_comprehensive_false_positive_reduction imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
"

echo -e "\n4. Checking if crisis_analyzer is being used (causing the issue)..."
docker exec ash-nlp python -c "
import sys
sys.path.append('/app')

try:
    from analysis.crisis_analyzer import CrisisAnalyzer
    print('⚠️  CrisisAnalyzer is available - this might be causing the issue')
    print('   The error might be coming from CrisisAnalyzer, not the fallback code')
except ImportError as e:
    print('✅ CrisisAnalyzer not available - fallback code should work')
"

echo -e "\n5. Testing a simple NLP request..."
curl -s -X POST http://10.20.30.253:8881/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_id": "debug", "channel_id": "debug"}' | jq '.'

echo -e "\n6. Checking what's actually running..."
docker exec ash-nlp ps aux | grep python

echo -e "\n7. Quick fix suggestions:"
echo "   Option 1: Restart the container completely"
echo "   docker-compose down && docker-compose up -d"
echo ""
echo "   Option 2: Check if CrisisAnalyzer is the problem"
echo "   Look at the logs above - if CrisisAnalyzer is available, the error"
echo "   is coming from there, not your fallback code"
echo ""
echo "   Option 3: Force rebuild"
echo "   docker-compose build --no-cache ash-nlp"
echo "   docker-compose up -d"