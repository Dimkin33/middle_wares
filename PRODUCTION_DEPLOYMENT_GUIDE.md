# Production Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the Tennis Score Tracking application to a production server using Docker containerization.

## Prerequisites

### Server Requirements
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+ or compatible Linux distribution
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 10GB available space
- **CPU**: 2+ cores recommended
- **Network**: Public IP address and domain name (optional but recommended)

### Required Software
- Docker 20.10+ and Docker Compose 2.0+
- Git
- Text editor (nano, vim, etc.)
- SSL certificate (for HTTPS - recommended for production)

## Step 1: Server Setup

### 1.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
# For CentOS/RHEL: sudo yum update -y
```

### 1.2 Install Docker and Docker Compose
```bash
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
```

### 1.3 Configure Firewall
```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 2: Application Deployment

### 2.1 Clone Repository
```bash
cd /opt
sudo git clone https://github.com/your-username/tennis-scoreboard.git
sudo chown -R $USER:$USER tennis-scoreboard
cd tennis-scoreboard
```

### 2.2 Configure Environment Variables
```bash
# Copy and edit environment file
cp .env.example .env
nano .env
```

**Production Environment Configuration:**
```properties
# Database Configuration
POSTGRES_USER=tennis_prod_user
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_DB=tennis_production
DB_HOST_PORT=5432
DB_HOST=db
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_HOST_PORT}/${POSTGRES_DB}"

# Application Configuration
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# Security (if implementing authentication)
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
```

### 2.3 Configure Production Docker Compose
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: tennis_db_prod
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql:/docker-entrypoint-initdb.d
    networks:
      - tennis_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  app:
    build: .
    container_name: tennis_app_prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - APP_ENV=production
    depends_on:
      db:
        condition: service_healthy
    networks:
      - tennis_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: tennis_nginx_prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./src/tennis_score/public:/usr/share/nginx/html/static
    depends_on:
      - app
    networks:
      - tennis_network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  tennis_network:
    driver: bridge
```

### 2.4 Configure Production Nginx
Create `nginx/nginx.prod.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8080;
    }

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Static files
        location /static/ {
            root /usr/share/nginx/html;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Application
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }
}
```

## Step 3: SSL Certificate Setup

### 3.1 Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to nginx directory
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
sudo chown -R $USER:$USER nginx/ssl

# Setup auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3.2 Using Self-Signed Certificate (Development/Testing)
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out nginx/ssl/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

## Step 4: Database Backup Strategy

### 4.1 Create Backup Script
Create `scripts/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/tennis-scoreboard/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="tennis_db_prod"

mkdir -p $BACKUP_DIR

# Create database backup
docker exec $CONTAINER_NAME pg_dump -U tennis_prod_user tennis_production > $BACKUP_DIR/tennis_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "tennis_backup_*.sql" -mtime +7 -delete

echo "Backup completed: tennis_backup_$DATE.sql"
```

### 4.2 Setup Automated Backups
```bash
chmod +x scripts/backup_db.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /opt/tennis-scoreboard/scripts/backup_db.sh
```

## Step 5: Monitoring and Logging

### 5.1 Create Monitoring Script
Create `scripts/monitor.sh`:
```bash
#!/bin/bash

echo "=== Container Status ==="
docker ps

echo -e "\n=== Resource Usage ==="
docker stats --no-stream

echo -e "\n=== Disk Usage ==="
df -h /opt/tennis-scoreboard

echo -e "\n=== Application Logs (Last 20 lines) ==="
docker logs tennis_app_prod --tail 20

echo -e "\n=== Nginx Logs (Last 10 lines) ==="
docker logs tennis_nginx_prod --tail 10
```

### 5.2 Log Rotation Setup
Create `/etc/logrotate.d/docker-tennis`:
```
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 0644 root root
    postrotate
        docker kill -s USR1 $(docker ps -q) 2>/dev/null || true
    endscript
}
```

## Step 6: Deployment Process

### 6.1 Initial Deployment
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Test application
curl -I https://your-domain.com
```

### 6.2 Health Checks
```bash
# Check database connection
docker exec tennis_db_prod pg_isready -U tennis_prod_user -d tennis_production

# Check application health
curl -f http://localhost:8080/ || echo "App health check failed"

# Check nginx status
curl -I https://your-domain.com
```

## Step 7: Maintenance Procedures

### 7.1 Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Verify deployment
bash scripts/monitor.sh
```

### 7.2 Database Maintenance
```bash
# Manual backup
bash scripts/backup_db.sh

# Database cleanup (if needed)
docker exec tennis_db_prod psql -U tennis_prod_user -d tennis_production -c "VACUUM ANALYZE;"

# Restore from backup
docker exec -i tennis_db_prod psql -U tennis_prod_user -d tennis_production < backups/tennis_backup_YYYYMMDD_HHMMSS.sql
```

### 7.3 Scaling (Optional)
```bash
# Scale application instances
docker-compose -f docker-compose.prod.yml up -d --scale app=3

# Load balancer configuration (requires nginx update)
# See nginx documentation for upstream configuration
```

## Step 8: Security Hardening

### 8.1 System Security
```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Disable root SSH access
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart ssh
```

### 8.2 Application Security
- Use strong passwords in `.env` file
- Regularly update Docker images
- Implement rate limiting in nginx
- Monitor logs for suspicious activity
- Consider implementing authentication system

## Step 9: Performance Optimization

### 9.1 Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_matches_player1_id ON matches(player1_id);
CREATE INDEX IF NOT EXISTS idx_matches_player2_id ON matches(player2_id);
CREATE INDEX IF NOT EXISTS idx_matches_winner_id ON matches(winner_id);
CREATE INDEX IF NOT EXISTS idx_matches_uuid ON matches(uuid);
```

### 9.2 Nginx Caching
Add to nginx configuration:
```nginx
# Cache static files
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Cache HTML files for short time
location ~* \.html$ {
    expires 1h;
    add_header Cache-Control "public";
}
```

## Step 10: Troubleshooting

### 10.1 Common Issues
1. **Container won't start**: Check logs with `docker-compose logs`
2. **Database connection issues**: Verify environment variables and network connectivity
3. **SSL certificate issues**: Check certificate paths and permissions
4. **Performance issues**: Monitor resource usage with `docker stats`

### 10.2 Emergency Procedures
```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Emergency database backup
docker exec tennis_db_prod pg_dump -U tennis_prod_user tennis_production > emergency_backup.sql

# Restart services
docker-compose -f docker-compose.prod.yml up -d

# Check service health
bash scripts/monitor.sh
```

## Resource Requirements Summary

### Minimum Production Requirements
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 10GB
- **Network**: 100 Mbps

### Recommended Production Requirements
- **CPU**: 4 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **Network**: 1 Gbps
- **Backup Storage**: Additional 20GB

## Estimated Costs
- **VPS/Cloud Server**: $10-50/month depending on specs
- **Domain Name**: $10-15/year
- **SSL Certificate**: Free (Let's Encrypt) or $50-200/year (commercial)

## Support and Monitoring
- Monitor application health daily
- Check logs weekly
- Update system monthly
- Review security quarterly
- Plan for disaster recovery

---

**Note**: This deployment has been tested with Docker containerization and provides production-ready configuration. The application supports concurrent matches in memory with database persistence for completed matches.
