# Production Deployment Guide

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

Complete guide for deploying the FastAPI RealWorld Demo to production environments.

> **⚠️ Important Note**: This guide provides deployment strategies and configurations, but the application currently focuses on development best practices. Additional production hardening, monitoring setup, and security configurations will be needed for enterprise production deployments.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Environment Configuration](#environment-configuration)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Security Considerations](#security-considerations)
- [Monitoring and Logging](#monitoring-and-logging)
- [Performance Optimization](#performance-optimization)

## Deployment Options

### 1. Docker + Cloud Provider (Recommended)

Best for scalability and ease of management:
- **Application**: Docker container
- **Database**: Managed PostgreSQL (AWS RDS, Google Cloud SQL)
- **Orchestration**: Docker Compose or Kubernetes
- **Reverse Proxy**: Nginx or cloud load balancer

### 2. Traditional VPS Deployment

For smaller applications or budget constraints:
- **Server**: Ubuntu/CentOS VPS
- **Process Manager**: systemd or supervisor
- **Database**: PostgreSQL on same server or separate
- **Reverse Proxy**: Nginx

### 3. Serverless Deployment

For variable workloads:
- **Platform**: AWS Lambda, Google Cloud Functions
- **Database**: Managed PostgreSQL
- **API Gateway**: Cloud provider's API gateway

## Environment Configuration

### Production Environment Variables

Create a `.env.prod` file with production settings:

```bash
# Application
SECRET_KEY=your-super-secure-secret-key-min-32-chars
DEBUG=False
ENVIRONMENT=production

# Database
POSTGRES_USER=your-prod-user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=realworld-prod
POSTGRES_HOST=your-db-host.amazonaws.com
POSTGRES_PORT=5432

# Security
ALLOWED_HOSTS=["yourdomain.com", "www.yourdomain.com"]
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# JWT
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Security Checklist

- [ ] Strong `SECRET_KEY` (min 32 characters, random)
- [ ] `DEBUG=False` in production
- [ ] Secure database credentials
- [ ] HTTPS only (`SECURE_SSL_REDIRECT=True`)
- [ ] Proper CORS configuration
- [ ] Environment variables stored securely

## Docker Deployment

### Production Dockerfile

```dockerfile
# Dockerfile.prod
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/opt/poetry-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Install the application
RUN poetry install --only-root

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthcheck || exit 1

# Run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/key.pem;

        # SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files (if any)
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## Cloud Deployment

### AWS Deployment

#### Option 1: ECS with Fargate

```yaml
# ecs-task-definition.json
{
  "family": "realworld-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "realworld-api",
      "image": "your-registry/realworld-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "POSTGRES_HOST",
          "value": "your-rds-endpoint.amazonaws.com"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:prod/realworld-secrets"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/realworld-api",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Option 2: Elastic Beanstalk

```yaml
# .ebextensions/01-packages.config
packages:
  yum:
    postgresql-devel: []

# .ebextensions/02-python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /opt/python/current/app
```

### Google Cloud Platform

#### Cloud Run Deployment

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: realworld-api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/cpu-throttling: "true"
    spec:
      containerConcurrency: 1000
      timeoutSeconds: 300
      containers:
      - image: gcr.io/your-project/realworld-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_HOST
          value: "your-cloud-sql-ip"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        resources:
          limits:
            cpu: 1000m
            memory: 512Mi
```

### Digital Ocean App Platform

```yaml
# .do/app.yaml
name: realworld-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/fastapi-realworld-demo
    branch: main
  run_command: poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: SECRET_KEY
    value: your-secret-key
    type: SECRET
  - key: POSTGRES_HOST
    value: your-db-host
  - key: POSTGRES_DB
    value: realworld_prod
databases:
- name: realworld-db
  engine: PG
  version: "13"
```

## Security Considerations

### Application Security

1. **Environment Variables**
   - Never commit secrets to version control
   - Use secret management services (AWS Secrets Manager, etc.)
   - Rotate secrets regularly

2. **Database Security**
   - Use connection pooling
   - Enable SSL/TLS for database connections
   - Regular backups and point-in-time recovery
   - Database user with minimal permissions

3. **Network Security**
   - Use HTTPS everywhere
   - Configure proper CORS settings
   - Consider implementing rate limiting (not currently implemented)
   - Use a Web Application Firewall (WAF)

### Deployment Security Script

```bash
#!/bin/bash
# deploy-security-check.sh

echo "🔍 Running security checks..."

# Check for secrets in environment
if grep -r "password\|secret\|key" .env.prod; then
    echo "❌ Potential secrets found in environment file"
    exit 1
fi

# Check SSL certificates
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo "❌ SSL certificates not found"
    exit 1
fi

# Check database connection
if ! poetry run python -c "from app.adapters.orm.engine import get_engine; import asyncio; asyncio.run(get_engine().dispose())"; then
    echo "❌ Database connection failed"
    exit 1
fi

echo "✅ Security checks passed"
```

## Monitoring and Logging

### Application Logging

```python
# app/config/logging.py
import logging
import sys
from typing import Any

def setup_logging(log_level: str = "INFO", log_format: str = "text") -> None:
    """Configure application logging."""
    
    if log_format == "json":
        import json
        
        class JSONFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_data = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                return json.dumps(log_data)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
    else:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        )
        handler.setFormatter(formatter)
    
    logging.root.handlers = [handler]
    logging.root.setLevel(getattr(logging, log_level.upper()))
```

### Health Check Endpoint

```python
# app/api/healthcheck.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.adapters.orm.engine import get_engine

router = APIRouter()

@router.get("/healthcheck")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        # Check database connection
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
```

### Monitoring Stack

```yaml
# monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

## Performance Optimization

### Database Optimization

1. **Connection Pooling**
   ```python
   # app/adapters/orm/engine.py
   from sqlalchemy.ext.asyncio import create_async_engine
   
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True,
       pool_recycle=3600
   )
   ```

2. **Database Indexing**
   ```python
   # In your ORM models
   class UserORM(Base):
       __tablename__ = "users"
       
       email = Column(String, unique=True, index=True)  # Index for lookups
       username = Column(String, unique=True, index=True)  # Index for lookups
   ```

### Application Performance

1. **Async Everywhere**
   - Use async/await for all I/O operations
   - Use async database drivers (asyncpg)
   - Use async HTTP clients (httpx)

2. **Caching**
   ```python
   # Add Redis caching
   from redis.asyncio import Redis
   
   redis = Redis.from_url("redis://localhost:6379")
   
   async def get_cached_user(user_id: int) -> User | None:
       cached = await redis.get(f"user:{user_id}")
       if cached:
           return User.parse_raw(cached)
       return None
   ```

### Deployment Performance

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Deploying to production..."

# Build optimized Docker image
docker build -f Dockerfile.prod -t realworld-api:latest .

# Run database migrations
poetry run alembic upgrade head

# Deploy with zero downtime
docker-compose -f docker-compose.prod.yml up -d --remove-orphans

# Health check
sleep 10
curl -f http://localhost:8000/healthcheck || exit 1

echo "✅ Deployment successful!"
```

## Backup and Recovery

### Database Backup Script

```bash
#!/bin/bash
# backup.sh

DB_NAME="realworld_prod"
DB_USER="your_user"
DB_HOST="your_host"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "✅ Backup completed: backup_$DATE.sql.gz"
```

This deployment guide provides a comprehensive approach to production deployment with security, monitoring, and performance considerations.
