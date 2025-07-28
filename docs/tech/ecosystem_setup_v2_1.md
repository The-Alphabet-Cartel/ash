# 🌟 Ash Ecosystem Setup Guide v2.1 (Centralized Architecture)

**Repository:** https://github.com/the-alphabet-cartel/ash  
**Discord Community:** https://discord.gg/alphabetcartel  
**Website:** https://alphabetcartel.org

Complete configuration and setup guide for the centralized Ash crisis detection ecosystem.

---

## 📋 Overview

This guide covers the complete setup and configuration of the Ash ecosystem v2.1, which utilizes a centralized architecture on a single Linux server using Docker containers for optimal performance and simplified management.

### 🏗️ Infrastructure Overview

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
│  │   Port: 8882    │    │   Port: 8881    │    │(ash-dash)   │  │
│  │   Container     │    │   Container     │    │ Port: 8883  │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                │                                │
│                                ▼                                │
│                         ┌─────────────┐                         │
│                         │ Testing     │                         │
│                         │ Suite       │                         │
│                         │(ash-thrash) │                         │
│                         │ Port: 8884  │                         │
│                         │ Container   │                         │
│                         └─────────────┘                         │
│                                                                 │
│                         ┌─────────────┐                         │
│                         │ PostgreSQL  │                         │
│                         │ Database    │                         │
│                         │ Port: 5432  │                         │
│                         │ Container   │                         │
│                         └─────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Prerequisites

### System Requirements

**Linux Server (10.20.30.253):**
- **OS:** Debian 12 (or compatible Linux distribution)
- **CPU:** AMD Ryzen 7 5800X (or equivalent)
- **GPU:** NVIDIA RTX 3060 (or compatible CUDA GPU)
- **RAM:** 64GB (minimum 32GB recommended)
- **Storage:** 1TB SSD (minimum 500GB)
- **Network:** Gigabit Ethernet connection

### Software Prerequisites

**Required Software:**
- **Docker** & Docker Compose
- **Git** with LFS support
- **NVIDIA Drivers** and CUDA Toolkit
- **curl**, **wget**, **nano/vim**

**Development Environment:**
- **GitHub account** with access to The Alphabet Cartel organization
- **Discord Bot Token** for bot integration
- **Claude API Key** for NLP processing
- **SSL Certificates** for dashboard (production)

---

## 🚀 Phase 1: Server Preparation

### System Setup

**1. Update System:**
```bash
# Update package repositories
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    curl \
    wget \
    git \
    git-lfs \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    nano \
    vim \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm
```

**2. Install Docker:**
```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

**3. Install NVIDIA Docker Support:**
```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install NVIDIA Container Toolkit
sudo apt update && sudo apt install -y nvidia-container-toolkit

# Restart Docker daemon
sudo systemctl restart docker

# Test NVIDIA Docker integration
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

**4. Configure System for Production:**
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8881/tcp  # NLP Server API
sudo ufw allow 8882/tcp  # Discord bot API
sudo ufw allow 8883/tcp  # Dashboard
sudo ufw allow 8884/tcp  # Testing Suite
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 80/tcp    # HTTP

# Optimize system for container workloads
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
echo 'fs.file-max=65536' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Configure Docker daemon for production
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "5"
    },
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF

sudo systemctl restart docker
```

---

## 🏗️ Phase 2: Ash Ecosystem Deployment

### Repository Setup

**1. Clone Repository:**
```bash
# Create application directory
sudo mkdir -p /opt/ash
sudo chown $USER:$USER /opt/ash
cd /opt/ash

# Clone ecosystem repository with submodules
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Verify submodules
git submodule status
```

### Central Configuration

**2. Create Master Environment File:**
```bash
# Create centralized environment configuration
cp .env.template .env

# Edit master configuration
nano .env
```

**Master Environment Configuration (.env):**
```bash
# =============================================================================
# Ash Ecosystem Master Configuration
# =============================================================================

# Infrastructure Configuration
ASH_SERVER_IP=10.20.30.253
ASH_NETWORK_NAME=ash_network

# =============================================================================
# Discord Bot Configuration (ash-bot)
# =============================================================================
DISCORD_TOKEN=your_production_discord_bot_token
DISCORD_GUILD_ID=your_production_guild_id
DISCORD_BOT_PREFIX=!ash

# Internal service URLs
NLP_SERVER_URL=http://ash-nlp:8881
TESTING_SERVER_URL=http://ash-thrash:8884
DASHBOARD_URL=http://ash-dash:8883

# Bot Performance Settings
BOT_MAX_CONCURRENT_ANALYSIS=10
BOT_MESSAGE_CACHE_SIZE=1000
BOT_ANALYSIS_TIMEOUT=20

# =============================================================================
# NLP Server Configuration (ash-nlp)
# =============================================================================
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.1

# GPU Configuration (RTX 3060)
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=8.6
GPU_MEMORY_FRACTION=0.8
ENABLE_MIXED_PRECISION=true

# NLP Server Performance
NLP_WORKERS=6
NLP_TIMEOUT=60
NLP_BATCH_SIZE=16
NLP_MAX_CONCURRENT_REQUESTS=12
NLP_MODEL_CACHE_SIZE=4GB

# Learning System
ENABLE_ADAPTIVE_LEARNING=true
LEARNING_RATE=0.001
CONFIDENCE_THRESHOLD=0.75
LEARNING_BATCH_SIZE=32

# =============================================================================
# Dashboard Configuration (ash-dash)
# =============================================================================
NODE_ENV=production
DASHBOARD_PORT=8883
DASHBOARD_HOST=0.0.0.0

# SSL Configuration
ENABLE_SSL=true
SSL_CERT_PATH=./certs/cert.pem
SSL_KEY_PATH=./certs/key.pem

# Internal service connections
ASH_BOT_API=http://ash-bot:8882
ASH_NLP_API=http://ash-nlp:8881
ASH_TESTING_API=http://ash-thrash:8884

# Dashboard Performance
CACHE_TTL=300
HEALTH_CHECK_INTERVAL=30000
METRICS_UPDATE_INTERVAL=15000

# Security Settings
SESSION_SECRET=your_very_secure_random_session_secret_here
JWT_SECRET=your_jwt_secret_key_here
ENABLE_CORS=true
CORS_ORIGINS=https://dashboard.alphabetcartel.net,https://alphabetcartel.org

# =============================================================================
# Testing Suite Configuration (ash-thrash)
# =============================================================================
TEST_ENVIRONMENT=production
COMPREHENSIVE_TEST_ENABLED=true
QUICK_TEST_ENABLED=true
CONTINUOUS_TESTING_ENABLED=true

# Test Configuration
TEST_PHRASES_COUNT=350
QUICK_TEST_PHRASES=25
TARGET_ACCURACY=92.0
MAX_FALSE_POSITIVE_RATE=4.0

# Testing Schedule
COMPREHENSIVE_TEST_SCHEDULE=0 6 * * *  # Daily at 6 AM
QUICK_TEST_SCHEDULE=*/30 * * * *       # Every 30 minutes

# =============================================================================
# Database Configuration
# =============================================================================
POSTGRES_DB=ash_production
POSTGRES_USER=ash_user
POSTGRES_PASSWORD=your_very_secure_database_password_here
DATABASE_URL=postgresql://ash_user:your_very_secure_database_password_here@postgres:5432/ash_production

# Database Performance
POSTGRES_MAX_CONNECTIONS=200
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=16GB

# =============================================================================
# Monitoring & Logging
# =============================================================================
LOG_LEVEL=INFO
ENABLE_METRICS=true
ENABLE_HEALTH_CHECKS=true
HEALTH_CHECK_INTERVAL=60

# Monitoring Ports
METRICS_PORT_BOT=9091
METRICS_PORT_NLP=9092
METRICS_PORT_DASH=9093
METRICS_PORT_TESTING=9094

# =============================================================================
# Security & Privacy
# =============================================================================
ENABLE_RATE_LIMITING=true
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=1000

# API Security
ENABLE_API_AUTHENTICATION=true
API_KEY_HEADER=X-API-Key
INTERNAL_API_KEY=your_internal_api_key_here

# Crisis Detection
CRISIS_CONFIDENCE_THRESHOLD=0.7
SEVERE_CRISIS_THRESHOLD=0.9
ENABLE_CONTEXT_ANALYSIS=true
MAX_CONTEXT_LENGTH=2048
```

### Master Docker Compose Configuration

**3. Create Master Docker Compose:**
```bash
# Create the master docker-compose.yml file
cat > docker-compose.yml << 'EOF'
version: '3.8'

networks:
  ash_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  postgres_data:
  redis_data:
  nlp_models:
  dashboard_certs:
  testing_results:

services:
  # =============================================================================
  # Database Services
  # =============================================================================
  postgres:
    image: postgres:15-alpine
    container_name: ash-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
    ports:
      - "5432:5432"
    networks:
      - ash_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  redis:
    image: redis:7-alpine
    container_name: ash-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-ash_redis_pass}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - ash_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  # =============================================================================
  # Core Application Services
  # =============================================================================
  ash-nlp:
    build:
      context: ./ash-nlp
      dockerfile: Dockerfile
    container_name: ash-nlp
    restart: unless-stopped
    environment:
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - CLAUDE_MODEL=${CLAUDE_MODEL}
      - GPU_MEMORY_FRACTION=${GPU_MEMORY_FRACTION}
      - WORKERS=${NLP_WORKERS}
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=${LOG_LEVEL}
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    volumes:
      - nlp_models:/app/models
      - ./ash-nlp/src:/app/src:ro
    ports:
      - "8881:8881"
      - "${METRICS_PORT_NLP}:${METRICS_PORT_NLP}"
    networks:
      - ash_network
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8881/health"]
      interval: 30s
      timeout: 15s
      retries: 5
      start_period: 60s
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8.0'
        reservations:
          memory: 8G
          cpus: '4.0'
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]

  ash-bot:
    build:
      context: ./ash-bot
      dockerfile: Dockerfile
    container_name: ash-bot
    restart: unless-stopped
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - DISCORD_GUILD_ID=${DISCORD_GUILD_ID}
      - NLP_SERVER_URL=http://ash-nlp:8881
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=${LOG_LEVEL}
      - MAX_CONCURRENT_ANALYSIS=${BOT_MAX_CONCURRENT_ANALYSIS}
    volumes:
      - ./ash-bot/src:/app/src:ro
    ports:
      - "8882:8882"
      - "${METRICS_PORT_BOT}:${METRICS_PORT_BOT}"
    networks:
      - ash_network
    depends_on:
      postgres:
        condition: service_healthy
      ash-nlp:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8882/health"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  ash-dash:
    build:
      context: ./ash-dash
      dockerfile: Dockerfile
    container_name: ash-dash
    restart: unless-stopped
    environment:
      - NODE_ENV=${NODE_ENV}
      - PORT=${DASHBOARD_PORT}
      - ASH_BOT_API=http://ash-bot:8882
      - ASH_NLP_API=http://ash-nlp:8881
      - ASH_TESTING_API=http://ash-thrash:8884
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379
      - SESSION_SECRET=${SESSION_SECRET}
      - ENABLE_SSL=${ENABLE_SSL}
    volumes:
      - dashboard_certs:/app/certs
      - ./ash-dash/src:/app/src:ro
    ports:
      - "8883:8883"
      - "${METRICS_PORT_DASH}:${METRICS_PORT_DASH}"
    networks:
      - ash_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      ash-bot:
        condition: service_healthy
      ash-nlp:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "-k", "http://localhost:8883/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  ash-thrash:
    build:
      context: ./ash-thrash
      dockerfile: Dockerfile
    container_name: ash-thrash
    restart: unless-stopped
    environment:
      - NLP_SERVER_URL=http://ash-nlp:8881
      - TEST_ENVIRONMENT=${TEST_ENVIRONMENT}
      - DATABASE_URL=${DATABASE_URL}
      - COMPREHENSIVE_TEST_ENABLED=${COMPREHENSIVE_TEST_ENABLED}
      - TEST_PHRASES_COUNT=${TEST_PHRASES_COUNT}
      - TARGET_ACCURACY=${TARGET_ACCURACY}
      - LOG_LEVEL=${LOG_LEVEL}
    volumes:
      - testing_results:/app/results
      - ./ash-thrash/src:/app/src:ro
    ports:
      - "8884:8884"
      - "${METRICS_PORT_TESTING}:${METRICS_PORT_TESTING}"
    networks:
      - ash_network
    depends_on:
      postgres:
        condition: service_healthy
      ash-nlp:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8884/health"]
      interval: 60s
      timeout: 15s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  # =============================================================================
  # Monitoring Services
  # =============================================================================
  prometheus:
    image: prom/prometheus:latest
    container_name: ash-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - ash_network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  grafana:
    image: grafana/grafana:latest
    container_name: ash-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    ports:
      - "3000:3000"
    networks:
      - ash_network
    depends_on:
      - prometheus
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

volumes:
  prometheus_data:
  grafana_data:
EOF
```

### Database Initialization

**4. Create Database Initialization Script:**
```bash
# Create database initialization script
mkdir -p scripts
cat > scripts/init-db.sql << 'EOF'
-- Ash Ecosystem Database Initialization
-- Create separate schemas for each component

-- Create schemas
CREATE SCHEMA IF NOT EXISTS ash_bot;
CREATE SCHEMA IF NOT EXISTS ash_nlp;
CREATE SCHEMA IF NOT EXISTS ash_dash;
CREATE SCHEMA IF NOT EXISTS ash_thrash;

-- Create users and permissions (if needed for separation)
-- Note: Using single database with schemas for simplicity

-- Bot tables
CREATE TABLE IF NOT EXISTS ash_bot.messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255) NOT NULL,
    content TEXT,
    analysis_result JSONB,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ash_bot.interventions (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) REFERENCES ash_bot.messages(message_id),
    user_id VARCHAR(255) NOT NULL,
    intervention_type VARCHAR(100),
    response_time_seconds INTEGER,
    outcome VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NLP tables
CREATE TABLE IF NOT EXISTS ash_nlp.analysis_logs (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    input_text TEXT NOT NULL,
    analysis_result JSONB,
    confidence FLOAT,
    processing_time_ms INTEGER,
    model_version VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ash_nlp.learning_feedback (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) REFERENCES ash_nlp.analysis_logs(request_id),
    feedback_type VARCHAR(50), -- 'accurate', 'inaccurate', 'false_positive', 'false_negative'
    human_assessment VARCHAR(50),
    confidence_adjustment FLOAT,
    pattern_updates JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dashboard tables
CREATE TABLE IF NOT EXISTS ash_dash.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    role VARCHAR(50) DEFAULT 'observer',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ash_dash.sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES ash_dash.users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ash_dash.system_metrics (
    id SERIAL PRIMARY KEY,
    component VARCHAR(50) NOT NULL, -- 'bot', 'nlp', 'dashboard', 'testing'
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT,
    metric_unit VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Testing tables
CREATE TABLE IF NOT EXISTS ash_thrash.test_runs (
    id SERIAL PRIMARY KEY,
    test_type VARCHAR(50) NOT NULL, -- 'comprehensive', 'quick', 'performance'
    test_config JSONB,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50), -- 'running', 'completed', 'failed'
    results_summary JSONB
);

CREATE TABLE IF NOT EXISTS ash_thrash.test_results (
    id SERIAL PRIMARY KEY,
    test_run_id INTEGER REFERENCES ash_thrash.test_runs(id),
    phrase_id VARCHAR(255),
    input_text TEXT,
    expected_result VARCHAR(100),
    actual_result VARCHAR(100),
    confidence FLOAT,
    response_time_ms INTEGER,
    is_correct BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON ash_bot.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON ash_bot.messages(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_created_at ON ash_nlp.analysis_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_system_metrics_component_timestamp ON ash_dash.system_metrics(component, timestamp);
CREATE INDEX IF NOT EXISTS idx_test_results_test_run_id ON ash_thrash.test_results(test_run_id);

-- Insert default dashboard user
INSERT INTO ash_dash.users (username, email, role) 
VALUES ('admin', 'admin@alphabetcartel.org', 'admin') 
ON CONFLICT (username) DO NOTHING;

COMMIT;
EOF
```

---

## 🔧 Phase 3: Service Configuration

### SSL Certificate Setup

**1. Generate SSL Certificates for Dashboard:**
```bash
# Create certificates directory
mkdir -p certs

# Generate self-signed certificate for development/staging
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=TheAlphabetCartel/CN=dashboard.alphabetcartel.net"

# Set appropriate permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem

# For production, use Let's Encrypt:
# sudo apt install certbot
# sudo certbot certonly --standalone -d dashboard.alphabetcartel.net
# Then copy certificates to certs/ directory
```

### Monitoring Configuration

**2. Create Monitoring Configuration:**
```bash
# Create monitoring directory structure
mkdir -p monitoring/grafana/{dashboards,provisioning/dashboards,provisioning/datasources}

# Create Prometheus configuration
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'ash-bot'
    static_configs:
      - targets: ['ash-bot:9091']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'ash-nlp'
    static_configs:
      - targets: ['ash-nlp:9092']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'ash-dashboard'
    static_configs:
      - targets: ['ash-dash:9093']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'ash-testing'
    static_configs:
      - targets: ['ash-thrash:9094']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 60s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 60s
EOF

# Create Grafana datasource configuration
cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Create Grafana dashboard provisioning
cat > monitoring/grafana/provisioning/dashboards/ash.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'ash-dashboards'
    orgId: 1
    folder: 'Ash Ecosystem'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF
```

---

## 🚀 Phase 4: Deployment

### Initial Deployment

**1. Deploy the Complete Ecosystem:**
```bash
# Build and start all services
docker-compose build

# Start services in dependency order
docker-compose up -d postgres redis
sleep 30

# Start core services
docker-compose up -d ash-nlp
sleep 45  # Allow NLP server to fully initialize

docker-compose up -d ash-bot ash-dash ash-thrash
sleep 30

# Start monitoring services
docker-compose up -d prometheus grafana

# Verify all services are running
docker-compose ps
```

**2. Verify Deployment:**
```bash
# Check service health
curl http://localhost:8881/health  # NLP Server
curl http://localhost:8882/health  # Discord Bot
curl -k https://localhost:8883/health  # Dashboard (SSL)
curl http://localhost:8884/health  # Testing Suite

# Check database connectivity
docker exec ash-postgres pg_isready -U ash_user -d ash_production

# Check monitoring
curl http://localhost:9090/targets  # Prometheus targets
curl http://localhost:3000  # Grafana (admin/admin)
```

### System Service Setup

**3. Create System Service for Auto-Start:**
```bash
# Create systemd service for the entire ecosystem
sudo tee /etc/systemd/system/ash-ecosystem.service > /dev/null << 'EOF'
[Unit]
Description=Ash Crisis Detection Ecosystem
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ash/ash
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=300
TimeoutStopSec=120

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable ash-ecosystem.service
sudo systemctl start ash-ecosystem.service

# Check service status
sudo systemctl status ash-ecosystem.service
```

---

## ✅ Phase 5: Validation & Testing

### System Validation

**1. Comprehensive Health Check:**
```bash
# Create comprehensive health check script
cat > scripts/health-check.sh << 'EOF'
#!/bin/bash

echo "=== Ash Ecosystem Health Check ==="
echo "Timestamp: $(date)"
echo

# Check Docker containers
echo "Container Status:"
docker-compose ps

echo -e "\nService Health Checks:"

# Test each service
services=("8881/health" "8882/health" "8883/health" "8884/health")
service_names=("NLP Server" "Discord Bot" "Dashboard" "Testing Suite")

for i in "${!services[@]}"; do
    echo -n "Testing ${service_names[$i]} (${services[$i]})... "
    if curl -f -s -k "http://localhost:${services[$i]}" > /dev/null; then
        echo "✅ Healthy"
    else
        echo "❌ Failed"
    fi
done

# Check database
echo -n "Testing Database... "
if docker exec ash-postgres pg_isready -U ash_user -d ash_production > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Failed"
fi

# Check GPU access
echo -n "Testing GPU Access... "
if docker exec ash-nlp nvidia-smi > /dev/null 2>&1; then
    echo "✅ Available"
else
    echo "⚠️ Not Available"
fi

# Test inter-service communication
echo -e "\nInter-Service Communication:"
echo -n "Bot → NLP Server... "
if docker exec ash-bot curl -f -s http://ash-nlp:8881/health > /dev/null; then
    echo "✅ Connected"
else
    echo "❌ Failed"
fi

echo -n "Dashboard → All Services... "
if docker exec ash-dash curl -f -s http://ash-bot:8882/health > /dev/null && \
   docker exec ash-dash curl -f -s http://ash-nlp:8881/health > /dev/null && \
   docker exec ash-dash curl -f -s http://ash-thrash:8884/health > /dev/null; then
    echo "✅ Connected"
else
    echo "❌ Failed"
fi

# Check system resources
echo -e "\nSystem Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"

if command -v nvidia-smi &> /dev/null; then
    echo "GPU Memory: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf "%.1f%%", $1/$2*100}')"
fi

echo -e "\n=== Health Check Complete ==="
EOF

chmod +x scripts/health-check.sh

# Run health check
./scripts/health-check.sh
```

**2. Integration Testing:**
```bash
# Test crisis detection end-to-end
echo "Testing crisis detection pipeline..."

# Test NLP analysis directly
curl -X POST http://localhost:8881/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel like nobody would miss me if I disappeared", "context": "integration_test"}'

# Run quick testing suite validation
curl -X POST http://localhost:8884/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}'

# Wait for test completion
sleep 30

# Check test results
curl http://localhost:8884/api/test/results/latest
```

**3. Performance Validation:**
```bash
# Test system performance under load
echo "Running performance validation..."

# Load test NLP server
for i in {1..10}; do
    curl -X POST http://localhost:8881/api/analyze \
      -H "Content-Type: application/json" \
      -d "{\"text\": \"Test message $i for performance testing\", \"context\": \"load_test\"}" &
done

wait

# Check response times
docker-compose logs ash-nlp | grep "Response time" | tail -10
```

---

## 🔄 Maintenance & Updates

### Backup Procedures

**1. Create Backup Scripts:**
```bash
# Create comprehensive backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/ash/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M)
BACKUP_PATH="$BACKUP_DIR/ash-ecosystem-$TIMESTAMP"

echo "Creating Ash Ecosystem backup: $BACKUP_PATH"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Backup configuration files
echo "Backing up configuration..."
cp .env "$BACKUP_PATH/"
cp docker-compose.yml "$BACKUP_PATH/"
cp -r certs "$BACKUP_PATH/" 2>/dev/null || true
cp -r monitoring "$BACKUP_PATH/"
cp -r scripts "$BACKUP_PATH/"

# Backup database
echo "Backing up database..."
docker exec ash-postgres pg_dump -U ash_user ash_production | gzip > "$BACKUP_PATH/database.sql.gz"

# Backup Docker volumes
echo "Backing up volumes..."
docker run --rm -v ash_nlp_models:/data -v "$BACKUP_PATH:/backup" alpine tar czf /backup/nlp-models.tar.gz -C /data .
docker run --rm -v ash_testing_results:/data -v "$BACKUP_PATH:/backup" alpine tar czf /backup/testing-results.tar.gz -C /data .

# Create backup manifest
echo "Creating backup manifest..."
cat > "$BACKUP_PATH/backup-manifest.txt" << MANIFEST
Ash Ecosystem Backup
Created: $(date)
Server: $(hostname)
Docker Compose Version: $(docker-compose --version)
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "Not available")

Contents:
- Configuration files (.env, docker-compose.yml)
- SSL certificates (certs/)
- Monitoring configuration (monitoring/)
- Utility scripts (scripts/)
- Database dump (database.sql.gz)
- NLP models (nlp-models.tar.gz)
- Testing results (testing-results.tar.gz)
MANIFEST

# Compress entire backup
echo "Compressing backup..."
cd "$BACKUP_DIR"
tar czf "ash-ecosystem-$TIMESTAMP.tar.gz" "ash-ecosystem-$TIMESTAMP/"
rm -rf "ash-ecosystem-$TIMESTAMP/"

echo "Backup completed: $BACKUP_DIR/ash-ecosystem-$TIMESTAMP.tar.gz"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "ash-ecosystem-*.tar.gz" -mtime +30 -delete

echo "Backup process completed successfully"
EOF

chmod +x scripts/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ash/ash/scripts/backup.sh >> /opt/ash/ash/logs/backup.log 2>&1") | crontab -
```

### Update Procedures

**2. Create Update Script:**
```bash
# Create update script
cat > scripts/update.sh << 'EOF'
#!/bin/bash

echo "=== Ash Ecosystem Update Process ==="
echo "Timestamp: $(date)"

# Backup before update
echo "Creating pre-update backup..."
./scripts/backup.sh

# Update repository
echo "Updating repository..."
git fetch origin
git submodule update --remote --merge

# Check for changes
if git diff --quiet HEAD origin/main && git submodule foreach --quiet 'git diff --quiet HEAD origin/main'; then
    echo "No updates available"
    exit 0
fi

echo "Updates detected, proceeding with update..."

# Update main repository
git pull origin main
git submodule update --recursive

# Rebuild services with changes
echo "Rebuilding updated services..."
docker-compose build --no-cache

# Rolling update (update services one by one to minimize downtime)
echo "Performing rolling update..."

# Update NLP server first (core service)
docker-compose up -d --no-deps ash-nlp
sleep 30
docker exec ash-nlp curl -f http://localhost:8881/health || { echo "NLP server failed to start"; exit 1; }

# Update dashboard
docker-compose up -d --no-deps ash-dash
sleep 15
docker exec ash-dash curl -f -k http://localhost:8883/health || { echo "Dashboard failed to start"; exit 1; }

# Update bot
docker-compose up -d --no-deps ash-bot
sleep 15
docker exec ash-bot curl -f http://localhost:8882/health || { echo "Bot failed to start"; exit 1; }

# Update testing suite
docker-compose up -d --no-deps ash-thrash
sleep 15
docker exec ash-thrash curl -f http://localhost:8884/health || { echo "Testing suite failed to start"; exit 1; }

# Verify system health
echo "Verifying system health after update..."
./scripts/health-check.sh

echo "Update completed successfully"
EOF

chmod +x scripts/update.sh
```

### Monitoring Setup

**3. Create Monitoring Scripts:**
```bash
# Create performance monitoring script
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="/opt/ash/ash/logs/monitoring.log"
mkdir -p "$(dirname "$LOG_FILE")"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # System metrics
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEMORY=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    DISK=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
    
    # GPU metrics (if available)
    if command -v nvidia-smi &> /dev/null; then
        GPU_MEM=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf "%.1f", $1/$2*100}')
        GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    else
        GPU_MEM="N/A"
        GPU_UTIL="N/A"
    fi
    
    # Service health
    SERVICES_HEALTHY=0
    SERVICES_TOTAL=4
    
    for port in 8881 8882 8883 8884; do
        if curl -f -s -k "http://localhost:$port/health" > /dev/null 2>&1; then
            ((SERVICES_HEALTHY++))
        fi
    done
    
    # Log metrics
    echo "$TIMESTAMP,CPU:$CPU,Memory:$MEMORY,Disk:$DISK,GPU_Mem:$GPU_MEM,GPU_Util:$GPU_UTIL,Services:$SERVICES_HEALTHY/$SERVICES_TOTAL" >> "$LOG_FILE"
    
    # Alert on critical conditions
    if (( $(echo "$CPU > 90" | bc -l) )) || (( $(echo "$MEMORY > 95" | bc -l) )) || [[ $SERVICES_HEALTHY -lt 3 ]]; then
        echo "$TIMESTAMP ALERT: Critical system condition detected - CPU:$CPU% Memory:$MEMORY% Services:$SERVICES_HEALTHY/$SERVICES_TOTAL" >> "$LOG_FILE"
        
        # Send notification (if webhook configured)
        if [[ -n "$DISCORD_WEBHOOK_URL" ]]; then
            curl -X POST "$DISCORD_WEBHOOK_URL" \
                -H "Content-Type: application/json" \
                -d "{\"content\": \"🚨 Ash System Alert: CPU:$CPU% Memory:$MEMORY% Services:$SERVICES_HEALTHY/$SERVICES_TOTAL healthy\"}"
        fi
    fi
    
    sleep 300  # Check every 5 minutes
done
EOF

chmod +x scripts/monitor.sh

# Run monitoring in background
nohup ./scripts/monitor.sh &
```

---

## 📞 Support & Emergency Procedures

### Emergency Recovery

**1. Create Emergency Recovery Script:**
```bash
# Create emergency recovery script
cat > scripts/emergency-recovery.sh << 'EOF'
#!/bin/bash

echo "=== EMERGENCY RECOVERY INITIATED ==="
echo "Timestamp: $(date)"

# Stop all services
echo "Stopping all services..."
docker-compose down

# Clean up potentially corrupted containers and networks
echo "Cleaning up Docker resources..."
docker system prune -f
docker volume prune -f
docker network prune -f

# Check system resources
echo "Checking system resources..."
df -h
free -h
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi
fi

# Restart core infrastructure
echo "Starting core infrastructure..."
docker-compose up -d postgres redis
sleep 30

# Start services in dependency order
echo "Starting NLP server..."
docker-compose up -d ash-nlp
sleep 45

echo "Starting remaining services..."
docker-compose up -d ash-bot ash-dash ash-thrash
sleep 30

# Verify recovery
echo "Verifying recovery..."
./scripts/health-check.sh

# Run quick test
echo "Running quick validation test..."
curl -X POST http://localhost:8884/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}' || echo "Quick test failed to start"

echo "=== EMERGENCY RECOVERY COMPLETED ==="
echo "Check health-check results above for system status"
EOF

chmod +x scripts/emergency-recovery.sh
```

### Support Resources

**Documentation:**
- **Main README:** [../../README.md](../../README.md)
- **Development Guide:** [development_v2_1.md](development_v2_1.md)
- **Troubleshooting Guide:** [troubleshooting_v2_1.md](troubleshooting_v2_1.md)
- **Team Operations:** [../team/team_guide_v2_1.md](../team/team_guide_v2_1.md)

**Community Support:**
- **Discord Community:** https://discord.gg/alphabetcartel
  - `#tech-support` for technical assistance
  - `#crisis-response` for operational concerns
- **GitHub Issues:** Component-specific bug reports
- **Emergency Contact:** Technical team leaders via Discord

---

**This centralized ecosystem setup guide provides the foundation for a robust, scalable, and maintainable crisis detection system. All components work together seamlessly on a single server while maintaining high availability and performance for supporting LGBTQIA+ community safety and wellbeing.**

**🌈 Together, we're building technology that strengthens chosen family bonds and saves lives.**

---

**Built with 🖤 for The Alphabet Cartel**  
**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org