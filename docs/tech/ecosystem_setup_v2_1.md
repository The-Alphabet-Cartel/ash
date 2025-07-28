# 🔧 Ash Ecosystem Setup Guide v2.1 (Updated for Submodules)

**Updated for the new submodule structure** | **Repository:** https://github.com/the-alphabet-cartel/ash

## 🚀 Quick Start (Complete Ecosystem)

### Prerequisites
- Docker and Docker Compose installed on both servers
- Access to The Alphabet Cartel GitHub organization
- Discord bot token and Claude API key configured
- Git with submodule support

### Method 1: Clone Complete Ecosystem (Recommended)

```bash
# Clone the main repository with all submodules
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Verify all submodules are present
ls -la
# Should show: ash-bot/ ash-nlp/ ash-dash/ ash-thrash/ directories

# If submodules didn't clone properly, initialize them
git submodule update --init --recursive
```

### Method 2: Add Submodules to Existing Repository

If you already have a main `ash` repository:

```bash
cd ash

# Add each component as a submodule
git submodule add https://github.com/the-alphabet-cartel/ash-bot.git ash-bot
git submodule add https://github.com/the-alphabet-cartel/ash-nlp.git ash-nlp
git submodule add https://github.com/the-alphabet-cartel/ash-dash.git ash-dash
git submodule add https://github.com/the-alphabet-cartel/ash-thrash.git ash-thrash

# Commit the submodule configuration
git add .gitmodules ash-bot ash-nlp ash-dash ash-thrash
git commit -m "Add Ash ecosystem components as submodules"
git push origin main
```

## 🔧 Updated Development Setup

### Environment Configuration (Each Component)

**Setup all components:**
```bash
# Update all submodules to latest
git submodule update --remote --merge

# Setup ash-bot (Discord Bot)
cd ash-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.template .env
# Edit .env with Discord token and configuration
cd ..

# Setup ash-nlp (NLP Server)
cd ash-nlp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.template .env
# Edit .env with Claude API key and GPU settings
cd ..

# Setup ash-dash (Dashboard)
cd ash-dash
npm install
cp .env.template .env
# Edit .env with API endpoints and configuration
cd ..

# Setup ash-thrash (Testing Suite)
cd ash-thrash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.template .env
# Edit .env with NLP server details
cd ..
```

## 🚀 Updated Production Deployment

### Server Distribution (Updated Commands)

**Linux Server (10.20.30.253) - Discord Bot:**
```bash
cd /opt/ash/ash-bot
docker-compose up -d

# Verify bot deployment
curl http://10.20.30.253:8882/health
```

**Windows Server (10.20.30.16) - NLP, Dashboard, Testing:**
```powershell
# Navigate to main ecosystem directory
cd C:\Production\ash

# Start NLP server
cd ash-nlp
docker-compose up -d

# Start dashboard  
cd ..\ash-dash
docker-compose up -d

# Start testing suite
cd ..\ash-thrash
docker-compose up -d

# Verify all services
curl http://10.20.30.16:8881/health  # NLP
curl http://10.20.30.16:8883/health  # Dashboard
curl http://10.20.30.16:8884/health  # Testing
```

### Orchestrated Deployment (Using Main Repository)

**From main ash repository:**
```bash
# Deploy entire ecosystem using master docker-compose
docker-compose up -d

# Or deploy specific services
docker-compose up -d ash-nlp ash-dash ash-thrash  # Windows server services
```

## 🔧 Updated Working with Submodules

### Common Operations (Updated)

**Update all submodules to latest:**
```bash
cd ash  # Main repository
git submodule update --remote --merge
```

**Pull changes in main repo and all submodules:**
```bash
git pull --recurse-submodules
```

**Make changes in a specific component:**
```bash
# Work on bot changes
cd ash-bot
git checkout main
# Make your changes
git add .
git commit -m "Your bot changes"
git push origin main

# Update main repository to reference new commit
cd ..  # Back to main repository
git add ash-bot
git commit -m "Update ash-bot submodule to latest"
git push origin main
```

**Work on single component only:**
```bash
# Clone just one component for focused development
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot
# Work on bot-specific changes
```

### Development Workflow (Updated)

**For component-specific changes:**
1. Work directly in the component's repository (ash-bot, ash-nlp, etc.)
2. Test changes locally in that component
3. Push changes to component repository
4. Update main repository submodule reference

**For ecosystem-wide changes:**
1. Work in the main `ash` repository
2. Make changes across multiple submodules as needed
3. Update and test with full ecosystem
4. Push changes to component repositories first
5. Update main repository with new submodule references

## 📊 Updated System Health Monitoring

### Health Check Endpoints (Updated)
```bash
# From main repository, check all services
curl http://10.20.30.253:8882/health  # Bot API
curl http://10.20.30.16:8881/health   # NLP Server
curl http://10.20.30.16:8883/health   # Dashboard
curl http://10.20.30.16:8884/health   # Testing Suite

# Or use the dashboard to monitor all services
open http://10.20.30.16:8883  # Access dashboard for system overview
```

## 🧪 Updated Testing Procedures

### Integration Testing (Updated)
```bash
# From main repository
cd ash-thrash
python src/comprehensive_testing.py

# Quick validation across ecosystem
python src/quick_validation.py

# Test specific component integration
cd ../ash-bot
pytest tests/integration/

cd ../ash-nlp
pytest tests/integration/
```

### Cross-Component Testing
```bash
# Test full crisis detection pipeline
cd ash
python scripts/test_full_pipeline.py

# Test dashboard integration
cd ash-dash
npm run test:integration

# Validate all component APIs
python scripts/validate_all_apis.py
```

## 🔄 Updated CI/CD for Submodules

### GitHub Actions (Updated)

**Main repository workflow:**
```yaml
name: Ash Ecosystem CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  update-submodules:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive
    
    - name: Update submodules
      run: |
        git submodule update --remote --merge
        git add -A
        git diff --staged --quiet || git commit -m "Auto-update submodules"
        git push

  test-ecosystem:
    runs-on: ubuntu-latest
    needs: update-submodules
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive
    
    - name: Test full ecosystem
      run: |
        docker-compose up -d
        sleep 30
        bash scripts/test_all_components.sh
```

## 🎯 Migration from Individual Repositories

### If you currently have separate repositories:

```bash
# Backup current individual repositories
mkdir backup
cp -r ash-bot backup/
cp -r ash-nlp backup/
cp -r ash-dash backup/
cp -r ash-thrash backup/

# Remove individual repository directories
rm -rf ash-bot ash-nlp ash-dash ash-thrash

# Clone new main repository with submodules
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Your existing .env files can be copied from backup
cp ../backup/ash-bot/.env ash-bot/
cp ../backup/ash-nlp/.env ash-nlp/
cp ../backup/ash-dash/.env ash-dash/
cp ../backup/ash-thrash/.env ash-thrash/
```

## 📚 Updated Documentation Structure

**Main Repository Documentation:**
- `README.md` - Ecosystem overview and setup
- `docs/deployment.md` - Complete deployment guide
- `docs/development.md` - Development workflow
- `docs/architecture.md` - System architecture

**Component Documentation:**
- `ash-bot/README.md` - Bot-specific documentation
- `ash-nlp/README.md` - NLP server documentation
- `ash-dash/README.md` - Dashboard documentation
- `ash-thrash/README.md` - Testing suite documentation

---

**This updated guide reflects the new submodule structure and provides clear paths for both ecosystem-wide development and component-specific work.**