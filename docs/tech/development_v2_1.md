# 🛠️ Ash Ecosystem Development Guide v2.1 (Centralized Architecture)

**Repository:** https://github.com/the-alphabet-cartel/ash  
**Discord Community:** https://discord.gg/alphabetcartel  
**Website:** https://alphabetcartel.org

This guide covers development workflows, best practices, and contribution guidelines for the Ash crisis detection ecosystem using the centralized architecture.

---

## 📋 Development Overview

The Ash ecosystem uses a **centralized submodule-based architecture** that allows for both independent component development and coordinated ecosystem-wide changes. All components run as Docker containers on a single Linux server for optimal performance and simplified management.

### 🏗️ Development Architecture

```
ash/                          # Main ecosystem repository
├── ash-bot/                  # Discord bot submodule
├── ash-nlp/                  # NLP server submodule
├── ash-dash/                 # Dashboard submodule
├── ash-thrash/               # Testing suite submodule
├── docker-compose.yml        # Master orchestration
├── docker-compose.dev.yml    # Development configuration
├── .env.template             # Centralized configuration template
├── scripts/                  # Development automation scripts
│   ├── setup-dev.sh         # Development environment setup
│   ├── health-check.sh      # System health validation
│   └── test-integration.sh  # Cross-component testing
└── docs/                     # Ecosystem documentation
```

### 🖥️ Infrastructure Overview

**Production Environment:**
- **Server:** Linux (Debian 12) at 10.20.30.253
- **Hardware:** Ryzen 7 5800X, RTX 3060, 64GB RAM
- **Deployment:** Docker containers with unified orchestration
- **Networking:** Internal Docker networks for service communication

**Development Environment:**
- **Local Development:** Docker-based development environment
- **Testing:** Comprehensive integration testing with ash-thrash
- **Monitoring:** Local Prometheus/Grafana stack for development

---

## 🚀 Getting Started

### Prerequisites

**Development Environment Requirements:**
- **Git** with submodule support
- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Node.js 18+** (for dashboard development)
- **Python 3.9+** (for Python components)
- **Your preferred editor** (Atom, VS Code, etc.)

**Access Requirements:**
- GitHub account with access to The Alphabet Cartel organization
- Discord bot token (for bot development)
- Claude API key (for NLP development)
- Understanding of Docker container basics

### Initial Development Setup

**1. Clone the Ecosystem:**
```bash
# Clone with all submodules
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Verify submodules are present
ls -la  # Should show ash-bot, ash-nlp, ash-dash, ash-thrash directories
git submodule status  # Verify all submodules are properly initialized
```

**2. Setup Development Environment:**
```bash
# Run automated setup script (Linux/Mac)
bash scripts/setup-dev.sh

# Or manual setup for each component
for component in ash-bot ash-nlp ash-dash ash-thrash; do
  echo "Setting up $component..."
  cd $component
  
  # Copy environment template
  cp .env.template .env.dev
  
  # Setup Python virtual environment (for Python components)
  if [ -f "requirements.txt" ]; then
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements-dev.txt
    deactivate
  fi
  
  # Setup Node.js dependencies (for dashboard)
  if [ -f "package.json" ]; then
    npm install
  fi
  
  cd ..
done
```

**3. Configure Development Environment:**

**For Windows Development (using your preferred setup):**
```powershell
# Using Atom editor and GitHub Desktop
# Clone repository using GitHub Desktop
# Navigate to project directory

# Setup each component
foreach ($component in @("ash-bot", "ash-nlp", "ash-dash", "ash-thrash")) {
    Write-Host "Setting up $component..."
    cd $component
    
    # Copy environment template
    Copy-Item .env.template .env.dev
    
    # Setup Python environment if needed
    if (Test-Path "requirements.txt") {
        python -m venv venv
        .\venv\Scripts\activate
        pip install -r requirements-dev.txt
        deactivate
    }
    
    # Setup Node.js dependencies if needed
    if (Test-Path "package.json") {
        npm install
    }
    
    cd ..
}
```

**4. Configure Master Development Environment:**

**Create Development Configuration (.env.dev):**
```bash
# =============================================================================
# Ash Ecosystem Development Configuration
# =============================================================================

# Infrastructure Configuration
ASH_SERVER_IP=localhost
ASH_ENVIRONMENT=development

# =============================================================================
# Discord Bot Configuration (ash-bot)
# =============================================================================
DISCORD_TOKEN=your_dev_discord_bot_token
DISCORD_GUILD_ID=your_dev_guild_id

# Internal service URLs (container networking)
NLP_SERVER_URL=http://ash-nlp:8881
TESTING_SERVER_URL=http://ash-thrash:8884

# Development Settings
LOG_LEVEL=DEBUG
ENABLE_CRISIS_DETECTION=true

# =============================================================================
# NLP Server Configuration (ash-nlp)
# =============================================================================
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20240229

# GPU Configuration (adjust for your local GPU)
CUDA_VISIBLE_DEVICES=0
GPU_MEMORY_FRACTION=0.6  # Conservative for development

# Development Settings
NLP_WORKERS=2  # Reduced for development
ENABLE_MOCK_RESPONSES=false  # Set to true for offline development
LOG_LEVEL=DEBUG

# =============================================================================
# Dashboard Configuration (ash-dash)
# =============================================================================
NODE_ENV=development
ENABLE_SSL=false  # Disable SSL for local development
DASH_ENABLE_HOT_RELOAD=true

# Internal service connections
ASH_BOT_API=http://ash-bot:8882
ASH_NLP_API=http://ash-nlp:8881
ASH_TESTING_API=http://ash-thrash:8884

# Development Settings
CACHE_TTL=10  # Short cache for development
LOG_LEVEL=debug

# =============================================================================
# Testing Configuration (ash-thrash)
# =============================================================================
TEST_ENVIRONMENT=development
COMPREHENSIVE_TEST_ENABLED=true
QUICK_TEST_ENABLED=true

# Reduced test load for development
TEST_PHRASES_COUNT=50  # Reduced from 350 for faster development

# =============================================================================
# Database Configuration
# =============================================================================
GLOBAL_POSTGRES_DB=ash_development
GLOBAL_POSTGRES_USER=ash_dev
GLOBAL_POSTGRES_PASSWORD=ash_dev_password

# =============================================================================
# Development Tools
# =============================================================================
ENABLE_METRICS=true
ENABLE_DEBUG_LOGGING=true
```

**Create Development Docker Compose (docker-compose.dev.yml):**
```yaml
version: '3.8'

# Override for development environment
services:
  ash-nlp:
    environment:
      - LOG_LEVEL=DEBUG
      - ENABLE_MOCK_RESPONSES=false
      - GPU_MEMORY_FRACTION=0.6
    volumes:
      - ./ash-nlp/src:/app/src:cached  # Live code reloading
    ports:
      - "8881:8881"
      - "9092:9092"  # Metrics
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'

  ash-bot:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - ./ash-bot/src:/app/src:cached
    ports:
      - "8882:8882"
      - "9091:9091"  # Metrics

  ash-dash:
    environment:
      - NODE_ENV=development
      - DASH_ENABLE_HOT_RELOAD=true
      - LOG_LEVEL=debug
    volumes:
      - ./ash-dash/src:/app/src:cached
      - ./ash-dash/public:/app/public:cached
    ports:
      - "8883:8883"
      - "3000:3000"  # Development server
    command: npm run dev

  ash-thrash:
    environment:
      - LOG_LEVEL=DEBUG
      - TEST_PHRASES_COUNT=50
    volumes:
      - ./ash-thrash/src:/app/src:cached
    ports:
      - "8884:8884"

  # Development database with reduced resources
  postgres:
    environment:
      GLOBAL_POSTGRES_DB: ash_development
      GLOBAL_POSTGRES_USER: ash_dev
      GLOBAL_POSTGRES_PASSWORD: ash_dev_password
    ports:
      - "5432:5432"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'

  # Development Redis
  redis:
    ports:
      - "6379:6379"
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
```

---

## 🔧 Development Workflows

### Working with Submodules

**Understanding Submodule Structure:**
```bash
# View current submodule status
git submodule status

# Update all submodules to latest commits
git submodule update --remote --merge

# Update specific submodule
cd ash-bot
git pull origin main
cd ..
git add ash-bot
git commit -m "Update ash-bot submodule to latest"
```

**Component-Specific Development:**
```bash
# Work on specific component
cd ash-bot
git checkout -b feature/new-detection-pattern

# Make changes, test locally
docker-compose -f ../docker-compose.yml -f ../docker-compose.dev.yml build ash-bot
docker-compose -f ../docker-compose.yml -f ../docker-compose.dev.yml up -d ash-bot

# Test changes
curl http://localhost:8882/health

# Commit and push
git add .
git commit -m "Add new detection pattern for gaming terminology"
git push origin feature/new-detection-pattern

# Create pull request in component repository
# After merge, update main repository
cd ..
git submodule update --remote ash-bot
git add ash-bot
git commit -m "Update ash-bot with new detection pattern"
git push origin main
```

### Local Development Environment

**Starting Development Environment:**
```bash
# Start complete development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start individual components for focused development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up ash-nlp -d  # NLP server only
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up ash-dash -d  # Dashboard only

# View logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# View specific service logs
docker-compose logs -f ash-bot
```

**Development with Local Services:**
```bash
# For Python components (ash-bot, ash-nlp, ash-thrash)
cd ash-bot
source venv/bin/activate  # Windows: venv\Scripts\activate
python src/main.py  # Run locally instead of in container

# For Node.js dashboard
cd ash-dash
npm run dev  # Development server with hot reload

# For hybrid development (some services local, others in containers)
# Start dependencies in containers
docker-compose up -d postgres redis

# Run your component locally with container dependencies
cd ash-bot
python src/main.py
```

### Cross-Component Integration Testing

**Testing Component Communication:**
```bash
# Ensure all services are running
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for services to initialize
sleep 30

# Run health checks
./scripts/health-check.sh

# Run integration tests
cd ash-thrash
python src/integration_testing.py

# Test specific workflows
python src/test_bot_nlp_integration.py
python src/test_dashboard_integration.py
```

**Manual Integration Testing:**
```bash
# Test Discord bot → NLP server communication
curl -X POST http://localhost:8882/api/test-nlp-connection

# Test dashboard → all services communication
curl http://localhost:8883/api/system/health

# Test crisis detection end-to-end
curl -X POST http://localhost:8881/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel like nobody would miss me", "context": "test"}'

# Test container networking
docker exec ash-bot curl -f http://ash-nlp:8881/health
docker exec ash-dash curl -f http://ash-bot:8882/health
```

---

## 🧪 Testing & Quality Assurance

### Automated Testing Strategy

**Component-Level Testing:**
```bash
# Python components
cd ash-bot
source venv/bin/activate
python -m pytest tests/ -v --coverage

cd ../ash-nlp
source venv/bin/activate
python -m pytest tests/ -v --coverage

cd ../ash-thrash
source venv/bin/activate
python -m pytest tests/ -v --coverage

# Dashboard testing
cd ../ash-dash
npm test
npm run test:integration
npm run test:e2e
```

**Container Integration Testing:**
```bash
# Test container communication
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Wait for initialization
sleep 30

# Comprehensive ecosystem testing
cd ash-thrash
python src/comprehensive_testing.py --development

# Quick validation testing
python src/quick_validation.py

# Performance testing
python src/performance_testing.py --duration=300  # 5-minute test
```

**Load Testing:**
```bash
# Simulate high-volume crisis detection
cd ash-thrash
python src/load_testing.py --concurrent=20 --duration=300

# Test dashboard under load
cd ash-dash
npm run test:load

# Monitor container performance during testing
docker stats
```

### Testing Best Practices

**Before Committing:**
1. **Run component tests** for your specific changes
2. **Test container integration** with related components
3. **Validate against test suite** using ash-thrash
4. **Check container resource usage** and performance impact
5. **Update tests** for new functionality

**Testing Guidelines:**
- **Write tests first** for new features (TDD approach)
- **Test container networking** for service communication
- **Test edge cases** especially for crisis detection logic
- **Mock external services** for isolated unit testing
- **Include performance benchmarks** for critical paths
- **Test with realistic data** including LGBTQIA+ community language

### Container-Specific Testing

**Container Health Testing:**
```bash
# Test container startup and health
docker-compose build ash-bot
docker-compose up -d ash-bot
sleep 15

# Verify health endpoint
curl http://localhost:8882/health

# Test container restart resilience
docker-compose restart ash-bot
sleep 10
curl http://localhost:8882/health
```

**Resource Usage Testing:**
```bash
# Monitor container resource usage during tests
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Test resource limits
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
# Run load tests and monitor resource consumption
```

### Continuous Integration

**Pre-commit Hooks:**
```bash
# Install pre-commit hooks for code quality
pip install pre-commit
pre-commit install

# This will run:
# - Code formatting (black, prettier)
# - Linting (flake8, eslint)
# - Type checking (mypy, typescript)
# - Container build tests
# - Basic integration tests
```

**CI/CD Pipeline:**
- **Component CI:** Individual component testing on push
- **Container Build:** Automated Docker image building and testing
- **Integration CI:** Cross-component testing on main repository changes
- **Deployment CI:** Automated deployment to staging environment

---

## 🚀 Development Environment Options

### Local Development Approaches

**Option 1: Full Container Development**
```bash
# All services running in containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Advantages:
# - Complete production-like environment
# - All services running consistently
# - Easy to test full integration
# - No dependency on local installations

# Disadvantages:
# - Requires significant local resources
# - Slower development iteration
# - More complex debugging
```

**Option 2: Hybrid Development**
```bash
# Run your component locally, others in containers
docker-compose up -d postgres redis ash-nlp  # Dependencies in containers

# Run your component locally
cd ash-bot
source venv/bin/activate
export NLP_SERVER_URL=http://localhost:8881
python src/main.py  # Local bot with container dependencies

# Advantages:
# - Fast development iteration
# - Easy debugging and profiling
# - Use production-like dependencies
# - Flexible development workflow

# Disadvantages:
# - Environment setup complexity
# - Potential version mismatches
# - Network configuration requirements
```

**Option 3: Component-Focused Development**
```bash
# Develop single component with minimal dependencies
cd ash-nlp

# Use mocked dependencies for isolated development
export ENABLE_MOCK_RESPONSES=true
python src/main.py

# Advantages:
# - Fastest development iteration
# - Minimal resource requirements
# - Focused testing
# - Easy unit testing

# Disadvantages:
# - Limited integration testing
# - Potential integration issues
# - Requires good mocking strategy
```

### Development Tools & Setup

**For Windows Development (Your Environment):**
```powershell
# Using Atom and GitHub Desktop workflow

# 1. Clone repository using GitHub Desktop
# 2. Open project in Atom
# 3. Setup development environment

# PowerShell setup script for Windows development
$components = @("ash-bot", "ash-nlp", "ash-dash", "ash-thrash")

foreach ($component in $components) {
    Write-Host "Setting up $component for development..."
    
    Set-Location $component
    
    # Copy development environment
    if (Test-Path ".env.template") {
        Copy-Item .env.template .env.dev
        Write-Host "Created .env.dev for $component"
    }
    
    # Setup Python virtual environment
    if (Test-Path "requirements.txt") {
        python -m venv venv
        .\venv\Scripts\activate
        pip install -r requirements-dev.txt
        Write-Host "Python environment setup for $component"
        deactivate
    }
    
    # Setup Node.js dependencies
    if (Test-Path "package.json") {
        npm install
        Write-Host "Node.js dependencies installed for $component"
    }
    
    Set-Location ..
}

Write-Host "Development environment setup complete!"

# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
Write-Host "Containers started. Services will be available shortly."
```

**Docker Desktop Configuration for Development:**
```yaml
# Recommended Docker Desktop settings for development
# Settings → Resources → Advanced
# Memory: 16GB (or 50% of total RAM)
# CPUs: 6-8 cores
# Swap: 4GB
# Disk image size: 100GB

# Enable Kubernetes (optional, for advanced development)
# Enable experimental features for better performance
```

---

## 📊 Development Monitoring & Debugging

### Logging & Debugging

**Centralized Development Logging:**
```bash
# View logs from all containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Component-specific logs
docker-compose logs -f ash-bot
docker-compose logs -f ash-nlp

# Filter logs by level
docker-compose logs | grep ERROR
docker-compose logs | grep DEBUG

# Real-time log monitoring
docker-compose logs -f --tail=100
```

**Debug Mode Configuration:**
```bash
# Enable debug mode for all components
export ASH_DEBUG_MODE=true

# Component-specific debug settings
export ASH_BOT_DEBUG=true
export ASH_NLP_DEBUG=true
export ASH_DASH_DEBUG=true

# Start with debug configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Performance Monitoring

**Development Performance Dashboard:**
```bash
# Access local monitoring
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090

# Monitor container performance
docker stats

# Monitor application metrics
curl http://localhost:9091/metrics  # Bot metrics
curl http://localhost:9092/metrics  # NLP metrics
```

**Resource Usage Monitoring:**
```bash
# Monitor container resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# System resource monitoring
# Linux/Mac:
htop
# Windows:
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
```

### Debugging Workflows

**Container Debugging:**
```bash
# Debug specific container
docker exec -it ash-bot bash

# Inside container debugging
ps aux  # Check running processes
netstat -tulpn  # Check network connections
curl http://ash-nlp:8881/health  # Test internal networking

# Debug with logs
docker-compose logs ash-bot --follow --tail=50
```

**Application Debugging:**
```bash
# Debug Discord bot locally
cd ash-bot
source venv/bin/activate

# Set debug environment
export DISCORD_TOKEN=your_dev_token
export LOG_LEVEL=DEBUG
export NLP_SERVER_URL=http://localhost:8881

# Run with debugger
python -m pdb src/main.py

# Or use IDE debugging with breakpoints
```

**Network Debugging:**
```bash
# Test container networking
docker network inspect ash_ash_network

# Test service-to-service communication
docker exec ash-bot ping ash-nlp
docker exec ash-bot curl http://ash-nlp:8881/health

# Debug DNS resolution
docker exec ash-bot nslookup ash-nlp
```

---

## 🤝 Contribution Guidelines

### Code Standards

**Python Code Style:**
```bash
# Use Black for formatting
black src/ tests/

# Use flake8 for linting
flake8 src/ tests/ --max-line-length=88

# Use mypy for type checking
mypy src/

# Use isort for import sorting
isort src/ tests/
```

**JavaScript/TypeScript Style:**
```bash
# Use Prettier for formatting
npm run format

# Use ESLint for linting
npm run lint

# Type checking for TypeScript
npm run type-check
```

**Docker Best Practices:**
- **Multi-stage builds** for optimized images
- **Layer caching** for faster builds
- **Health checks** for all services
- **Resource limits** for development and production
- **Security scanning** for vulnerabilities

**General Guidelines:**
- **Follow existing patterns** in each component
- **Write comprehensive docstrings** for all functions
- **Include type hints** for Python code
- **Comment complex logic** especially for crisis detection
- **Use meaningful variable names** and function names
- **Test container integration** for service changes

### Pull Request Process

**1. Preparation:**
```bash
# Create feature branch
cd ash-bot  # or relevant component
git checkout -b feature/improve-gaming-terminology-detection

# Make changes following code standards
# Write/update tests
# Update documentation
# Test in container environment
```

**2. Testing:**
```bash
# Run component tests
python -m pytest tests/ -v

# Build and test container
docker-compose build ash-bot
docker-compose up -d ash-bot
curl http://localhost:8882/health

# Run integration tests
cd ../ash-thrash
python src/comprehensive_testing.py

# Validate performance
python src/performance_testing.py --duration=120
```

**3. Documentation:**
- **Update README.md** if functionality changes
- **Update API documentation** for endpoint changes
- **Update team guide** if operational procedures change
- **Include migration guide** for breaking changes
- **Document container configuration** changes

**4. Pull Request:**
- **Use descriptive title** summarizing the change
- **Include detailed description** with context and rationale
- **Reference related issues** using GitHub issue numbers
- **Include testing results** and performance impact
- **Document container changes** and resource requirements
- **Request appropriate reviewers** from development team

### Code Review Guidelines

**As a Reviewer:**
- **Test the changes** in your local environment
- **Verify container builds** and health checks pass
- **Check for security implications** especially in crisis detection
- **Validate performance impact** using ash-thrash testing
- **Ensure documentation is updated** appropriately
- **Test container integration** with other services

**Review Checklist:**
- [ ] Code follows established patterns and standards
- [ ] Tests are comprehensive and pass
- [ ] Container builds successfully
- [ ] Health checks work properly
- [ ] Documentation is updated appropriately
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is acceptable
- [ ] Container resource usage is reasonable
- [ ] Changes align with project goals and community needs

---

## 🔄 Release & Deployment Workflow

### Development Release Cycle

**Weekly Development Releases:**
1. **Monday:** Development planning and sprint kickoff
2. **Wednesday:** Mid-week integration testing and review
3. **Friday:** Feature freeze and comprehensive testing
4. **Weekend:** Container building and staging deployment

**Component Release Process:**
```bash
# 1. Feature completion
cd ash-bot
git checkout main
git pull origin main

# 2. Create release branch
git checkout -b release/v1.4.3

# 3. Update version and changelog
# Edit version files and CHANGELOG.md
# Update container configurations if needed

# 4. Container testing
cd ..
docker-compose build ash-bot
docker-compose up -d ash-bot

# 5. Comprehensive testing
cd ash-thrash
python src/comprehensive_testing.py --component=ash-bot

# 6. Create pull request for release
# 7. After approval, tag and release
cd ash-bot
git tag v1.4.3
git push origin v1.4.3
```

**Ecosystem Release Coordination:**
```bash
# Update main repository with latest component versions
cd ash
git submodule update --remote --merge

# Build complete ecosystem
docker-compose build

# Test complete ecosystem
docker-compose up -d
./scripts/health-check.sh

# Create ecosystem release
git tag v2.1.1
git push origin v2.1.1

# Deploy to staging
./scripts/deploy-staging.sh v2.1.1

# After validation, deploy to production
./scripts/deploy-production.sh v2.1.1
```

### Container Management in Development

**Building and Managing Containers:**
```bash
# Build specific component
docker-compose build ash-bot

# Build all components
docker-compose build

# Force rebuild without cache
docker-compose build --no-cache

# Pull latest base images
docker-compose pull

# Clean up old images
docker image prune -f
```

**Container Versioning:**
```bash
# Tag containers for development
docker tag ash_ash-bot:latest ash_ash-bot:dev
docker tag ash_ash-nlp:latest ash_ash-nlp:dev

# Build with specific tags
docker-compose build --build-arg VERSION=dev

# Push to development registry (if using external registry)
# docker push ash_ash-bot:dev
```

---

## 🛡️ Security & Privacy in Development

### Security Best Practices

**Container Security:**
- **Never commit secrets** to version control
- **Use environment variables** for all sensitive configuration
- **Scan images** for vulnerabilities regularly
- **Run containers as non-root** when possible
- **Use network isolation** for service communication

**API Security:**
- **Validate all inputs** especially for crisis detection analysis
- **Implement rate limiting** for all API endpoints
- **Use HTTPS/TLS** for external communications
- **Authenticate internal APIs** for service-to-service communication

**Development Security:**
```bash
# Security scanning
pip install safety
safety check  # Check for known vulnerabilities

npm audit  # Check Node.js dependencies

# Container security scanning
docker scan ash_ash-bot:latest
```

### Privacy-Preserving Development

**Testing with Sensitive Data:**
```bash
# Use synthetic test data
cd ash-thrash
python src/generate_synthetic_test_data.py

# Never use real crisis conversations for testing
# Always anonymize any community data used for improvement
```

**Crisis Detection Ethics:**
- **Minimize false positives** to avoid unnecessary interventions
- **Optimize for community safety** over system convenience
- **Respect user autonomy** while providing appropriate support
- **Maintain transparency** about system capabilities and limitations

---

## 📚 Development Resources

### Documentation

**Technical Documentation:**
- **[Ecosystem Setup](../tech/ecosystem_setup_v2_1.md)** - Complete system configuration
- **[Troubleshooting Guide](../tech/troubleshooting_v2_1.md)** - Common development issues
- **[Implementation Guide](../tech/implementation_v2_1.md)** - Technical implementation details

**Community Resources:**
- **Discord #development** - Real-time development discussion
- **GitHub Discussions** - Feature requests and architectural discussions
- **Team Meetings** - Weekly development coordination calls

### External Resources

**Development Tools:**
- **[Docker Documentation](https://docs.docker.com/)** - Container development
- **[Docker Compose Documentation](https://docs.docker.com/compose/)** - Multi-container applications
- **[Discord.py Documentation](https://discordpy.readthedocs.io/)** - Discord bot development
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - API development
- **[React Documentation](https://reactjs.org/docs/)** - Dashboard frontend

**AI/ML Resources:**
- **[Anthropic Claude Documentation](https://docs.anthropic.com/)** - AI integration
- **[PyTorch Documentation](https://pytorch.org/docs/)** - Machine learning
- **[Transformers Documentation](https://huggingface.co/docs/transformers/)** - NLP models

### Community & Support

**Getting Help:**
- **Discord #tech-support** - Technical questions and troubleshooting
- **GitHub Issues** - Bug reports and feature requests
- **Team Mentorship** - Paired programming and guidance for new contributors
- **Office Hours** - Weekly open discussion with senior developers

**Contributing Back:**
- **Code Contributions** - Features, bug fixes, optimizations
- **Documentation** - Guides, examples, tutorials
- **Testing** - Quality assurance and validation
- **Community Support** - Helping other developers and users
- **Container Optimization** - Performance and resource improvements

---

**This development guide provides the foundation for contributing to the Ash crisis detection ecosystem using the centralized architecture. The container-based approach simplifies development while maintaining production-like environments, ensuring that every line of code you write has the potential to help save lives and support LGBTQIA+ community members in their most vulnerable moments.**

**🌈 Together, we're building technology that strengthens chosen family bonds and creates safer spaces for everyone.**

---

**Built with 🖤 for The Alphabet Cartel**  
**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org