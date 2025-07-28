# 🚀 Ash Ecosystem Deployment Guide v2.1 (Centralized Architecture)

**Updated for Centralized Single-Server Architecture** | **Repository:** https://github.com/the-alphabet-cartel/ash

## 📋 Deployment Overview

The Ash ecosystem v2.1 uses a centralized architecture where all components run as Docker containers on a single Linux server. This guide covers deployment scenarios for the new unified infrastructure.

### 🏗️ Deployment Architecture

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
│                                                                 │
│                    ┌─────────────┐    ┌─────────────┐           │
│                    │ Prometheus  │    │   Grafana   │           │
│                    │ Monitoring  │    │ Dashboard   │           │
│                    │ Container   │    │ Container   │           │
│                    │ Port: 9090  │    │ Port: 3000  │           │
│                    └─────────────┘    └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Production Deployment

### System Requirements

**Hardware Requirements:**
- **CPU:** AMD Ryzen 7 5800X (or equivalent 8-core processor)
- **GPU:** NVIDIA RTX 3060 (or compatible CUDA GPU with 12GB+ VRAM)
- **RAM:** 64GB (minimum 32GB)
- **Storage:** 1TB NVMe SSD (minimum 500GB)
- **Network:** Gigabit Ethernet connection

**Software Requirements:**
- **OS:** Debian 12 (recommended) or Ubuntu 22.04 LTS
- **Docker:** Latest version with Docker Compose
- **NVIDIA Drivers:** Latest stable version
- **NVIDIA Container Toolkit:** For GPU support in containers

### Phase 1: Server Preparation

**1. System Setup:**
```bash
# Update system packages
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
    build-essential

# Install Python and Node.js (for local debugging if needed)
sudo apt install -y python3 python3-pip python3-venv nodejs npm
```

**2. Docker Installation:**
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

**3. NVIDIA GPU Setup:**
```bash
# Install NVIDIA drivers (if not already installed)
sudo apt install -y nvidia-driver-535  # Or latest version
sudo reboot  # Reboot required after driver installation

# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install NVIDIA Container Toolkit
sudo apt update && sudo apt install -y nvidia-container-toolkit

# Configure Docker daemon for GPU support
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

# Restart Docker daemon
sudo systemctl restart docker

# Test NVIDIA Docker integration
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

**4. System Optimization:**
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8881/tcp  # NLP Server
sudo ufw allow 8882/tcp  # Discord Bot
sudo ufw allow 8883/tcp  # Dashboard
sudo ufw allow 8884/tcp  # Testing Suite
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 80/tcp    # HTTP

# Optimize system for containers
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
echo 'fs.file-max=65536' | sudo tee -a /etc/sysctl.conf
echo 'net.core.somaxconn=32768' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Create application directory
sudo mkdir -p /opt/ash
sudo chown $USER:$USER /opt/ash
```

---

### Phase 2: Application Deployment

**1. Repository Setup:**
```bash
# Clone the ecosystem repository
cd /opt/ash
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Verify submodules are properly initialized
git submodule status
```

**2. Environment Configuration:**
```bash
# Create production environment file
cp .env.template .env

# Edit configuration with production settings
nano .env
```

**Production Environment Configuration (.env):**
```bash
# =============================================================================
# Ash Ecosystem Production Configuration
# =============================================================================

# Infrastructure
ASH_SERVER_IP=10.20.30.253
ASH_ENVIRONMENT=production

# =============================================================================
# Discord Bot Configuration
# =============================================================================
DISCORD_TOKEN=your_production_discord_bot_token
DISCORD_GUILD_ID=your_production_guild_id
DISCORD_BOT_PREFIX=!ash

# Internal service URLs (container networking)
NLP_SERVER_URL=http://ash-nlp:8881
TESTING_SERVER_URL=http://ash-thrash:8884
GLOBAL_DASH_API_URL=http://ash-dash:8883

# Performance settings
BOT_MAX_CONCURRENT_ANALYSIS=15
BOT_MESSAGE_CACHE_SIZE=2000
BOT_ANALYSIS_TIMEOUT=25

# =============================================================================
# NLP Server Configuration
# =============================================================================
CLAUDE_API_KEY=your_production_claude_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=0.1

# GPU Configuration (RTX 3060 optimized)
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=8.6
GPU_MEMORY_FRACTION=0.85
ENABLE_MIXED_PRECISION=true

# NLP Performance settings
NLP_WORKERS=8
NLP_TIMEOUT=60
NLP_BATCH_SIZE=20
NLP_MAX_CONCURRENT_REQUESTS=16
NLP_MODEL_CACHE_SIZE=6GB

# Learning system
ENABLE_ADAPTIVE_LEARNING=true
LEARNING_RATE=0.001
CONFIDENCE_THRESHOLD=0.75
LEARNING_BATCH_SIZE=32

# =============================================================================
# Dashboard Configuration
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

# Performance settings
CACHE_TTL=300
METRICS_UPDATE_INTERVAL=15000

# Security settings
SESSION_SECRET=your_very_secure_random_session_secret_here
JWT_SECRET=your_jwt_secret_key_here
ENABLE_CORS=true
CORS_ORIGINS=https://dashboard.alphabetcartel.net,https://alphabetcartel.org
ENABLE_RATE_LIMITING=true
DASH_RATE_LIMIT_WINDOW=900000
DASH_RATE_LIMIT_MAX=2000

# =============================================================================
# Testing Suite Configuration
# =============================================================================
TEST_ENVIRONMENT=production
COMPREHENSIVE_TEST_ENABLED=true
QUICK_TEST_ENABLED=true
CONTINUOUS_TESTING_ENABLED=true

# Test configuration
TEST_PHRASES_COUNT=350
QUICK_TEST_PHRASES=25
TARGET_ACCURACY=92.0
MAX_FALSE_POSITIVE_RATE=4.0
ACCURACY_ALERT_THRESHOLD=88.0

# Test scheduling
THRASH_COMPREHENSIVE_TEST_SCHEDULE=0 6 * * *  # Daily at 6 AM
QUICK_TEST_SCHEDULE=*/30 * * * *       # Every 30 minutes
PERFORMANCE_TEST_SCHEDULE=0 */6 * * *  # Every 6 hours

# =============================================================================
# Database Configuration
# =============================================================================
GLOBAL_POSTGRES_DB=ash_production
GLOBAL_POSTGRES_USER=ash_user
GLOBAL_POSTGRES_PASSWORD=your_very_secure_database_password_here
THRASH_DATABASE_URL=postgresql://ash_user:your_very_secure_database_password_here@postgres:5432/ash_production

# Database performance (optimized for 64GB RAM)
POSTGRES_MAX_CONNECTIONS=300
POSTGRES_SHARED_BUFFERS=512MB
POSTGRES_EFFECTIVE_CACHE_SIZE=32GB
POSTGRES_MAINTENANCE_WORK_MEM=512MB
POSTGRES_CHECKPOINT_COMPLETION_TARGET=0.9
POSTGRES_WAL_BUFFERS=16MB
POSTGRES_DEFAULT_STATISTICS_TARGET=100

# =============================================================================
# Redis Configuration
# =============================================================================
REDIS_PASSWORD=your_secure_redis_password_here
REDIS_MAXMEMORY=4GB
REDIS_MAXMEMORY_POLICY=allkeys-lru

# =============================================================================
# Monitoring Configuration
# =============================================================================
ENABLE_METRICS=true

# Monitoring ports
METRICS_PORT_BOT=9091
METRICS_PORT_NLP=9092
METRICS_PORT_DASH=9093
METRICS_PORT_TESTING=9094

# Grafana configuration
GRAFANA_ADMIN_PASSWORD=your_secure_grafana_password

# =============================================================================
# Security & Privacy
# =============================================================================
THRASH_ENABLE_API_AUTHENTICATION=true
API_KEY_HEADER=X-API-Key
INTERNAL_API_KEY=your_internal_api_key_here

# Crisis detection
CRISIS_CONFIDENCE_THRESHOLD=0.7
SEVERE_CRISIS_THRESHOLD=0.9
ENABLE_CONTEXT_ANALYSIS=true
MAX_CONTEXT_LENGTH=2048

# =============================================================================
# Logging Configuration
# =============================================================================
LOG_LEVEL=INFO
THRASH_ENABLE_DETAILED_LOGGING=true
LOG_RETENTION_DAYS=90

# =============================================================================
# Backup Configuration
# =============================================================================
DASH_BACKUP_RETENTION_DAYS=30
BACKUP_LOCATION=/opt/ash/backups
```

**3. SSL Certificate Setup:**
```bash
# Create certificates directory
mkdir -p certs

# Option 1: Generate self-signed certificate (development/staging)
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=TheAlphabetCartel/CN=dashboard.alphabetcartel.net"

# Option 2: Use Let's Encrypt (production)
sudo apt install certbot
sudo certbot certonly --standalone -d dashboard.alphabetcartel.net
sudo cp /etc/letsencrypt/live/dashboard.alphabetcartel.net/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/dashboard.alphabetcartel.net/privkey.pem certs/key.pem
sudo chown $USER:$USER certs/*

# Set appropriate permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem
```

**4. Monitoring Configuration:**
```bash
# Create monitoring configuration
mkdir -p monitoring/grafana/{dashboards,provisioning/dashboards,provisioning/datasources}

# Create Prometheus configuration
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 30s
  evaluation_interval: 30s
  external_labels:
    monitor: 'ash-ecosystem'

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

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

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['host.docker.internal:9100']
    scrape_interval: 30s
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
    editable: true
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

### Phase 3: Container Deployment

**1. Build and Deploy:**
```bash
# Build all container images
docker-compose build

# Start core infrastructure first
docker-compose up -d postgres redis
echo "Waiting for database initialization..."
sleep 45

# Verify database is ready
docker exec ash-postgres pg_isready -U ash_user -d ash_production

# Start application services
docker-compose up -d ash-nlp
echo "Waiting for NLP server initialization..."
sleep 60

# Verify NLP server with GPU
docker exec ash-nlp nvidia-smi
curl http://localhost:8881/health

# Start remaining services
docker-compose up -d ash-bot ash-dash ash-thrash
echo "Waiting for services to initialize..."
sleep 30

# Start monitoring services
docker-compose up -d prometheus grafana
sleep 20

# Verify all services
docker-compose ps
```

**2. Initial Testing:**
```bash
# Run comprehensive health check
./scripts/health-check.sh

# Test service endpoints
curl http://localhost:8881/health  # NLP Server
curl http://localhost:8882/health  # Discord Bot
curl -k https://localhost:8883/health  # Dashboard
curl http://localhost:8884/health  # Testing Suite
curl http://localhost:9090/targets  # Prometheus
curl http://localhost:3000  # Grafana

# Run initial comprehensive test
curl -X POST http://localhost:8884/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_type": "comprehensive"}'

# Monitor test progress
sleep 60
curl http://localhost:8884/api/test/results/latest
```

**3. System Service Setup:**
```bash
# Create systemd service for automatic startup
sudo tee /etc/systemd/system/ash-ecosystem.service > /dev/null << 'EOF'
[Unit]
Description=Ash Crisis Detection Ecosystem
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ash/ash
ExecStartPre=/usr/local/bin/docker-compose down
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=600
TimeoutStopSec=120
User=ash
Group=ash

[Install]
WantedBy=multi-user.target
EOF

# Create ash user for service
sudo useradd -r -s /bin/false ash
sudo chown -R ash:ash /opt/ash

# Enable and start service
sudo systemctl enable ash-ecosystem.service
sudo systemctl start ash-ecosystem.service

# Check service status
sudo systemctl status ash-ecosystem.service
```

---

## 📊 Production Configuration Options

### Performance Optimization

**High-Performance Configuration:**
```yaml
# docker-compose.prod.yml - Performance optimized
version: '3.8'

services:
  ash-nlp:
    deploy:
      resources:
        limits:
          memory: 20G
          cpus: '10.0'
        reservations:
          memory: 12G
          cpus: '6.0'
    environment:
      - NLP_WORKERS=10
      - NLP_BATCH_SIZE=24
      - GPU_MEMORY_FRACTION=0.9

  ash-bot:
    deploy:
      resources:
        limits:
          memory: 6G
          cpus: '4.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    environment:
      - BOT_MAX_CONCURRENT_ANALYSIS=20

  ash-dash:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 3G
          cpus: '2.0'

  postgres:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
    environment:
      - POSTGRES_SHARED_BUFFERS=1GB
      - POSTGRES_EFFECTIVE_CACHE_SIZE=48GB
    command: >
      postgres
      -c max_connections=400
      -c shared_buffers=1GB
      -c effective_cache_size=48GB
      -c maintenance_work_mem=1GB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=32MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
```

**Resource-Constrained Configuration:**
```yaml
# docker-compose.minimal.yml - For smaller servers
version: '3.8'

services:
  ash-nlp:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
    environment:
      - NLP_WORKERS=4
      - NLP_BATCH_SIZE=8
      - GPU_MEMORY_FRACTION=0.7

  ash-bot:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  ash-dash:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  postgres:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
    environment:
      - POSTGRES_SHARED_BUFFERS=256MB
      - POSTGRES_EFFECTIVE_CACHE_SIZE=16GB
```

### Deployment Variants

**Development Deployment:**
```bash
# Use development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Enable development features
export LOG_LEVEL=DEBUG
export CACHE_TTL=10
```

**Staging Deployment:**
```bash
# Use staging configuration
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Enable staging-specific settings
export ENVIRONMENT=staging
export ENABLE_TEST_ENDPOINTS=true
```

**Production Deployment:**
```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Enable production optimizations
export ENVIRONMENT=production
export ENABLE_PERFORMANCE_MONITORING=true
```

---

## ✅ Post-Deployment Validation

### Comprehensive System Testing

**1. Service Health Validation:**
```bash
# Create comprehensive validation script
cat > scripts/validate-deployment.sh << 'EOF'
#!/bin/bash

echo "=== Ash Ecosystem Deployment Validation ==="
echo "Timestamp: $(date)"
echo

# Function to test endpoint with retry
test_endpoint() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "Testing $name... "
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s -k "$url" > /dev/null 2>&1; then
            echo "✅ Success"
            return 0
        fi
        sleep 2
        ((attempt++))
    done
    echo "❌ Failed after $max_attempts attempts"
    return 1
}

# Test all service endpoints
test_endpoint "NLP Server" "http://localhost:8881/health"
test_endpoint "Discord Bot" "http://localhost:8882/health"
test_endpoint "Dashboard" "https://localhost:8883/health"
test_endpoint "Testing Suite" "http://localhost:8884/health"
test_endpoint "Prometheus" "http://localhost:9090/-/ready"
test_endpoint "Grafana" "http://localhost:3000/api/health"

# Test database connectivity
echo -n "Testing Database... "
if docker exec ash-postgres pg_isready -U ash_user -d ash_production > /dev/null 2>&1; then
    echo "✅ Connected"
else
    echo "❌ Failed"
fi

# Test Redis connectivity
echo -n "Testing Redis... "
if docker exec ash-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Connected"
else
    echo "❌ Failed"
fi

# Test GPU access
echo -n "Testing GPU Access... "
if docker exec ash-nlp nvidia-smi > /dev/null 2>&1; then
    echo "✅ Available"
else
    echo "⚠️ Not Available"
fi

# Test container networking
echo -e "\nTesting Container Networking:"
containers=("ash-bot" "ash-dash" "ash-thrash")
for container in "${containers[@]}"; do
    echo -n "  $container → NLP Server... "
    if docker exec "$container" curl -f -s http://ash-nlp:8881/health > /dev/null 2>&1; then
        echo "✅ Connected"
    else
        echo "❌ Failed"
    fi
done

# Test crisis detection pipeline
echo -e "\nTesting Crisis Detection Pipeline:"
echo -n "  End-to-End Test... "
response=$(curl -s -X POST http://localhost:8881/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel like nobody would miss me", "context": "deployment_test"}' 2>/dev/null)

if echo "$response" | grep -q "confidence"; then
    echo "✅ Working"
else
    echo "❌ Failed"
fi

# System resource check
echo -e "\nSystem Resources:"
echo "  CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "  Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "  Disk Usage: $(df -h / | awk 'NR==2{print $5}')"

if command -v nvidia-smi &> /dev/null; then
    echo "  GPU Memory: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf "%.1f%%", $1/$2*100}')"
fi

# Container status
echo -e "\nContainer Status:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n=== Deployment Validation Complete ==="
EOF

chmod +x scripts/validate-deployment.sh
./scripts/validate-deployment.sh
```

**2. Performance Testing:**
```bash
# Run comprehensive performance test
curl -X POST http://localhost:8884/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_type": "comprehensive", "include_performance": true}'

# Wait for completion
sleep 120

# Check results
curl http://localhost:8884/api/test/results/latest | jq '.'

# Run load test
cd ash-thrash
python src/load_testing.py --concurrent=50 --duration=300

# Monitor performance during load test
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**3. Monitoring Setup Validation:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Test Grafana dashboards
curl -u admin:$GRAFANA_ADMIN_PASSWORD http://localhost:3000/api/dashboards/tags

# Check alert rules
curl http://localhost:9090/api/v1/rules
```

---

## 🔄 Maintenance & Operations

### Backup Procedures

**1. Automated Backup Setup:**
```bash
# Create comprehensive backup script
cat > scripts/backup-production.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/ash/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M)
BACKUP_PATH="$BACKUP_DIR/ash-ecosystem-$TIMESTAMP"

echo "Creating production backup: $BACKUP_PATH"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Backup configuration
echo "Backing up configuration..."
cp .env "$BACKUP_PATH/"
cp docker-compose*.yml "$BACKUP_PATH/"
cp -r certs "$BACKUP_PATH/" 2>/dev/null || true
cp -r monitoring "$BACKUP_PATH/"
cp -r scripts "$BACKUP_PATH/"

# Backup databases
echo "Backing up databases..."
docker exec ash-postgres pg_dump -U ash_user ash_production | gzip > "$BACKUP_PATH/postgres.sql.gz"

# Backup Redis data
echo "Backing up Redis..."
docker exec ash-redis redis-cli BGSAVE
docker cp ash-redis:/data/dump.rdb "$BACKUP_PATH/redis.rdb"

# Backup Docker volumes
echo "Backing up volumes..."
docker run --rm -v ash_nlp_models:/data -v "$BACKUP_PATH:/backup" alpine tar czf /backup/nlp-models.tar.gz -C /data .
docker run --rm -v ash_testing_results:/data -v "$BACKUP_PATH:/backup" alpine tar czf /backup/testing-results.tar.gz -C /data .
docker run --rm -v ash_grafana_data:/data -v "$BACKUP_PATH:/backup" alpine tar czf /backup/grafana-data.tar.gz -C /data .

# Create system snapshot
echo "Creating system snapshot..."
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" > "$BACKUP_PATH/docker-images.txt"
docker volume ls > "$BACKUP_PATH/docker-volumes.txt"
docker network ls > "$BACKUP_PATH/docker-networks.txt"

# System information
uname -a > "$BACKUP_PATH/system-info.txt"
docker --version >> "$BACKUP_PATH/system-info.txt"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv >> "$BACKUP_PATH/system-info.txt" 2>/dev/null || echo "No GPU" >> "$BACKUP_PATH/system-info.txt"

# Create backup manifest
cat > "$BACKUP_PATH/backup-manifest.txt" << MANIFEST
Ash Ecosystem Production Backup
Created: $(date)
Server: $(hostname) ($(hostname -I | awk '{print $1}'))
Backup Type: Full System Backup
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "Not available")

Contents:
- Configuration files (.env, docker-compose.yml)
- SSL certificates (certs/)
- Monitoring configuration (monitoring/)
- Utility scripts (scripts/)
- PostgreSQL database dump (postgres.sql.gz)
- Redis data (redis.rdb)
- NLP models (nlp-models.tar.gz)
- Testing results (testing-results.tar.gz)
- Grafana dashboards (grafana-data.tar.gz)
- System information (system-info.txt, docker-*.txt)
MANIFEST

# Compress backup
echo "Compressing backup..."
cd "$BACKUP_DIR"
tar czf "ash-ecosystem-$TIMESTAMP.tar.gz" "ash-ecosystem-$TIMESTAMP/"
rm -rf "ash-ecosystem-$TIMESTAMP/"

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "ash-ecosystem-*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/ash-ecosystem-$TIMESTAMP.tar.gz"

# Verify backup integrity
if tar -tzf "$BACKUP_DIR/ash-ecosystem-$TIMESTAMP.tar.gz" >/dev/null; then
    echo "Backup integrity verified"
else
    echo "ERROR: Backup integrity check failed"
    exit 1
fi
EOF

chmod +x scripts/backup-production.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/ash/ash/scripts/backup-production.sh >> /opt/ash/ash/logs/backup.log 2>&1") | crontab -
```

### Update Procedures

**1. Rolling Update Process:**
```bash
# Create rolling update script
cat > scripts/rolling-update.sh << 'EOF'
#!/bin/bash

echo "=== Ash Ecosystem Rolling Update ==="
echo "Timestamp: $(date)"

# Pre-update backup
echo "Creating pre-update backup..."
./scripts/backup-production.sh

# Update repository
echo "Updating repository..."
git fetch origin
git submodule update --remote --merge

# Build new images
echo "Building updated images..."
docker-compose build --no-cache

# Rolling update (one service at a time)
services=("ash-nlp" "ash-bot" "ash-dash" "ash-thrash")

for service in "${services[@]}"; do
    echo "Updating $service..."
    
    # Update service
    docker-compose up -d --no-deps "$service"
    
    # Wait for health check
    sleep 30
    
    # Verify service health
    case $service in
        "ash-nlp")
            if curl -f http://localhost:8881/health; then
                echo "$service updated successfully"
            else
                echo "ERROR: $service failed to start properly"
                exit 1
            fi
            ;;
        "ash-bot")
            if curl -f http://localhost:8882/health; then
                echo "$service updated successfully"
            else
                echo "ERROR: $service failed to start properly"
                exit 1
            fi
            ;;
        "ash-dash")
            if curl -f -k https://localhost:8883/health; then
                echo "$service updated successfully"
            else
                echo "ERROR: $service failed to start properly"
                exit 1
            fi
            ;;
        "ash-thrash")
            if curl -f http://localhost:8884/health; then
                echo "$service updated successfully"
            else
                echo "ERROR: $service failed to start properly"
                exit 1
            fi
            ;;
    esac
done

# Update monitoring services
echo "Updating monitoring services..."
docker-compose up -d prometheus grafana

# Final health check
echo "Running final health check..."
sleep 30
./scripts/health-check.sh

# Run quick test
echo "Running post-update validation..."
curl -X POST http://localhost:8884/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}'

echo "=== Rolling Update Complete ==="
EOF

chmod +x scripts/rolling-update.sh
```

### Monitoring and Alerting

**1. Production Monitoring Setup:**
```bash
# Create monitoring daemon
cat > scripts/production-monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="/opt/ash/ash/logs/production-monitor.log"
ALERT_THRESHOLD_CPU=85
ALERT_THRESHOLD_MEMORY=90
ALERT_THRESHOLD_GPU_TEMP=80
CHECK_INTERVAL=300  # 5 minutes

mkdir -p "$(dirname "$LOG_FILE")"

log_metric() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"
}

send_alert() {
    local message="$1"
    local severity="$2"
    
    log_metric "ALERT [$severity]: $message"
    
    # Send Discord webhook alert (configure webhook URL)
    if [[ -n "$DISCORD_WEBHOOK_URL" ]]; then
        curl -X POST "$DISCORD_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"content\": \"🚨 Ash Production Alert [$severity]: $message\"}"
    fi
    
    # Send email alert (configure email settings)
    if command -v mail &> /dev/null && [[ -n "$ALERT_EMAIL" ]]; then
        echo "$message" | mail -s "Ash Production Alert [$severity]" "$ALERT_EMAIL"
    fi
}

log_metric "Starting Ash production monitoring daemon"

while true; do
    # System metrics
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'.' -f1)
    MEMORY=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    DISK=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
    
    # GPU metrics
    if command -v nvidia-smi &> /dev/null; then
        GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits)
        GPU_MEM=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf "%.0f", $1/$2*100}')
        GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
    else
        GPU_TEMP=0
        GPU_MEM=0
        GPU_UTIL=0
    fi
    
    # Service health
    HEALTHY_SERVICES=0
    TOTAL_SERVICES=6  # bot, nlp, dash, thrash, postgres, redis
    
    for port in 8881 8882 8883 8884; do
        if curl -f -s -k "http://localhost:$port/health" &>/dev/null; then
            ((HEALTHY_SERVICES++))
        fi
    done
    
    # Database health
    if docker exec ash-postgres pg_isready -U ash_user -d ash_production &>/dev/null; then
        ((HEALTHY_SERVICES++))
    fi
    
    # Redis health
    if docker exec ash-redis redis-cli ping &>/dev/null; then
        ((HEALTHY_SERVICES++))
    fi
    
    # Log metrics
    log_metric "CPU:${CPU}% MEM:${MEMORY}% DISK:${DISK}% GPU_TEMP:${GPU_TEMP}C GPU_MEM:${GPU_MEM}% GPU_UTIL:${GPU_UTIL}% SERVICES:${HEALTHY_SERVICES}/${TOTAL_SERVICES}"
    
    # Check alert conditions
    if [ "$CPU" -gt "$ALERT_THRESHOLD_CPU" ]; then
        send_alert "High CPU usage: ${CPU}%" "WARNING"
    fi
    
    if [ "$MEMORY" -gt "$ALERT_THRESHOLD_MEMORY" ]; then
        send_alert "High memory usage: ${MEMORY}%" "CRITICAL"
    fi
    
    if [ "$GPU_TEMP" -gt "$ALERT_THRESHOLD_GPU_TEMP" ]; then
        send_alert "GPU overheating: ${GPU_TEMP}°C" "CRITICAL"
    fi
    
    if [ "$HEALTHY_SERVICES" -lt 5 ]; then
        send_alert "Multiple services unhealthy: ${HEALTHY_SERVICES}/${TOTAL_SERVICES}" "CRITICAL"
    fi
    
    if [ "$DISK" -gt 85 ]; then
        send_alert "High disk usage: ${DISK}%" "WARNING"
    fi
    
    sleep "$CHECK_INTERVAL"
done
EOF

chmod +x scripts/production-monitor.sh

# Run monitoring daemon as system service
sudo tee /etc/systemd/system/ash-monitor.service > /dev/null << 'EOF'
[Unit]
Description=Ash Production Monitoring
After=ash-ecosystem.service
Requires=ash-ecosystem.service

[Service]
Type=simple
User=ash
WorkingDirectory=/opt/ash/ash
ExecStart=/opt/ash/ash/scripts/production-monitor.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ash-monitor.service
sudo systemctl start ash-monitor.service
```

---

## 📞 Support & Troubleshooting

### Common Deployment Issues

**Container Startup Failures:**
```bash
# Check container logs
docker-compose logs ash-nlp

# Check resource constraints
docker stats

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Restart specific service
docker-compose restart ash-nlp
```

**Network Connectivity Issues:**
```bash
# Check Docker networks
docker network ls
docker network inspect ash_ash_network

# Test container communication
docker exec ash-bot ping ash-nlp
docker exec ash-bot curl http://ash-nlp:8881/health
```

**Performance Issues:**
```bash
# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check GPU utilization
nvidia-smi dmon -c 10 -s mu

# Optimize container resources
# Edit docker-compose.prod.yml resource limits
```

### Emergency Recovery

**Complete System Recovery:**
```bash
# Stop all services
docker-compose down

# Clean Docker environment
docker system prune -f

# Restore from backup
tar -xzf /opt/ash/backups/ash-ecosystem-YYYYMMDD-HHMM.tar.gz
# Copy configuration files back
# Restart services

# Emergency restart
./scripts/emergency-recovery.sh
```

### Support Resources

**Documentation:**
- **Ecosystem Setup:** [ecosystem_setup_v2_1.md](tech/ecosystem_setup_v2_1.md)
- **Troubleshooting:** [troubleshooting_v2_1.md](tech/troubleshooting_v2_1.md)
- **Team Guide:** [team/team_guide_v2_1.md](team/team_guide_v2_1.md)

**Community Support:**
- **Discord:** https://discord.gg/alphabetcartel (#tech-support)
- **GitHub Issues:** Component-specific bug reports
- **Emergency Contact:** @tech-lead role in Discord

---

**This deployment guide provides comprehensive instructions for deploying the Ash crisis detection ecosystem in a production environment using the centralized architecture. The containerized approach ensures consistent, reliable deployment while maintaining the system's core mission of supporting LGBTQIA+ community safety and wellbeing.**

**🌈 Together, we're building technology that saves lives and strengthens chosen family bonds.**

---

**Built with 🖤 for The Alphabet Cartel**  
**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org