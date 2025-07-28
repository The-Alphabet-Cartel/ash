# Ash - Crisis Detection and Community Support Bot

The complete ecosystem for The Alphabet Cartel's Discord crisis detection and community support system.

**Discord Community:** https://discord.gg/alphabetcartel  
**Website:** http://alphabetcartel.org  
**Organization:** https://github.com/the-alphabet-cartel

## 🏗️ Architecture Overview

The Ash ecosystem consists of four interconnected components working together to provide comprehensive crisis detection and community support:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │◄──►│   NLP Server    │◄──►│   Dashboard     │
│   (ash-bot)     │    │   (ash-nlp)     │    │   (ash-dash)    │
│                 │    │                 │    │                 │
│ 10.20.30.253    │    │ 10.20.30.16     │    │ 10.20.30.16     │
│ Port: 8882      │    │ Port: 8881      │    │ Port: 8883      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 ▲
                                 │
                       ┌─────────────────┐
                       │  Testing Suite  │
                       │  (ash-thrash)   │
                       │                 │
                       │ 10.20.30.16     │
                       │ Port: 8884      │
                       └─────────────────┘
```

## 📦 Components

### [ash-bot](./ash-bot) - Discord Bot
**Repository:** https://github.com/the-alphabet-cartel/ash-bot  
**Technology:** Python, Discord.py, Docker  
**API Port:** 8882

The main Discord bot that monitors conversations, detects crisis situations, and provides immediate support responses. Integrates with the NLP server for advanced language processing.

### [ash-nlp](./ash-nlp) - NLP Processing Server
**Repository:** https://github.com/the-alphabet-cartel/ash-nlp  
**Technology:** Python, FastAPI, Machine Learning, Docker  
**API Port:** 8881

Advanced natural language processing server that analyzes messages for crisis indicators using both keyword matching and machine learning models.

### [ash-dash](./ash-dash) - Analytics Dashboard
**Repository:** https://github.com/the-alphabet-cartel/ash-dash  
**Technology:** Node.js, Vue.js, Docker  
**Dashboard Port:** 8883

Real-time analytics dashboard providing insights into bot performance, crisis detection accuracy, and community health metrics.

### [ash-thrash](./ash-thrash) - Testing Suite
**Repository:** https://github.com/the-alphabet-cartel/ash-thrash  
**Technology:** Python, FastAPI, Docker  
**API Port:** 8884

Comprehensive 350-phrase testing suite that validates crisis detection accuracy and integrates with the dashboard for continuous quality assurance.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed on both servers
- Access to The Alphabet Cartel GitHub organization
- Discord bot token and Claude API key configured

### Clone with Submodules
```bash
# Clone the complete ecosystem
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# If already cloned, initialize submodules
git submodule update --init --recursive
```

### Development Setup
```bash
# Update all submodules to latest
git submodule update --remote

# Set up each component
cd ash-bot && python -m venv venv && source venv/bin/activate && pip install -r requirements-dev.txt
cd ../ash-nlp && python -m venv venv && source venv/bin/activate && pip install -r requirements-dev.txt  
cd ../ash-dash && npm install
cd ../ash-thrash && npm install

# Configure environment variables
cp .env.template .env  # In each repository
# Edit .env files for development configuration
```

### Production Deployment

**Bot:**
```bash
cd ash-bot
docker-compose up -d
```

**NLP, Dashboard, Testing:**
```bash
# Start NLP server
cd ash-nlp
docker-compose up -d

# Start dashboard  
cd ../ash-dash
docker-compose up -d

# Start testing suite
cd ../ash-thrash
docker-compose up -d
```

## 🔧 Working with Submodules

### Common Operations

**Update all submodules to latest:**
```bash
git submodule update --remote --merge
```

**Pull changes in main repo and all submodules:**
```bash
git pull --recurse-submodules
```

**Make changes in a submodule:**
```bash
cd ash-bot
# Make your changes
git add .
git commit -m "Your changes"
git push origin main

# Update main repo to point to new commit
cd ..
git add ash-bot
git commit -m "Update ash-bot submodule"
git push origin main
```

**Clone specific submodule only:**
```bash
git submodule update --init ash-bot
```

## 📊 System Status

### Health Check Endpoints
- **Bot API:** http://10.20.30.253:8882/health
- **NLP Server:** http://10.20.30.253:8881/health  
- **Dashboard:** http://10.20.30.253:8883/health
- **Testing Suite:** http://10.20.30.253:8884/health

### Monitoring
All services include health monitoring and logging. Access the dashboard at http://dashboard.alphatbetcartel.net for real-time system status.

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive test suite
cd ash-thrash
python src/comprehensive_testing.py

# Quick validation test  
python src/quick_validation.py
```

### Integration Testing
The testing suite validates communication between all components and measures crisis detection accuracy across 350 test phrases.

## 📚 Documentation

Each component includes detailed documentation:
- [Bot Documentation](./ash-bot/README.md)
- [NLP Server Documentation](./ash-nlp/README.md)  
- [Dashboard Documentation](./ash-dash/README.md)
- [Testing Suite Documentation](./ash-thrash/README.md)

## 🛠️ Development Environment

### For Windows Development
- **Editor:** Atom
- **Git Management:** GitHub Desktop
- **Docker:** Docker Desktop for Windows
- **Server Access:** Remote development via SSH/RDP

### Repository Structure
```
ash/                          # Main repository
├── ash-bot/                  # Discord bot submodule
├── ash-nlp/                  # NLP server submodule  
├── ash-dash/                 # Dashboard submodule
├── ash-thrash/               # Testing suite submodule
├── docker-compose.yml        # Orchestration for all services
├── .env.template             # Environment template
├── setup.sh                  # Setup script
└── docs/                     # Comprehensive documentation
    ├── deployment.md         # Deployment guide
    ├── development.md        # Development guide
    └── architecture.md       # System architecture
```

## 🤝 Contributing

1. **Fork the main repository** and relevant submodule repositories
2. **Create feature branches** in the appropriate submodule
3. **Test changes** using ash-thrash
4. **Update documentation** as needed
5. **Submit pull requests** to individual component repositories
6. **Update main repository** submodule references after merging

## 🔐 Security & Privacy

All crisis detection is performed with privacy-first principles. No personal data is stored permanently, and all processing follows community guidelines.

## 📞 Support

- **Discord Support:** https://discord.gg/alphabetcartel
- **Issues:** Submit to appropriate component repository
- **Documentation:** Comprehensive guides in each submodule

## 📜 License

Each component may have its own license. Please refer to individual repositories for specific licensing information.

---

**The Alphabet Cartel** - Building inclusive gaming communities through technology.  
🌈 **Discord:** https://discord.gg/alphabetcartel | 🌐 **Website:** http://alphabetcartel.org