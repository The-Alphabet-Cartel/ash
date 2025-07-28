# 🔥 Ash - Crisis Detection & Community Support Ecosystem

> *Comprehensive AI-powered crisis detection and community support system for LGBTQIA+ gaming communities*

[![Discord Bot](https://img.shields.io/badge/discord-bot-7289da)](https://github.com/the-alphabet-cartel/ash-bot)
[![NLP Server](https://img.shields.io/badge/nlp-server-green)](https://github.com/the-alphabet-cartel/ash-nlp)
[![Analytics Dashboard](https://img.shields.io/badge/analytics-dashboard-blue)](https://github.com/the-alphabet-cartel/ash-dash)
[![Testing Suite](https://img.shields.io/badge/testing-suite-orange)](https://github.com/the-alphabet-cartel/ash-thrash)
[![Docker](https://img.shields.io/badge/deployment-docker-2496ed)](https://docker.com/)

---

## 🌈 About The Alphabet Cartel

**The Alphabet Cartel** is an LGBTQIA+ Discord community centered around gaming, political advocacy, and community support. We believe in building inclusive spaces where chosen family can thrive through technology and connection.

- **Discord:** https://discord.gg/alphabetcartel
- **Website:** https://alphabetcartel.org
- **GitHub:** https://github.com/the-alphabet-cartel

---

## 🎯 Project Overview

**Ash** is a comprehensive crisis detection and community support ecosystem designed specifically for LGBTQIA+ gaming communities. Using advanced AI and machine learning, Ash provides real-time crisis detection, community support coordination, and analytics to help keep our chosen family safe.

### 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ash Ecosystem v2.1                          │
│                 (Centralized Architecture)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              Linux Server (10.20.30.253)                       │
│              Debian 12 | Ryzen 7 5800X                         │
│              RTX 3060 | 64GB RAM                                │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Discord Bot   │    │   NLP Server    │    │ Analytics   │  │
│  │   (ash-bot)     │◄───┤   (ash-nlp)     │◄───┤ Dashboard   │  │
│  │   Container     │    │   Container     │    │(ash-dash)   │  │
│  │   Port: 8882    │    │   Port: 8881    │    │ Port: 8883  │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                │                                │
│                                ▼                                │
│                         ┌─────────────┐                         │
│                         │ Testing     │                         │
│                         │ Suite       │                         │
│                         │(ash-thrash) │                         │
│                         │ Container   │                         │
│                         │ Port: 8884  │                         │
│                         └─────────────┘                         │
│                                                                 │
│                    ┌─────────────┐    ┌─────────────┐           │
│                    │ PostgreSQL  │    │    Redis    │           │
│                    │ Database    │    │    Cache    │           │
│                    │ Container   │    │ Container   │           │
│                    │ Port: 5432  │    │ Port: 6379  │           │
│                    └─────────────┘    └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### 🧩 Component Overview

| Component | Repository | Purpose | Port | Container |
|-----------|------------|---------|------|-----------|
| **ash-bot** | [ash-bot](https://github.com/the-alphabet-cartel/ash-bot) | Discord bot for real-time crisis detection | 8882 | ash-bot |
| **ash-nlp** | [ash-nlp](https://github.com/the-alphabet-cartel/ash-nlp) | AI/ML processing server with adaptive learning | 8881 | ash-nlp |
| **ash-dash** | [ash-dash](https://github.com/the-alphabet-cartel/ash-dash) | Analytics dashboard and management interface | 8883 | ash-dash |
| **ash-thrash** | [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash) | Comprehensive testing and validation suite | 8884 | ash-thrash |
| **postgres** | - | PostgreSQL database for all components | 5432 | ash-postgres |
| **redis** | - | Redis cache for session and application data | 6379 | ash-redis |

---

## 🚀 Quick Start

### Prerequisites

- **Linux Server** (Debian 12 recommended)
- **Docker** & Docker Compose
- **Git** with submodule support
- **NVIDIA GPU** with CUDA support (for NLP processing)
- **64GB RAM** (minimum 32GB)
- Access to The Alphabet Cartel GitHub organization

### One-Command Setup

```bash
# Clone complete ecosystem with all submodules
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Configure environment
cp .env.template .env
# Edit .env with your configuration (Discord token, Claude API key, etc.)

# Deploy complete ecosystem
docker-compose up -d

# Verify all services
./scripts/health-check.sh
```

### Detailed Setup

**1. System Preparation:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**2. Environment Configuration:**
```bash
# Copy environment template
cp .env.template .env

# Edit configuration with your settings
nano .env
```

**Essential Configuration:**
```bash
# Discord Bot
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_guild_id

# NLP Server
CLAUDE_API_KEY=your_claude_api_key
GPU_MEMORY_FRACTION=0.8

# Database
POSTGRES_PASSWORD=your_secure_database_password

# Dashboard Security
SESSION_SECRET=your_session_secret
JWT_SECRET=your_jwt_secret

# SSL (for production)
ENABLE_SSL=true
```

**3. Deployment:**
```bash
# Build and start all services
docker-compose build
docker-compose up -d

# Wait for services to initialize
sleep 60

# Run health check
./scripts/health-check.sh

# Run initial test
curl -X POST http://localhost:8884/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}'
```

---

## 🌟 Key Features

### 🤖 **Advanced Crisis Detection**
- **Real-time Analysis** - Instant processing of Discord messages using GPU acceleration
- **Adaptive Learning** - Continuous improvement through community feedback
- **Cultural Sensitivity** - Specialized understanding of LGBTQIA+ language and context
- **Multi-layered Approach** - Combines rule-based and AI-powered detection

### 📊 **Comprehensive Analytics**
- **Real-time Dashboard** - Live monitoring at https://dashboard.alphabetcartel.net
- **Performance Metrics** - Accuracy tracking and system health monitoring
- **Community Insights** - Anonymized trends and pattern analysis
- **Learning Analytics** - System improvement tracking and optimization

### 🧪 **Robust Testing Framework**
- **350+ Test Phrases** - Comprehensive validation across crisis scenarios
- **Automated Validation** - Continuous integration testing
- **Performance Benchmarking** - Regular accuracy and speed assessments
- **Regression Testing** - Ensures improvements don't break existing functionality

### 🔐 **Privacy & Security First**
- **No Personal Data Storage** - Privacy-preserving analysis only
- **Encrypted Communication** - Secure API connections between components
- **Audit Logging** - Comprehensive tracking for transparency
- **Community Guidelines** - Follows Discord TOS and community standards

### ⚡ **Centralized Architecture Benefits**
- **Simplified Management** - Single server deployment and maintenance
- **Optimized Performance** - Container-based communication with minimal latency
- **Unified Monitoring** - Centralized logging and health checking
- **Easy Scaling** - Docker-based horizontal scaling capabilities

---

## 🛠️ Development Environment

### Repository Structure

```
ash/                          # Main ecosystem repository
├── ash-bot/                  # Discord bot submodule
├── ash-nlp/                  # NLP server submodule
├── ash-dash/                 # Dashboard submodule
├── ash-thrash/               # Testing suite submodule
├── docker-compose.yml        # Master orchestration
├── .env.template             # Environment configuration template
├── scripts/                  # Automation and utility scripts
│   ├── health-check.sh       # System health validation
│   ├── backup.sh            # Comprehensive backup
│   ├── update.sh            # System update automation
│   └── emergency-recovery.sh # Emergency recovery procedures
└── docs/                    # Complete documentation
    ├── deployment_v2_1.md   # Deployment guide
    ├── development_v2_1.md  # Development workflow
    ├── team/team_guide_v2_1.md # Team operations guide
    └── tech/                # Technical documentation
```

### Development Workflow

**Local Development Setup:**
```bash
# Clone repository
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Setup development environment
cp .env.template .env.dev
# Configure for development (set LOG_LEVEL=DEBUG, etc.)

# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Monitor logs
docker-compose logs -f
```

**Working with Submodules:**
```bash
# Update all submodules to latest
git submodule update --remote --merge

# Work on specific component
cd ash-bot
git checkout -b feature/new-detection-pattern
# Make changes, test, commit
git push origin feature/new-detection-pattern

# Update main repository with new submodule reference
cd ..
git add ash-bot
git commit -m "Update ash-bot submodule"
git push origin main
```

**Testing Changes:**
```bash
# Run component tests
cd ash-bot && python -m pytest tests/
cd ../ash-nlp && python -m pytest tests/

# Run integration tests
cd ash-thrash
python src/comprehensive_testing.py

# Check system health
./scripts/health-check.sh
```

---

## 📚 Documentation

### 📖 **User Guides**
- **[Team Guide](docs/team/team_guide_v2_1.md)** - Crisis response team operations and best practices
- **[Deployment Guide](docs/deployment_v2_1.md)** - Production deployment procedures
- **[GitHub Release Guide](docs/git/github_release_v2_1.md)** - Release management and versioning

### 🔧 **Technical Documentation**
- **[Development Guide](docs/tech/development_v2_1.md)** - Development workflows and contribution guidelines
- **[Ecosystem Setup](docs/tech/ecosystem_setup_v2_1.md)** - Complete system configuration
- **[Troubleshooting Guide](docs/tech/troubleshooting_v2_1.md)** - Common issues and solutions
- **[Implementation Guide](docs/tech/implementation_v2_1.md)** - Technical implementation details

### 🧩 **Component Documentation**
- **[Bot Documentation](./ash-bot/README.md)** - Discord bot specific guide
- **[NLP Documentation](./ash-nlp/README.md)** - AI/ML server technical details
- **[Dashboard Documentation](./ash-dash/README.md)** - Analytics interface guide
- **[Testing Documentation](./ash-thrash/README.md)** - Testing framework usage

---

## 🤝 Contributing

### Getting Started

1. **Join our community** - https://discord.gg/alphabetcartel
2. **Fork the main repository** and relevant component repositories
3. **Read the development guide** - [docs/tech/development_v2_1.md](docs/tech/development_v2_1.md)
4. **Set up development environment** following the quick start guide
5. **Pick an issue** from the GitHub Issues or discuss new features in Discord

### Development Process

1. **Create feature branch** in the appropriate component repository
2. **Make changes** following coding standards and best practices
3. **Write/update tests** ensuring comprehensive validation
4. **Test integration** using ash-thrash comprehensive testing
5. **Update documentation** as needed for changes
6. **Submit pull request** to the component repository
7. **Update main repository** submodule reference after merge

### Community Guidelines

- **Be respectful** - Follow our community code of conduct
- **Privacy first** - Never commit sensitive data or personal information
- **Test thoroughly** - Use ash-thrash to validate all changes
- **Document changes** - Update relevant documentation
- **Ask questions** - Use Discord #tech-support for help

---

## 🔧 Configuration

### Environment Variables

The master `.env` file contains configuration for all components:

```bash
# =============================================================================
# Discord Bot Configuration
# =============================================================================
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_guild_id
NLP_SERVER_URL=http://ash-nlp:8881

# =============================================================================
# NLP Server Configuration
# =============================================================================
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229
GPU_MEMORY_FRACTION=0.8
NLP_WORKERS=6

# =============================================================================
# Dashboard Configuration
# =============================================================================
NODE_ENV=production
ENABLE_SSL=true
SESSION_SECRET=your_session_secret

# =============================================================================
# Database Configuration
# =============================================================================
POSTGRES_PASSWORD=your_database_password
THRASH_DATABASE_URL=postgresql://ash_user:your_password@postgres:5432/ash_production

# =============================================================================
# Testing Configuration
# =============================================================================
TEST_ENVIRONMENT=production
TARGET_ACCURACY=92.0
COMPREHENSIVE_TEST_ENABLED=true
```

### Service Ports

| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| ash-nlp | 8881 | 8881 | NLP API and health checks |
| ash-bot | 8882 | 8882 | Bot API and metrics |
| ash-dash | 8883 | 8883 | Dashboard web interface |
| ash-thrash | 8884 | 8884 | Testing API and results |
| postgres | 5432 | 5432 | Database connections |
| redis | 6379 | 6379 | Cache and session storage |

---

## 📊 System Status

### Live Monitoring

- **🖥️ Dashboard:** https://dashboard.alphabetcartel.net
- **🤖 Bot Status:** Monitored via Discord presence and API health
- **🧠 NLP Health:** Real-time API health checks and GPU monitoring
- **🧪 Testing Status:** Continuous validation reports and accuracy tracking

### Performance Metrics

- **Detection Accuracy:** >92% (target >90%)
- **False Positive Rate:** <4% (target <5%)
- **Response Time:** <2 seconds average
- **System Uptime:** >99.5% target
- **GPU Utilization:** Optimized for RTX 3060 performance

### Health Monitoring

```bash
# Quick health check
./scripts/health-check.sh

# Detailed system monitoring
docker-compose ps
docker stats

# Service-specific health
curl http://localhost:8881/health  # NLP Server
curl http://localhost:8882/health  # Discord Bot
curl -k https://localhost:8883/health  # Dashboard
curl http://localhost:8884/health  # Testing Suite
```

---

## 🔐 Security & Privacy

### Privacy Protection

- **No personal data storage** - Messages are analyzed in real-time without persistent storage
- **Anonymized metrics** - All analytics are aggregated and anonymized
- **Encrypted communications** - All inter-service communication uses secure Docker networks
- **Community consent** - Users can opt-out of analysis through Discord commands

### Security Measures

- **Container isolation** - All services run in isolated Docker containers
- **Network security** - Services communicate via private Docker networks
- **API authentication** - Internal API endpoints require authentication
- **Regular security updates** - Automated dependency updates and security patches
- **Audit logging** - Comprehensive logging for transparency and debugging

### Data Handling

- **Temporary processing only** - Crisis detection analysis without data retention
- **Secure credential management** - Environment variables and Docker secrets
- **Database encryption** - PostgreSQL with encrypted connections
- **SSL/TLS encryption** - HTTPS for dashboard and external communications

---

## 📞 Support

### Community Support

- **💬 Discord Community:** https://discord.gg/alphabetcartel
  - `#tech-support` - Technical assistance and troubleshooting
  - `#crisis-response` - Team coordination and best practices
  - `#development` - Development discussions and updates

### Technical Support

- **📁 GitHub Issues:** Report bugs and request features in component repositories
- **📚 Documentation:** Comprehensive guides in each repository
- **🔍 Troubleshooting:** See [docs/tech/troubleshooting_v2_1.md](docs/tech/troubleshooting_v2_1.md)

### Emergency Contact

For critical issues affecting crisis response capabilities:
- **Discord:** Ping `@tech-lead` role
- **GitHub:** Create urgent issue with `[CRITICAL]` tag

---

## 📜 License

This project is part of The Alphabet Cartel's open-source initiatives. Each component may have its own license - please refer to individual repositories for specific licensing information.

---

## 🙏 Acknowledgments

### Community

- **The Alphabet Cartel community** for ongoing support and feedback
- **Crisis response volunteers** who help keep our community safe
- **LGBTQIA+ advocacy organizations** for guidance and inspiration

### Technology

- **Anthropic Claude** for advanced language understanding
- **Discord.py** for Discord integration
- **FastAPI** for high-performance APIs
- **Docker** for containerization and deployment
- **PostgreSQL** for reliable data storage
- **React** for dashboard user interface

---

## 🗺️ Roadmap

### v2.2 (Q4 2025)
- Enhanced learning system with community feedback loops
- Improved dashboard analytics and reporting
- Multi-language support for Spanish and other languages
- Advanced performance optimization

### v2.5 (Q2 2026)
- Advanced conversation context tracking
- Predictive analytics for community mental health trends
- Professional service integrations
- Mobile-responsive dashboard improvements

### v3.0 (2026)
- Voice channel crisis detection capabilities
- Advanced AI model integrations
- Comprehensive mental health support platform
- Real-time crisis intervention workflows

---

## 🚀 Getting Started Today

1. **Clone the repository:**
   ```bash
   git clone --recursive https://github.com/the-alphabet-cartel/ash.git
   cd ash
   ```

2. **Configure your environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your Discord token, Claude API key, etc.
   ```

3. **Deploy the ecosystem:**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment:**
   ```bash
   ./scripts/health-check.sh
   ```

5. **Join our community:**
   - Discord: https://discord.gg/alphabetcartel
   - Read the [Team Guide](docs/team/team_guide_v2_1.md)

---

**Building chosen family, one conversation at a time.**

*Ash is designed with love for LGBTQIA+ gaming communities everywhere. Together, we create safer spaces where everyone can be authentically themselves.*

---

**The Alphabet Cartel** 🌈  
**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org