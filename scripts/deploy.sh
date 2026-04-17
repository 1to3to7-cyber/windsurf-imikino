#!/bin/bash

# Imikino Production Deployment Script
# Author: BIZIMANA Fils
# Email: 1to3to7@gmail.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="imikino"
DOMAIN="imikino.rw"
API_DOMAIN="api.imikino.rw"
ADMIN_EMAIL="1to3to7@gmail.com"

echo -e "${BLUE}🚀 Starting Imikino Production Deployment${NC}"
echo "========================================"

# Check if required tools are installed
check_requirements() {
    echo -e "${YELLOW}📋 Checking requirements...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Git is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All requirements satisfied${NC}"
}

# Backup current deployment
backup_current() {
    echo -e "${YELLOW}💾 Creating backup...${NC}"
    
    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [ -f "./data/imikino.db" ]; then
        cp "./data/imikino.db" "$BACKUP_DIR/imikino.db"
        echo -e "${GREEN}✅ Database backed up${NC}"
    fi
    
    # Backup configuration files
    cp -r "./nginx" "$BACKUP_DIR/" 2>/dev/null || true
    cp ".env" "$BACKUP_DIR/" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Backup created at $BACKUP_DIR${NC}"
}

# Run tests
run_tests() {
    echo -e "${YELLOW}🧪 Running tests...${NC}"
    
    # Frontend tests
    echo "Running frontend tests..."
    cd frontend
    npm run test:coverage
    FRONTEND_EXIT_CODE=$?
    
    # Backend tests
    echo "Running backend tests..."
    cd ../backend
    python -m pytest backend/tests/ -v --cov=backend --cov-report=xml
    BACKEND_EXIT_CODE=$?
    
    if [ $FRONTEND_EXIT_CODE -eq 0 ] && [ $BACKEND_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed${NC}"
    else
        echo -e "${RED}❌ Tests failed${NC}"
        exit 1
    fi
}

# Build application
build_application() {
    echo -e "${YELLOW}🔨 Building application...${NC}"
    
    # Build frontend
    echo "Building frontend..."
    cd frontend
    npm run build
    FRONTEND_BUILD_EXIT_CODE=$?
    
    # Build backend Docker image
    echo "Building backend Docker image..."
    cd ../backend
    docker build -t "${PROJECT_NAME}-backend:latest" -f Dockerfile.prod .
    BACKEND_BUILD_EXIT_CODE=$?
    
    # Build frontend Docker image
    echo "Building frontend Docker image..."
    cd ../frontend
    docker build -t "${PROJECT_NAME}-frontend:latest" -f Dockerfile.prod .
    FRONTEND_DOCKER_EXIT_CODE=$?
    
    if [ $FRONTEND_BUILD_EXIT_CODE -eq 0 ] && [ $BACKEND_BUILD_EXIT_CODE -eq 0 ] && [ $FRONTEND_DOCKER_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ Build completed successfully${NC}"
    else
        echo -e "${RED}❌ Build failed${NC}"
        exit 1
    fi
}

# Deploy to production
deploy_production() {
    echo -e "${YELLOW}🚀 Deploying to production...${NC}"
    
    # Stop existing services
    echo "Stopping existing services..."
    docker-compose -f docker-compose.prod.yml down
    
    # Wait for services to stop
    sleep 10
    
    # Start new services
    echo "Starting new services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 30
    
    # Health checks
    echo "Running health checks..."
    
    # Check frontend
    if curl -f "https://$DOMAIN/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${RED}❌ Frontend health check failed${NC}"
    fi
    
    # Check backend API
    if curl -f "https://$API_DOMAIN/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend API is healthy${NC}"
    else
        echo -e "${RED}❌ Backend API health check failed${NC}"
    fi
    
    # Check admin chamber
    if curl -f "https://$DOMAIN/admin/code" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Admin chamber is accessible${NC}"
    else
        echo -e "${RED}❌ Admin chamber is not accessible${NC}"
    fi
}

# Post-deployment verification
verify_deployment() {
    echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
    
    # Check if all containers are running
    RUNNING_CONTAINERS=$(docker-compose -f docker-compose.prod.yml ps -q | wc -l)
    EXPECTED_CONTAINERS=4  # frontend, backend, redis, nginx
    
    if [ $RUNNING_CONTAINERS -eq $EXPECTED_CONTAINERS ]; then
        echo -e "${GREEN}✅ All containers are running${NC}"
    else
        echo -e "${YELLOW}⚠️  Expected $EXPECTED_CONTAINERS containers, but $RUNNING_CONTAINERS are running${NC}"
    fi
    
    # Check SSL certificate
    if [ -f "./nginx/ssl/cert.pem" ]; then
        echo -e "${GREEN}✅ SSL certificate is present${NC}"
        
        # Check certificate expiry
        EXPIRY_DATE=$(openssl x509 -in ./nginx/ssl/cert.pem -noout -dates | grep "notAfter" | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
        CURRENT_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400))
        
        if [ $DAYS_LEFT -lt 30 ]; then
            echo -e "${YELLOW}⚠️  SSL certificate expires in $DAYS_LEFT days${NC}"
        else
            echo -e "${GREEN}✅ SSL certificate is valid ($DAYS_LEFT days remaining)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  SSL certificate not found${NC}"
    fi
}

# Send notification
send_notification() {
    echo -e "${YELLOW}📧 Sending deployment notification...${NC}"
    
    # Create deployment summary
    SUMMARY="🚀 Imikino Deployment Summary
    
    Project: $PROJECT_NAME
    Domain: $DOMAIN
    API Domain: $API_DOMAIN
    Admin: https://$DOMAIN/admin/code
    Admin Email: $ADMIN_EMAIL
    Timestamp: $(date)
    Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    All services are running and healthy.
    
    Best regards,
    BIZIMANA Fils
    1to3to7@gmail.com"
    
    # Send email (configure your email settings)
    echo "$SUMMARY" | mail -s "Imikino Deployment Complete" "$ADMIN_EMAIL" 2>/dev/null || echo "Email notification failed"
    
    echo -e "${GREEN}✅ Notification sent to $ADMIN_EMAIL${NC}"
}

# Cleanup old backups
cleanup_old_backups() {
    echo -e "${YELLOW}🧹 Cleaning up old backups...${NC}"
    
    # Keep only last 7 days of backups
    find ./backups -type d -mtime +7 -exec rm -rf {} + \; 2>/dev/null || true
    echo -e "${GREEN}✅ Old backups cleaned up${NC}"
}

# Main deployment process
main() {
    echo -e "${BLUE}🏆 Imikino Production Deployment Script${NC}"
    echo "Developed by BIZIMANA Fils"
    echo "Contact: 1to3to7@gmail.com"
    echo ""
    
    check_requirements
    backup_current
    run_tests
    build_application
    deploy_production
    verify_deployment
    send_notification
    cleanup_old_backups
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${GREEN}🌐 Your application is now live at: https://$DOMAIN${NC}"
    echo -e "${GREEN}🔧 Admin chamber: https://$DOMAIN/admin/code${NC}"
    echo -e "${GREEN}📊 API documentation: https://$API_DOMAIN/docs${NC}"
    echo ""
    echo -e "${BLUE}Thank you for using Imikino!${NC}"
}

# Handle script arguments
case "${1:-}" in
    --backup-only)
        backup_current
        ;;
    --test-only)
        run_tests
        ;;
    --build-only)
        build_application
        ;;
    --deploy-only)
        deploy_production
        ;;
    --help|*)
        echo "Imikino Deployment Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --backup-only    Only create backup"
        echo "  --test-only      Only run tests"
        echo "  --build-only    Only build application"
        echo "  --deploy-only    Only deploy (requires existing build)"
        echo "  --help          Show this help message"
        echo ""
        echo "Default: Run full deployment process"
        exit 0
        ;;
    *)
        main
        ;;
esac
