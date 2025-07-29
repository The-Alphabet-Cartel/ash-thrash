# Ash-Thrash Deployment Guide v2.1

**Comprehensive production deployment guide for the Ash-Thrash testing suite on dedicated server infrastructure.**

---

## 🎯 Deployment Overview

### Target Environment
- **Server**: Dedicated Debian 12 Linux server (10.20.30.253)
- **Hardware**: AMD Ryzen 7 5800X, 64GB RAM, NVIDIA RTX 3060
- **Container Platform**: Docker with Docker Compose
- **Network**: Internal network (10.20.30.0/24)
- **Dependencies**: Ash-NLP server (10.20.30.253:8881)

### Deployment Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Dedicated Server                         │
│                   (10.20.30.253)                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Ash-Bot     │  │  Ash-NLP     │  │ Ash-Dashboard │      │
│  │  Port 8882   │  │  Port 8881   │  │  Port 8883   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Ash-Thrash   │  │  PostgreSQL  │  │   Redis      │      │
│  │  Port 8884   │  │  Port 5432   │  │  Port 6379   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Production Deployment

### Step 1: Server Preparation

**System Requirements Check:**
```bash
# Verify system resources
echo "=== System Information ==="
uname -a
cat /etc/debian_version
lscpu | grep "Model name"
free -h
df -h
nvidia-smi  # Verify GPU availability

# Check network connectivity
ping -c 3 10.20.30.253
nc -zv 10.20.30.253 8881  # Test NLP server connectivity
```

**Install Dependencies:**
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

# Verify installation
docker --version
docker-compose --version

# Logout and login to apply group changes
```

### Step 2: Repository Setup

**Clone Repository:**
```bash
# Create project directory
sudo mkdir -p /opt/ash-thrash
sudo chown $USER:$USER /opt/ash-thrash
cd /opt/ash-thrash

# Clone repository
git clone https://github.com/the-alphabet-cartel/ash-thrash.git .

# Verify repository structure
ls -la
git branch
git status
```

**Setup Directory Structure:**
```bash
# Create required directories
mkdir -p logs results/comprehensive results/quick_validation results/reports results/backups
mkdir -p config data

# Set appropriate permissions
chmod 755 logs results config data
chmod 644 .env.template docker-compose.yml
chmod +x setup.sh

# Create symbolic links for easy access
sudo ln -sf /opt/ash-thrash /home/$USER/ash-thrash
```

### Step 3: Environment Configuration

**Create Production Environment File:**
```bash
# Copy template
cp .env.template .env

# Configure production environment
cat > .env << 'EOF'
# Production Environment Configuration - Ash-Thrash v2.1

# === Core Service Configuration ===
GLOBAL_NLP_API_URL=http://10.20.30.253:8881
NLP_API_TIMEOUT=30
NLP_MAX_RETRIES=3

# === API Server Configuration ===
THRASH_API_HOST=0.0.0.0
GLOBAL_THRASH_API_PORT=8884
GLOBAL_ENABLE_DEBUG_MODE=false
API_MAX_WORKERS=4
API_REQUEST_TIMEOUT=60

# === Database Configuration ===
DATABASE_HOST=ash-thrash-db
DATABASE_PORT=5432
DATABASE_NAME=ash_thrash_prod
DATABASE_USER=ash_user
DATABASE_PASSWORD=YOUR_SECURE_DATABASE_PASSWORD_HERE

# === Redis Configuration ===
REDIS_HOST=ash-thrash-redis
REDIS_PORT=6379
REDIS_PASSWORD=YOUR_SECURE_REDIS_PASSWORD_HERE

# === Testing Configuration ===
THRASH_ENABLE_SCHEDULED_TESTS=true
THRASH_COMPREHENSIVE_TEST_INTERVAL=daily
THRASH_QUICK_TEST_INTERVAL=hourly
THRASH_MAX_CONCURRENT_TESTS=2
TEST_TIMEOUT=600

# === Security Configuration ===
GLOBAL_SESSION_TOKEN=YOUR_SECURE_SECRET_KEY_HERE
THRASH_API_RATE_LIMIT=100
THRASH_ENABLE_API_AUTHENTICATION=true
ALLOWED_HOSTS=10.20.30.253,localhost,127.0.0.1

# === Monitoring Configuration ===
GLOBAL_LOG_LEVEL=INFO

# === Notification Configuration ===
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_DISCORD_NOTIFICATIONS=true
DISCORD_WEBHOOK_URL=YOUR_DISCORD_WEBHOOK_URL_HERE

# === Performance Configuration ===
ENABLE_CACHING=true
CACHE_TTL=300
MAX_MEMORY_USAGE=4GB
ENABLE_COMPRESSION=true

# === Development/Debug (Production: false) ===
DEBUG_MODE=false
ENABLE_TEST_DATA_EXPORT=true
EOF

# Secure environment file
chmod 600 .env
```

**Generate Secure Passwords:**
```bash
# Generate secure passwords
echo "Database Password: $(openssl rand -base64 32)"
echo "Redis Password: $(openssl rand -base64 32)"
echo "Secret Key: $(openssl rand -hex 32)"

# Update .env file with generated passwords
# sed -i 's/YOUR_SECURE_DATABASE_PASSWORD_HERE/actual_password/g' .env
# sed -i 's/YOUR_SECURE_REDIS_PASSWORD_HERE/actual_password/g' .env
# sed -i 's/YOUR_SECURE_SECRET_KEY_HERE/actual_key/g' .env
```

### Step 4: Docker Configuration

**Create Production Docker Compose:**
```bash
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  ash-thrash:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: ash-thrash-prod
    ports:
      - "8884:8884"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env
    volumes:
      - ./results:/app/results
      - ./logs:/app/logs
      - ./config:/app/config
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8884/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    depends_on:
      ash-thrash-db:
        condition: service_healthy
      ash-thrash-redis:
        condition: service_healthy
    networks:
      - ash-network
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  ash-thrash-db:
    image: postgres:15-alpine
    container_name: ash-thrash-db-prod
    environment:
      GLOBAL_POSTGRES_DB: ${DATABASE_NAME}
      GLOBAL_POSTGRES_USER: ${DATABASE_USER}
      GLOBAL_POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --lc-collate=C --lc-ctype=C"
    volumes:
      - ash_thrash_prod_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER} -d ${DATABASE_NAME}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    networks:
      - ash-network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  ash-thrash-redis:
    image: redis:7-alpine
    container_name: ash-thrash-redis-prod
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - ash_thrash_redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    networks:
      - ash-network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

volumes:
  ash_thrash_prod_data:
    driver: local
  ash_thrash_redis_data:
    driver: local

networks:
  ash-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF
```

**Create Production Dockerfile:**
```bash
cat > Dockerfile.prod << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create non-root user
RUN groupadd -r ash && useradd -r -g ash ash
RUN chown -R ash:ash /app
USER ash

# Create required directories
RUN mkdir -p results logs data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8884/health || exit 1

# Expose port
EXPOSE 8884

# Start application
CMD ["python", "src/api/server.py"]
EOF
```

### Step 5: Database Initialization

**Create Database Schema:**
```bash
mkdir -p database/init

cat > database/init/01-init-database.sql << 'EOF'
-- Ash-Thrash Production Database Schema
-- Version 2.1

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS ash_thrash;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default schema
SET search_path TO ash_thrash, public;

-- Test execution tracking
CREATE TABLE test_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'running',
    total_phrases INTEGER,
    successful_tests INTEGER,
    failed_tests INTEGER,
    success_rate DECIMAL(5,2),
    execution_time_seconds INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test results storage
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES test_executions(id) ON DELETE CASCADE,
    phrase_id VARCHAR(50) NOT NULL,
    phrase_text TEXT NOT NULL,
    expected_category VARCHAR(50) NOT NULL,
    expected_priority INTEGER NOT NULL,
    detected_category VARCHAR(50),
    detected_priority INTEGER,
    confidence_score DECIMAL(5,4),
    response_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    nlp_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES test_executions(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(20),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System health tracking
CREATE TABLE health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    response_time_ms INTEGER,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_test_executions_type_date ON test_executions(test_type, started_at);
CREATE INDEX idx_test_executions_status ON test_executions(status);
CREATE INDEX idx_test_results_execution ON test_results(execution_id);
CREATE INDEX idx_test_results_success ON test_results(success);
CREATE INDEX idx_test_results_category ON test_results(expected_category);
CREATE INDEX idx_performance_metrics_execution ON performance_metrics(execution_id);
CREATE INDEX idx_health_checks_service_date ON health_checks(service_name, checked_at);

-- Create analytics views
CREATE VIEW analytics.test_summary AS
SELECT 
    test_type,
    DATE(started_at) as test_date,
    COUNT(*) as total_executions,
    AVG(success_rate) as avg_success_rate,
    AVG(execution_time_seconds) as avg_execution_time,
    MIN(success_rate) as min_success_rate,
    MAX(success_rate) as max_success_rate
FROM test_executions 
WHERE status = 'completed'
GROUP BY test_type, DATE(started_at)
ORDER BY test_date DESC;

CREATE VIEW analytics.category_performance AS
SELECT 
    expected_category,
    COUNT(*) as total_tests,
    COUNT(*) FILTER (WHERE success = true) as successful_tests,
    ROUND(COUNT(*) FILTER (WHERE success = true) * 100.0 / COUNT(*), 2) as success_rate,
    AVG(confidence_score) as avg_confidence,
    AVG(response_time_ms) as avg_response_time
FROM test_results
GROUP BY expected_category
ORDER BY success_rate DESC;

-- Create audit triggers
CREATE OR REPLACE FUNCTION audit.track_changes()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_test_executions_updated
    BEFORE UPDATE ON test_executions
    FOR EACH ROW
    EXECUTE FUNCTION audit.track_changes();

-- Create database user with limited permissions
CREATE USER ash_readonly WITH PASSWORD 'readonly_password_here';
GRANT CONNECT ON DATABASE ash_thrash_prod TO ash_readonly;
GRANT USAGE ON SCHEMA ash_thrash, analytics TO ash_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA ash_thrash, analytics TO ash_readonly;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA ash_thrash TO ash_readonly;

-- Set up regular maintenance
CREATE OR REPLACE FUNCTION maintenance.cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Clean up test results older than retention period
    DELETE FROM test_results 
    WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- Clean up health checks older than 30 days
    DELETE FROM health_checks 
    WHERE checked_at < NOW() - INTERVAL '30 days';
    
    -- Update statistics
    ANALYZE;
END;
$$ LANGUAGE plpgsql;
EOF
```

### Step 6: Production Deployment

**Build and Deploy:**
```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# Start database first
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d ash-thrash-db ash-thrash-redis

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 30

# Start main application
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d ash-thrash

# Check deployment status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

**Verify Deployment:**
```bash
# Check container health
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker-compose logs ash-thrash | tail -20

# Test API endpoints
curl -f http://localhost:8884/health
curl -f http://localhost:8884/api/status

# Test NLP connectivity
curl -X POST http://localhost:8884/api/test/quick

# Check database connectivity
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "\dt"
```

### Step 7: Post-Deployment Configuration

**Setup Monitoring:**
```bash
# Create monitoring script
cat > /opt/ash-thrash/scripts/health-monitor.sh << 'EOF'
#!/bin/bash
# Ash-Thrash Health Monitoring Script

LOG_FILE="/opt/ash-thrash/logs/health-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# Check API health
if curl -sf http://localhost:8884/health > /dev/null; then
    log_message "API: Healthy"
else
    log_message "API: UNHEALTHY - Service not responding"
    # Send alert here
fi

# Check database connectivity
if docker-compose exec -T ash-thrash-db pg_isready -U ash_user > /dev/null; then
    log_message "Database: Healthy"
else
    log_message "Database: UNHEALTHY - Connection failed"
fi

# Check NLP server connectivity
if curl -sf http://10.20.30.253:8881/health > /dev/null; then
    log_message "NLP Server: Healthy"
else
    log_message "NLP Server: UNHEALTHY - Cannot reach NLP service"
fi

# Check disk space
DISK_USAGE=$(df /opt/ash-thrash | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    log_message "Storage: WARNING - Disk usage at ${DISK_USAGE}%"
else
    log_message "Storage: Healthy (${DISK_USAGE}% used)"
fi
EOF

chmod +x /opt/ash-thrash/scripts/health-monitor.sh
```

**Setup Scheduled Tasks:**
```bash
# Add cron jobs for monitoring and maintenance
(crontab -l 2>/dev/null; cat <<EOF
# Ash-Thrash Monitoring and Maintenance

# Health monitoring every 5 minutes
*/5 * * * * /opt/ash-thrash/scripts/health-monitor.sh

# Daily comprehensive test at 2 AM
0 2 * * * cd /opt/ash-thrash && docker-compose exec -T ash-thrash python src/comprehensive_testing.py

# Hourly quick validation
0 * * * * cd /opt/ash-thrash && docker-compose exec -T ash-thrash python src/quick_validation.py

# Weekly cleanup at 3 AM Sunday
0 3 * * 0 cd /opt/ash-thrash && docker-compose exec -T ash-thrash python src/maintenance/cleanup.py

# Monthly backup at 1 AM on the 1st
0 1 1 * * cd /opt/ash-thrash && docker-compose exec -T ash-thrash python src/maintenance/backup.py

# Weekly restart for maintenance (Sunday 4 AM)
0 4 * * 0 cd /opt/ash-thrash && docker-compose restart ash-thrash

EOF
) | crontab -
```

**Setup Log Rotation:**
```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/ash-thrash << 'EOF'
/opt/ash-thrash/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 ash ash
    postrotate
        docker-compose -f /opt/ash-thrash/docker-compose.yml -f /opt/ash-thrash/docker-compose.prod.yml restart ash-thrash
    endscript
}
EOF
```

### Step 8: Security Hardening

**Firewall Configuration:**
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (adjust port as needed)
sudo ufw allow 22/tcp

# Allow internal network access to API
sudo ufw allow from 10.20.30.0/24 to any port 8884

# Allow specific services
sudo ufw allow from 10.20.30.253 to any port 8881  # NLP server access
sudo ufw status verbose
```

**SSL/TLS Configuration (Optional):**
```bash
# If using external access, setup SSL with Let's Encrypt
# sudo apt install certbot
# sudo certbot certonly --standalone -d your-domain.com

# Update nginx or reverse proxy configuration
# Reference: docs/tech/ssl_setup.md
```

**Backup Strategy:**
```bash
# Create backup script
cat > /opt/ash-thrash/scripts/backup.sh << 'EOF'
#!/bin/bash
# Ash-Thrash Backup Script

BACKUP_DIR="/opt/backups/ash-thrash"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="ash-thrash_backup_${TIMESTAMP}.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Stop services for consistent backup
cd /opt/ash-thrash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml stop ash-thrash

# Create database backup
docker-compose exec -T ash-thrash-db pg_dump -U ash_user ash_thrash_prod > "$BACKUP_DIR/database_${TIMESTAMP}.sql"

# Create application backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    --exclude='logs/*' \
    --exclude='results/*/temp/*' \
    /opt/ash-thrash

# Restart services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml start ash-thrash

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x /opt/ash-thrash/scripts/backup.sh
```

---

## 🔧 Configuration Management

### Environment Profiles

**Production Configuration:**
```bash
# Production optimizations in .env
ENVIRONMENT=production
DEBUG_MODE=false
GLOBAL_LOG_LEVEL=INFO
API_WORKERS=4
ENABLE_CACHING=true
CACHE_TTL=300
MAX_MEMORY_USAGE=4GB
```

**Staging Configuration:**
```bash
# Create staging environment
cp .env .env.staging

# Staging-specific settings
sed -i 's/DATABASE_NAME=ash_thrash_prod/DATABASE_NAME=ash_thrash_staging/g' .env.staging
sed -i 's/GLOBAL_THRASH_API_PORT=8884/GLOBAL_THRASH_API_PORT=8885/g' .env.staging
sed -i 's/DEBUG_MODE=false/DEBUG_MODE=true/g' .env.staging
```

### Load Balancing (Future)

**Nginx Configuration Template:**
```nginx
upstream ash_thrash_backend {
    server 10.20.30.253:8884 weight=1 max_fails=3 fail_timeout=30s;
    # Add additional servers for load balancing
}

server {
    listen 80;
    server_name ash-thrash.internal;

    location / {
        proxy_pass http://ash_thrash_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health check
        proxy_next_upstream error timeout http_500 http_502 http_503;
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }

    location /health {
        access_log off;
        proxy_pass http://ash_thrash_backend/health;
    }
}
```

---

## 📊 Monitoring & Alerting

### Metrics Collection

**Prometheus Configuration:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ash-thrash'
    static_configs:
      - targets: ['10.20.30.253:8884']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'ash-nlp'
    static_configs:
      - targets: ['10.20.30.253:8881']
    metrics_path: /metrics
    scrape_interval: 30s
```

**Grafana Dashboard Setup:**
```json
{
  "dashboard": {
    "title": "Ash-Thrash Performance",
    "panels": [
      {
        "title": "Test Success Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "avg(ash_thrash_test_success_rate)",
            "refId": "A"
          }
        ]
      },
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, ash_thrash_http_request_duration_seconds_bucket)",
            "refId": "B"
          }
        ]
      }
    ]
  }
}
```

### Alert Rules

**Alert Manager Configuration:**
```yaml
# alertmanager.yml
groups:
  - name: ash-thrash-alerts
    rules:
      - alert: AshThrashServiceDown
        expr: up{job="ash-thrash"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Ash-Thrash service is down"
          description: "The Ash-Thrash testing service has been down for more than 2 minutes"

      - alert: AshThrashTestFailureRate
        expr: rate(ash_thrash_test_failures_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High test failure rate detected"
          description: "Test failure rate is {{ $value }} per second"

      - alert: AshThrashNLPConnectivity
        expr: ash_thrash_nlp_connectivity == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Cannot connect to NLP server"
          description: "Ash-Thrash cannot reach the NLP server"
```

---

## 🚨 Troubleshooting

### Common Issues

**Service Won't Start:**
```bash
# Check logs
docker-compose logs ash-thrash
docker-compose logs ash-thrash-db

# Check port conflicts
sudo netstat -tulpn | grep 8884
sudo lsof -i :8884

# Check disk space
df -h /opt/ash-thrash

# Check permissions
ls -la /opt/ash-thrash/.env
```

**Database Connection Issues:**
```bash
# Test database connectivity
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "SELECT 1;"

# Check database logs
docker-compose logs ash-thrash-db

# Reset database if needed
docker-compose down
docker volume rm ash-thrash_ash_thrash_prod_data
docker-compose up -d ash-thrash-db
```

**NLP Server Connectivity:**
```bash
# Test NLP server
curl -v http://10.20.30.253:8881/health

# Check network connectivity
ping 10.20.30.253
nc -zv 10.20.30.253 8881

# Check firewall rules
sudo ufw status
sudo iptables -L
```

### Recovery Procedures

**Emergency Restart:**
```bash
# Full system restart
cd /opt/ash-thrash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
docker system prune -f
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify health
sleep 60
curl http://localhost:8884/health
```

**Database Recovery:**
```bash
# Restore from backup
cd /opt/ash-thrash
docker-compose stop ash-thrash
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod < /opt/backups/ash-thrash/database_TIMESTAMP.sql
docker-compose start ash-thrash
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Review system logs
- Check disk usage
- Validate backup integrity
- Review test performance metrics

**Monthly:**
- Update Docker images
- Review security logs
- Update SSL certificates (if applicable)
- Performance optimization review

**Quarterly:**
- Full system backup verification
- Security audit
- Performance benchmarking
- Documentation updates

### Support Channels

**Technical Support:**
- **GitHub Issues**: https://github.com/the-alphabet-cartel/ash-thrash/issues
- **Discord**: #tech-support in https://discord.gg/alphabetcartel
- **Documentation**: Complete guides in docs/ directory

**Emergency Contacts:**
- **Technical Lead**: [Contact information]
- **System Administrator**: [Contact information]  
- **Crisis Response Lead**: [Contact information]

---

**This deployment guide ensures a robust, secure, and maintainable Ash-Thrash installation that integrates seamlessly with the broader Ash ecosystem while providing comprehensive testing capabilities for crisis detection systems.**

**Built with 🖤 for chosen family everywhere.**

**The Alphabet Cartel** - Building inclusive gaming communities through technology.

**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org | **GitHub:** https://github.com/the-alphabet-cartel