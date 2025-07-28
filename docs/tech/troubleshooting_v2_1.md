# 🚨 Ash Ecosystem Troubleshooting Guide v2.1 (Centralized Architecture)

**Repository:** https://github.com/the-alphabet-cartel/ash  
**Discord Community:** https://discord.gg/alphabetcartel  
**Website:** https://alphabetcartel.org

Comprehensive troubleshooting guide for the centralized Ash crisis detection ecosystem running on Linux server 10.20.30.253.

---

## 📋 Overview

This guide covers common issues, diagnostic procedures, and solutions for the Ash ecosystem v2.1 centralized architecture. All components run as Docker containers on a single Linux server with a unified Docker Compose configuration.

### 🏗️ System Architecture Reference

```
Linux Server (10.20.30.253)
┌─────────────────────────────────────────────────────────────────┐
│                    Ash Ecosystem v2.1                          │
│                 (Centralized Architecture)                      │
├─────────────────────────────────────────────────────────────────┤
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

---

## 🔧 Quick Diagnostic Commands

### System Health Check

**Complete Ecosystem Health Check:**
```bash
#!/bin/bash
echo "=== Ash Ecosystem Health Check ==="
echo "Server: $(hostname) ($(hostname -I | awk '{print $1}'))"
echo "Timestamp: $(date)"
echo

# Check Docker daemon
echo "Docker Status:"
systemctl is-active docker && echo "✅ Docker daemon running" || echo "❌ Docker daemon stopped"

# Check containers
echo -e "\nContainer Status:"
docker-compose ps

echo -e "\nDetailed Container Health:"
containers=("ash-postgres" "ash-redis" "ash-nlp" "ash-bot" "ash-dash" "ash-thrash")
for container in "${containers[@]}"; do
    if docker inspect "$container" &>/dev/null; then
        status=$(docker inspect --format='{{.State.Status}}' "$container")
        health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
        echo "$container: $status ($health)"
    else
        echo "$container: ❌ Not found"
    fi
done

# Service health endpoints
echo -e "\nService Health Endpoints:"
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

# Database connectivity
echo -n "Testing Database... "
if docker exec ash-postgres pg_isready -U ash_user -d ash_production > /dev/null 2>&1; then
    echo "✅ Connected"
else
    echo "❌ Failed"
fi

# Redis connectivity
echo -n "Testing Redis... "
if docker exec ash-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Connected"
else
    echo "❌ Failed"
fi

# GPU access
echo -n "Testing GPU Access... "
if docker exec ash-nlp nvidia-smi > /dev/null 2>&1; then
    echo "✅ Available"
else
    echo "⚠️ Not Available"
fi

# System resources
echo -e "\nSystem Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "%s", $5}')"

if command -v nvidia-smi &> /dev/null; then
    echo "GPU Memory: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | awk -F', ' '{printf "%.1f%%", $1/$2*100}')"
    echo "GPU Temperature: $(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits)°C"
fi

# Docker network
echo -e "\nDocker Network:"
docker network inspect ash_ash_network --format='{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null || echo "Network not found"

echo -e "\n=== Health Check Complete ==="
```

### Quick Container Status Check

```bash
# Quick status overview
echo "=== Quick Status Check ==="
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Check logs for errors
echo -e "\nRecent Errors:"
docker-compose logs --tail=5 | grep -i "error\|exception\|fail" | tail -10
```

---

## 🚨 Common Issues & Solutions

### 1. Docker Compose Issues

**Problem: Services not starting or failing to communicate**

**Symptoms:**
- Containers showing "Exited" status
- Services can't reach each other
- Health checks failing

**Diagnosis:**
```bash
# Check overall compose status
docker-compose ps

# Check specific service logs
docker-compose logs ash-nlp
docker-compose logs ash-bot
docker-compose logs ash-dash
docker-compose logs ash-thrash

# Check Docker network
docker network ls
docker network inspect ash_ash_network
```

**Solutions:**

1. **Restart Entire Ecosystem:**
```bash
# Stop all services
docker-compose down

# Wait for cleanup
sleep 10

# Start in dependency order
docker-compose up -d postgres redis
sleep 30

docker-compose up -d ash-nlp
sleep 45

docker-compose up -d ash-bot ash-dash ash-thrash
sleep 30

# Verify health
docker-compose ps
```

2. **Rebuild Containers:**
```bash
# Stop services
docker-compose down

# Remove containers and rebuild
docker-compose build --no-cache

# Start services
docker-compose up -d
```

3. **Clean Docker Environment:**
```bash
# Stop services
docker-compose down -v

# Clean up Docker resources
docker system prune -f
docker volume prune -f
docker network prune -f

# Restart services
docker-compose up -d
```

---

### 2. Database Connection Issues

**Problem: Services cannot connect to PostgreSQL**

**Symptoms:**
- "Connection refused" errors in logs
- Services failing to start
- Database health check failing

**Diagnosis:**
```bash
# Check database container
docker inspect ash-postgres

# Check database logs
docker-compose logs postgres

# Test connection from host
docker exec ash-postgres pg_isready -U ash_user -d ash_production

# Test connection from app containers
docker exec ash-nlp curl -f http://postgres:5432 || echo "Cannot reach database"
```

**Solutions:**

1. **Restart Database:**
```bash
# Restart database container
docker-compose restart postgres

# Wait for initialization
sleep 30

# Test connection
docker exec ash-postgres pg_isready -U ash_user -d ash_production
```

2. **Check Database Configuration:**
```bash
# Verify environment variables
grep -E "POSTGRES_|DATABASE_URL" .env

# Check database initialization
docker-compose logs postgres | grep -i "database system is ready"
```

3. **Reset Database (CAUTION: Data Loss):**
```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm ash_postgres_data

# Restart services (will recreate database)
docker-compose up -d postgres
sleep 60

# Check database initialization
docker-compose logs postgres
```

---

### 3. GPU/CUDA Issues

**Problem: NLP server can't access GPU**

**Symptoms:**
- NLP server using CPU instead of GPU
- CUDA errors in nlp logs
- Slow processing times

**Diagnosis:**
```bash
# Check GPU on host
nvidia-smi

# Check GPU in container
docker exec ash-nlp nvidia-smi

# Check CUDA installation in container
docker exec ash-nlp nvcc --version

# Check GPU memory usage
docker exec ash-nlp nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

**Solutions:**

1. **Restart NLP Service with GPU:**
```bash
# Stop NLP service
docker-compose stop ash-nlp

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Restart NLP service
docker-compose up -d ash-nlp

# Verify GPU access
docker exec ash-nlp nvidia-smi
```

2. **Check Docker GPU Configuration:**
```bash
# Verify Docker daemon configuration
cat /etc/docker/daemon.json

# Restart Docker daemon if needed
sudo systemctl restart docker

# Wait for Docker to start
sleep 10

# Restart services
docker-compose up -d
```

3. **Update NVIDIA Container Toolkit:**
```bash
# Update package lists
sudo apt update

# Update NVIDIA container toolkit
sudo apt install --only-upgrade nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker

# Restart NLP service
docker-compose up -d ash-nlp
```

---

### 4. Service Communication Issues

**Problem: Services can't communicate with each other**

**Symptoms:**
- Bot can't reach NLP server
- Dashboard can't connect to services
- API calls timing out

**Diagnosis:**
```bash
# Check Docker network
docker network inspect ash_ash_network

# Test container-to-container communication
docker exec ash-bot curl -f http://ash-nlp:8881/health
docker exec ash-dash curl -f http://ash-bot:8882/health
docker exec ash-dash curl -f http://ash-nlp:8881/health
docker exec ash-dash curl -f http://ash-thrash:8884/health

# Check service logs for connection errors
docker-compose logs | grep -i "connection\|timeout\|refused"
```

**Solutions:**

1. **Restart Services in Order:**
```bash
# Stop all application services
docker-compose stop ash-bot ash-dash ash-thrash ash-nlp

# Start NLP server first
docker-compose up -d ash-nlp
sleep 30

# Start other services
docker-compose up -d ash-bot ash-dash ash-thrash
sleep 20

# Test communication
docker exec ash-bot curl -f http://ash-nlp:8881/health
```

2. **Recreate Docker Network:**
```bash
# Stop all services
docker-compose down

# Remove network
docker network rm ash_ash_network 2>/dev/null || true

# Restart services (will recreate network)
docker-compose up -d

# Verify network
docker network inspect ash_ash_network
```

3. **Check Service Configuration:**
```bash
# Verify service URLs in environment
grep -E "_URL|_API" .env

# Check if services are using correct internal hostnames
docker-compose config | grep -A 5 -B 5 "http://"
```

---

### 5. SSL/Certificate Issues

**Problem: Dashboard SSL certificate errors**

**Symptoms:**
- "Certificate not trusted" browser errors
- SSL handshake failures
- Dashboard not accessible via HTTPS

**Diagnosis:**
```bash
# Check certificate files
ls -la certs/

# Test certificate validity
openssl x509 -in certs/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:8883 -servername dashboard.alphabetcartel.net

# Check dashboard logs for SSL errors
docker-compose logs ash-dash | grep -i ssl
```

**Solutions:**

1. **Regenerate Self-Signed Certificate:**
```bash
# Remove old certificates
rm -f certs/*

# Generate new certificate
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=TheAlphabetCartel/CN=dashboard.alphabetcartel.net"

# Set permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem

# Restart dashboard
docker-compose restart ash-dash

# Test access
curl -k https://localhost:8883/health
```

2. **Disable SSL Temporarily:**
```bash
# Update environment file
sed -i 's/ENABLE_SSL=true/ENABLE_SSL=false/' .env

# Restart dashboard
docker-compose restart ash-dash

# Test HTTP access
curl http://localhost:8883/health
```

3. **Use Let's Encrypt (Production):**
```bash
# Install certbot
sudo apt install certbot

# Stop dashboard temporarily
docker-compose stop ash-dash

# Generate certificate
sudo certbot certonly --standalone -d dashboard.alphabetcartel.net

# Copy certificates
sudo cp /etc/letsencrypt/live/dashboard.alphabetcartel.net/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/dashboard.alphabetcartel.net/privkey.pem certs/key.pem
sudo chown $USER:$USER certs/*

# Restart dashboard
docker-compose up -d ash-dash
```

---

### 6. Performance Issues

**Problem: Slow response times or high resource usage**

**Symptoms:**
- Crisis detection taking >5 seconds
- High CPU/memory usage
- System becoming unresponsive
- Out of memory errors

**Diagnosis:**
```bash
#