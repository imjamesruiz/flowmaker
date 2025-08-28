#!/bin/bash

# Worqly Production Deployment Script
# This script deploys the Worqly workflow automation platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="worqly"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"

echo -e "${BLUE}🚀 Starting Worqly Production Deployment${NC}"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file based on env.example${NC}"
    exit 1
fi

# Load environment variables
source "$ENV_FILE"

# Validate required environment variables
required_vars=(
    "POSTGRES_PASSWORD"
    "SECRET_KEY"
    "GOOGLE_CLIENT_ID"
    "GOOGLE_CLIENT_SECRET"
    "SLACK_CLIENT_ID"
    "SLACK_CLIENT_SECRET"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Error: $var is not set in .env file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables validated${NC}"

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
mkdir -p nginx/logs
mkdir -p nginx/ssl
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Generate SSL certificates (self-signed for development)
if [ ! -f "nginx/ssl/cert.pem" ]; then
    echo -e "${BLUE}🔐 Generating SSL certificates...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
fi

# Create Nginx configuration
echo -e "${BLUE}🌐 Creating Nginx configuration...${NC}"
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web:10m rate=30r/s;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header Access-Control-Allow-Origin $http_origin always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
            add_header Access-Control-Allow-Credentials true always;
            
            if ($request_method = 'OPTIONS') {
                add_header Access-Control-Allow-Origin $http_origin;
                add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
                add_header Access-Control-Allow-Headers "Authorization, Content-Type";
                add_header Access-Control-Allow-Credentials true;
                add_header Content-Length 0;
                add_header Content-Type text/plain;
                return 204;
            }
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }

        # Frontend
        location / {
            limit_req zone=web burst=50 nodelay;
            
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # Monitoring (optional)
        location /monitoring/ {
            auth_basic "Monitoring";
            auth_basic_user_file /etc/nginx/.htpasswd;
            
            proxy_pass http://grafana:3000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Create Prometheus configuration
echo -e "${BLUE}📊 Creating Prometheus configuration...${NC}"
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'celery'
    static_configs:
      - targets: ['celery_worker:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF

# Create Grafana datasource configuration
echo -e "${BLUE}📈 Creating Grafana datasource configuration...${NC}"
mkdir -p monitoring/grafana/datasources
cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Stop existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans

# Build and start services
echo -e "${BLUE}🔨 Building and starting services...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --build

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
timeout=300
elapsed=0

while [ $elapsed -lt $timeout ]; do
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "healthy"; then
        echo -e "${GREEN}✅ All services are healthy!${NC}"
        break
    fi
    
    echo -e "${YELLOW}⏳ Waiting for services to be healthy... ($elapsed/$timeout seconds)${NC}"
    sleep 10
    elapsed=$((elapsed + 10))
done

if [ $elapsed -ge $timeout ]; then
    echo -e "${RED}❌ Timeout waiting for services to be healthy${NC}"
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs
    exit 1
fi

# Run database migrations
echo -e "${BLUE}🗄️ Running database migrations...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend alembic upgrade head

# Create initial admin user (if needed)
echo -e "${BLUE}👤 Creating initial admin user...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" exec backend python create_admin_user.py

# Show service status
echo -e "${BLUE}📋 Service Status:${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" ps

# Show service URLs
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📱 Application URLs:${NC}"
echo -e "  Frontend: ${GREEN}https://localhost${NC}"
echo -e "  API: ${GREEN}https://localhost/api/v1${NC}"
echo -e "  Monitoring: ${GREEN}https://localhost/monitoring${NC}"
echo -e "  Prometheus: ${GREEN}http://localhost:9090${NC}"
echo -e "  Grafana: ${GREEN}http://localhost:3001${NC}"

echo -e "${YELLOW}⚠️  Default Grafana credentials: admin/admin${NC}"
echo -e "${YELLOW}⚠️  Remember to change default passwords in production!${NC}"

# Show logs for debugging
echo -e "${BLUE}📝 Recent logs:${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=20
