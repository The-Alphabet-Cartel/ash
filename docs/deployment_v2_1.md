# 🚀 Ash Ecosystem Deployment Guide v2.1 (Submodule Structure)

**Updated for GitHub Submodules** | **Repository:** https://github.com/the-alphabet-cartel/ash

## 📋 Deployment Overview (Updated)

The Ash ecosystem now uses GitHub submodules for better organization and development workflow. This guide covers deployment scenarios for the new structure.

### 🏗️ New Repository Structure

```
ash/                          # Main orchestration repository
├── ash-bot/                  # Discord bot (submodule)
├── ash-nlp/                  # NLP server (submodule)  
├── ash-dash/                 # Dashboard (submodule)
├── ash-thrash/               # Testing suite (submodule)
├── docker-compose.yml        # Master orchestration
├── .gitmodules              # Submodule configuration
└── docs/                    # Ecosystem documentation
```

## 🎯 Production Deployment (Updated)

### Method 1: Complete Ecosystem Deployment (Recommended)

**Step 1: Clone Main Repository**
```bash
# Linux Server (10.20.30.253)
cd /opt
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Windows Server (10.20.30.16) 
cd C:\Production
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash
```

**Step 2: Configure Environment**
```bash
# Configure each component
for component in ash-bot ash-nlp ash-dash ash-thrash; do
  cd $component
  cp .env.template .env
  # Edit .env with component-specific configuration
  cd ..
done
```

**Step 3: Distributed Deployment**
```bash
# Linux Server (10.20.30.253) - Bot Only
cd /opt/ash
docker-compose up ash-bot -d

# Windows Server (10.20.30.16) - NLP, Dashboard, Testing
cd C:\Production\ash
docker-compose up ash-nlp ash-dash ash-thrash -d
```

### Method 2: Individual Component Deployment

**For focused maintenance or development:**

```bash
# Deploy specific components
cd ash

# Bot only (Linux server)
cd ash-bot && docker-compose up -d && cd ..

# NLP only (Windows server)  
cd ash-nlp && docker-compose up -d && cd ..

# Dashboard only (Windows server)
cd ash-dash && docker-compose up -d && cd ..

# Testing only (Windows server)
cd ash-thrash && docker-compose up -d && cd ..
```

### Method 3: Development Deployment

**For development work:**

```bash
# Clone for development
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Setup development environment for all components
bash scripts/setup_dev_environment.sh

# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## 🔄 Maintenance and Updates (New Procedures)

### Updating Individual Components

**Update specific component:**
```bash
cd ash
git submodule update --remote ash-bot  # Update bot only
git add ash-bot
git commit -m "Update ash-bot to latest version"
git push origin main
```

**Update all components:**
```bash
cd ash
git submodule update --remote --merge
git add -A
git commit -m "Update all submodules to latest versions"
git push origin main
```

### Rolling Updates

**Zero-downtime component updates:**
```bash
# Update NLP server
cd ash-nlp
git pull origin main
docker-compose up -d --no-deps ash-nlp

# Update dashboard
cd ../ash-dash  
git pull origin main
docker-compose up -d --no-deps ash-dash

# Update testing suite
cd ../ash-thrash
git pull origin main
docker-compose up -d --no-deps ash-thrash
```

## 🧪 Testing Procedures (Updated)

### Integration Testing

**Test complete ecosystem:**
```bash
cd ash

# Run comprehensive integration test
cd ash-thrash
python src/comprehensive_testing.py --full-ecosystem

# Test component communication
python scripts/test_component_integration.py
```

**Test individual components:**
```bash
# Test bot functionality
cd ash-bot
pytest tests/integration/

# Test NLP server
cd ../ash-nlp
pytest tests/integration/

# Test dashboard
cd ../ash-dash
npm run test:integration
```

### Health Monitoring

**Updated health check procedures:**
```bash
# Check all services from main repository
cd ash
bash scripts/health_check_all.sh

# Individual component health
curl http://10.20.30.253:8882/health  # Bot
curl http://10.20.30.16:8881/health   # NLP
curl http://10.20.30.16:8883/health   # Dashboard  
curl http://10.20.30.16:8884/health   # Testing
```

## 🔧 Configuration Management (Updated)

### Environment Configuration

**Master configuration template:**
```bash
# Create master .env in main repository
cat > .env << 'EOF'
# Master Ash Ecosystem Configuration

# Global Settings
ENVIRONMENT=production
LOG_LEVEL=info
ENABLE_MONITORING=true

# Network Configuration
INTERNAL_NETWORK=172.20.0.0/16
BOT_SERVER_IP=10.20.30.253
AI_SERVER_IP=10.20.30.16

# Component Status
ASH_BOT_ENABLED=true
ASH_NLP_ENABLED=true
ASH_DASH_ENABLED=true
ASH_THRASH_ENABLED=true
EOF

# Distribute to components
bash scripts/distribute_config.sh
```

### Secret Management

**Updated secret distribution:**
```bash
# Secure secret management
echo "DISCORD_TOKEN=your_token" | tee ash-bot/.env
echo "CLAUDE_API_KEY=your_key" | tee ash-nlp/.env
echo "DATABASE_URL=your_db" | tee ash-dash/.env

# Verify secret distribution
bash scripts/verify_secrets.sh
```

## 🔄 CI/CD Integration (Updated)

### GitHub Actions for Submodules

**Automated deployment workflow:**
```yaml
# .github/workflows/deploy.yml
name: Deploy Ash Ecosystem

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive
    
    - name: Deploy to production
      run: |
        # Deploy to Linux server
        ssh deploy@10.20.30.253 "cd /opt/ash && git pull --recurse-submodules && docker-compose up ash-bot -d"
        
        # Deploy to Windows server  
        ssh deploy@10.20.30.16 "cd C:\Production\ash && git pull --recurse-submodules && docker-compose up ash-nlp ash-dash ash-thrash -d"
```

### Submodule Auto-Update

**Automated submodule updates:**
```bash
# Create auto-update script
cat > scripts/auto_update_submodules.sh << 'EOF'
#!/bin/bash
cd /opt/ash
git submodule update --remote --merge
if [[ -n $(git status --porcelain) ]]; then
  git add -A
  git commit -m "Auto-update submodules $(date)"
  git push origin main
  
  # Restart services with updates
  docker-compose up -d
fi
EOF

# Schedule in crontab
echo "0 2 * * * /opt/ash/scripts/auto_update_submodules.sh" | crontab -
```

## 📊 Monitoring and Observability (Updated)

### Centralized Monitoring

**Monitor all components from main repository:**
```bash
# Create monitoring script
cat > scripts/monitor_ecosystem.sh << 'EOF'
#!/bin/bash
echo "=== Ash Ecosystem Health Check ==="
echo "Timestamp: $(date)"
echo

for service in "Bot:10.20.30.253:8882" "NLP:10.20.30.16:8881" "Dashboard:10.20.30.16:8883" "Testing:10.20.30.16:8884"; do
  name=$(echo $service | cut -d: -f1)
  host=$(echo $service | cut -d: -f2)
  port=$(echo $service | cut -d: -f3)
  
  if curl -s -f "http://$host:$port/health" > /dev/null; then
    echo "✅ $name: Healthy"
  else
    echo "❌ $name: Unhealthy"
  fi
done

echo
echo "=== Submodule Status ==="
git submodule status
EOF

chmod +x scripts/monitor_ecosystem.sh
```

### Log Aggregation

**Centralized logging:**
```bash
# Collect logs from all components
bash scripts/collect_logs.sh

# View aggregated logs
tail -f logs/ecosystem.log
```

## 🚨 Troubleshooting (Updated)

### Common Submodule Issues

**Submodule not updating:**
```bash
cd ash
git submodule deinit -f ash-bot
git submodule update --init ash-bot
```

**Submodule pointing to wrong commit:**
```bash
cd ash-bot
git checkout main
git pull origin main
cd ..
git add ash-bot
git commit -m "Fix ash-bot submodule reference"
```

**Missing submodules after clone:**
```bash
git submodule update --init --recursive
```

### Service-Specific Issues

**Component not starting:**
```bash
# Check component-specific logs
cd ash-nlp
docker-compose logs

# Restart specific component
docker-compose restart ash-nlp
```

**Network connectivity issues:**
```bash
# Test inter-component communication
cd ash
python scripts/test_connectivity.py
```

## 🔐 Security Considerations (Updated)

### Submodule Security

**Verify submodule integrity:**
```bash
# Check submodule URLs
cat .gitmodules

# Verify signatures
git submodule foreach 'git verify-commit HEAD'
```

### Access Control

**Repository access management:**
```bash
# Ensure proper access to all repositories
gh auth status
gh repo list the-alphabet-cartel
```

---

**This updated deployment guide reflects the new submodule structure and provides comprehensive procedures for managing the Ash ecosystem as an integrated but modular system.**