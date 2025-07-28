# 🛠️ Ash Ecosystem Development Guide

**Repository:** https://github.com/the-alphabet-cartel/ash  
**Discord Community:** https://discord.gg/alphabetcartel  
**Website:** http://alphabetcartel.org

This guide covers development workflows, best practices, and contribution guidelines for the Ash crisis detection ecosystem.

---

## 📋 Development Overview

The Ash ecosystem uses a **submodule-based architecture** that allows for both independent component development and coordinated ecosystem-wide changes. This guide will help you navigate development workflows for different scenarios.

### 🏗️ Development Architecture

```
ash/                          # Main ecosystem repository
├── ash-bot/                  # Discord bot submodule
├── ash-nlp/                  # NLP server submodule
├── ash-dash/                 # Dashboard submodule
├── ash-thrash/               # Testing suite submodule
├── docker-compose.yml        # Master orchestration
├── docker-compose.dev.yml    # Development configuration
├── scripts/                  # Development automation scripts
└── docs/                     # Ecosystem documentation
```

---

## 🚀 Getting Started

### Prerequisites

**Development Environment:**
- **Git** with submodule support
- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Node.js 18+** (for ash-dash)
- **Python 3.9+** (for ash-bot, ash-nlp, ash-thrash)
- **Your preferred editor** (Atom, VS Code, etc.)

**Access Requirements:**
- GitHub account with access to The Alphabet Cartel organization
- Discord bot token (for bot development)
- Claude API key (for NLP development)
- Access to development servers (optional)

### Initial Setup

**1. Clone the Ecosystem:**
```bash
# Clone with all submodules
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Verify submodules are present
ls -la  # Should show ash-bot, ash-nlp, ash-dash, ash-thrash directories
```

**2. Setup Development Environment:**
```bash
# Run automated setup script
bash scripts/setup_dev_environment.sh

# Or manual setup for each component
cd ash-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.template .env
cd ..

cd ash-nlp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.template .env
cd ..

cd ash-dash
npm install
cp .env.template .env
cd ..

cd ash-thrash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.template .env
cd ..
```

**3. Configure Development Environment:**
```bash
# Configure each component for development
for component in ash-bot ash-nlp ash-dash ash-thrash; do
  echo "Configuring $component..."
  cd $component
  # Edit .env with development configuration
  # (Use your preferred editor)
  cd ..
done
```

---

## 🔄 Development Workflows

### Workflow 1: Component-Specific Development

**When to use:** Working on features specific to one component (bot commands, NLP models, dashboard UI, test cases)

**Process:**
```bash
# 1. Work directly in the component repository
cd ash-bot  # or ash-nlp, ash-dash, ash-thrash

# 2. Create feature branch
git checkout -b feature/new-crisis-command

# 3. Make your changes
# Edit files, add features, fix bugs

# 4. Test locally
python -m pytest tests/  # For Python components
npm test                  # For Node.js components

# 5. Commit and push to component repository
git add .
git commit -m "Add new crisis intervention command"
git push origin feature/new-crisis-command

# 6. Create PR in component repository
gh pr create --title "Add new crisis intervention command"

# 7. After PR is merged, update main repository
cd ..  # Back to main ash repository
git add ash-bot
git commit -m "Update ash-bot to include new crisis command"
git push origin main
```

### Workflow 2: Ecosystem-Wide Development

**When to use:** Changes affecting multiple components, integration features, system-wide configuration

**Process:**
```bash
# 1. Work from main repository
cd ash

# 2. Create feature branch in main repository
git checkout -b feature/improved-crisis-pipeline

# 3. Update submodules to latest
git submodule update --remote --merge

# 4. Make changes across components
cd ash-bot
# Make bot changes
git add . && git commit -m "Bot: Improve crisis detection pipeline"

cd ../ash-nlp
# Make NLP changes
git add . && git commit -m "NLP: Add new analysis models"

cd ../ash-dash
# Make dashboard changes
git add . && git commit -m "Dashboard: Update crisis visualization"

# 5. Push component changes
cd ../ash-bot && git push origin main
cd ../ash-nlp && git push origin main
cd ../ash-dash && git push origin main

# 6. Update main repository with new submodule references
cd ..  # Back to main repository
git add ash-bot ash-nlp ash-dash
git commit -m "Ecosystem: Implement improved crisis detection pipeline"
git push origin feature/improved-crisis-pipeline

# 7. Create PR in main repository
gh pr create --title "Implement improved crisis detection pipeline"
```

### Workflow 3: Fork-Based Development

**When to use:** External contributors, major experimental features

**Process:**
```bash
# 1. Fork main repository and relevant component repositories
gh repo fork the-alphabet-cartel/ash
gh repo fork the-alphabet-cartel/ash-bot  # If working on bot

# 2. Clone your fork
git clone --recursive https://github.com/YOUR_USERNAME/ash.git
cd ash

# 3. Update submodule URLs to point to your forks (if needed)
git config submodule.ash-bot.url https://github.com/YOUR_USERNAME/ash-bot.git

# 4. Follow standard development process
# ... make changes ...

# 5. Submit PRs to upstream repositories
```

---

## 🧪 Testing Strategies

### Unit Testing

**Component-Level Testing:**
```bash
# Test specific component
cd ash-bot
python -m pytest tests/unit/ -v

cd ../ash-nlp
python -m pytest tests/unit/ -v

cd ../ash-dash
npm run test:unit

cd ../ash-thrash
python -m pytest tests/unit/ -v
```

### Integration Testing

**Cross-Component Testing:**
```bash
# From main repository
cd ash

# Start test environment
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d

# Run comprehensive integration tests
cd ash-thrash
python src/comprehensive_testing.py --integration-mode

# Test specific integrations
python scripts/test_bot_nlp_integration.py
python scripts/test_dashboard_api_integration.py
```

### Development Testing

**Quick Development Validation:**
```bash
# Quick health check across all components
bash scripts/dev_health_check.sh

# Quick validation test
cd ash-thrash
python src/quick_validation.py

# Test component communication
python scripts/test_component_connectivity.py
```

---

## 🎯 Development Best Practices

### Code Quality

**Python Components (ash-bot, ash-nlp, ash-thrash):**
```bash
# Use consistent formatting
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
pylint src/

# Security scanning
bandit -r src/
```

**Node.js Components (ash-dash):**
```bash
# Formatting and linting
npm run lint
npm run format

# Type checking (if using TypeScript)
npm run type-check

# Security audit
npm audit
```

### Documentation Standards

**Code Documentation:**
- All functions and classes must have docstrings
- Include type hints for Python code
- Document API endpoints with OpenAPI/Swagger
- Add inline comments for complex logic

**Example Python Docstring:**
```python
def analyze_crisis_message(message: str, context: Dict[str, Any]) -> CrisisAnalysis:
    """
    Analyze a Discord message for crisis indicators.
    
    Args:
        message: The message text to analyze
        context: Additional context including user_id, channel_id, etc.
    
    Returns:
        CrisisAnalysis object containing risk level and confidence
        
    Raises:
        ValueError: If message is empty or context is missing required fields
    """
```

### Git Commit Standards

**Commit Message Format:**
```
<component>: <type>: <description>

[optional body]

[optional footer]
```

**Examples:**
```bash
# Component-specific changes
git commit -m "bot: feat: add new crisis intervention command"
git commit -m "nlp: fix: improve accuracy for depression detection"
git commit -m "dash: style: update crisis alert styling"
git commit -m "test: add: comprehensive anxiety detection tests"

# Ecosystem-wide changes
git commit -m "ecosystem: feat: implement cross-component health monitoring"
git commit -m "config: update: standardize environment configuration"
```

### Branch Naming

**Branch Naming Convention:**
```bash
# Feature branches
feature/crisis-command-improvements
feature/nlp-model-updates
feature/dashboard-redesign

# Bug fixes
fix/bot-memory-leak
fix/nlp-timeout-handling
fix/dashboard-authentication

# Experimental features
experiment/voice-channel-detection
experiment/multilingual-support
```

---

## 🔧 Development Tools and Scripts

### Automation Scripts

**Development Environment Setup:**
```bash
# Setup all components for development
bash scripts/setup_dev_environment.sh

# Reset development environment
bash scripts/reset_dev_environment.sh

# Update all submodules
bash scripts/update_submodules.sh
```

**Testing and Validation:**
```bash
# Run all tests across ecosystem
bash scripts/run_all_tests.sh

# Health check all services
bash scripts/health_check_all.sh

# Generate development report
bash scripts/generate_dev_report.sh
```

### IDE Configuration

**VS Code Settings (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "./ash-bot/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "git.submodules": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/node_modules": true,
    "**/.venv": true
  }
}
```

**Atom Configuration (for your setup):**
```coffee
# Add to ~/.atom/config.cson
"*":
  core:
    projectHome: "C:\\Projects"
  "git-plus":
    submodules: true
  "python-tools":
    python: "C:\\Projects\\ash\\ash-bot\\venv\\Scripts\\python.exe"
```

### Docker Development

**Development Docker Compose:**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  ash-bot-dev:
    build: 
      context: ./ash-bot
      dockerfile: Dockerfile.dev
    volumes:
      - ./ash-bot:/app
      - ./ash-bot/data:/app/data
    environment:
      - FLASK_ENV=development
      - DEBUG=true
    ports:
      - "8882:8882"
    
  ash-nlp-dev:
    build:
      context: ./ash-nlp
      dockerfile: Dockerfile.dev
    volumes:
      - ./ash-nlp:/app
      - ./ash-nlp/models:/app/models
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    ports:
      - "8881:8881"
```

**Development Commands:**
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs in development
docker-compose logs -f ash-bot-dev

# Execute commands in development containers
docker-compose exec ash-bot-dev python -m pytest
docker-compose exec ash-nlp-dev python scripts/test_models.py
```

---

## 🤝 Contributing Guidelines

### Pull Request Process

**1. Pre-PR Checklist:**
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No sensitive information in commits
- [ ] Submodule references updated (if needed)

**2. PR Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Component(s) Affected
- [ ] ash-bot
- [ ] ash-nlp
- [ ] ash-dash
- [ ] ash-thrash
- [ ] ecosystem-wide

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)

## Additional Notes
```

### Code Review Guidelines

**For Reviewers:**
- Focus on logic, security, and maintainability
- Check for proper error handling
- Verify tests cover new functionality
- Ensure documentation is updated
- Validate cross-component impacts

**For Contributors:**
- Respond to feedback promptly
- Make requested changes in separate commits
- Keep PRs focused and atomic
- Include rationale for design decisions

### Release Process

**1. Component Release:**
```bash
# Create release branch
cd ash-bot
git checkout -b release/v1.2.0

# Update version numbers
# Update CHANGELOG.md
# Final testing

# Merge to main and tag
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git push origin main --tags
```

**2. Ecosystem Release:**
```bash
# Update main repository with latest component versions
cd ash
git submodule update --remote --merge

# Create ecosystem release
git tag v2.1.1
git push origin main --tags

# Update deployment
bash scripts/deploy_production.sh v2.1.1
```

---

## 🚨 Troubleshooting Development Issues

### Common Submodule Issues

**Submodule out of sync:**
```bash
cd ash
git submodule sync
git submodule update --init --recursive
```

**Submodule has uncommitted changes:**
```bash
cd ash-bot
git stash
cd ..
git submodule update
cd ash-bot
git stash pop
```

**Submodule pointing to wrong commit:**
```bash
cd ash-bot
git checkout main
git pull origin main
cd ..
git add ash-bot
git commit -m "Update ash-bot submodule reference"
```

### Environment Issues

**Python virtual environment problems:**
```bash
# Reset virtual environment
cd ash-bot
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

**Docker development issues:**
```bash
# Reset Docker development environment
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
```

**Node.js dependency issues:**
```bash
cd ash-dash
rm -rf node_modules package-lock.json
npm install
```

### Integration Testing Issues

**Services not communicating:**
```bash
# Check network connectivity
docker network ls
docker network inspect ash_ash-network

# Test service endpoints
curl http://localhost:8881/health  # NLP
curl http://localhost:8882/health  # Bot
curl http://localhost:8883/health  # Dashboard
curl http://localhost:8884/health  # Testing
```

**Database connection issues:**
```bash
# Reset development database
docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS ash_dev; CREATE DATABASE ash_dev;"
```

---

## 📚 Additional Resources

### Documentation
- [Architecture Guide](./architecture.md) - System design and component relationships
- [API Documentation](../ash-thrash/docs/api.md) - Complete API reference
- [Deployment Guide](./deployment.md) - Production deployment procedures

### External Resources
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Documentation](https://vuejs.org/guide/)
- [Docker Documentation](https://docs.docker.com/)

### Community
- **Discord**: https://discord.gg/alphabetcartel
- **GitHub Discussions**: Use GitHub discussions for feature requests and questions
- **Issues**: Report bugs and technical issues via GitHub Issues

---

**Happy coding! 🖤 Built with love for LGBTQIA+ gaming communities by [The Alphabet Cartel](https://discord.gg/alphabetcartel)**