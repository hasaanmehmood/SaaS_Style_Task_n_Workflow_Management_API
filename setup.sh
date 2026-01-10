#!/bin/bash

# Robust Setup Script for Task Management API
# Handles common Docker and database issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1

    print_info "Waiting for $service to be healthy..."

    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps $service | grep -q "Up (healthy)"; then
            print_success "$service is healthy!"
            return 0
        fi

        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "$service failed to become healthy after $max_attempts attempts"
    return 1
}

# Main script
clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║     Task Management API - Robust Setup Script          ║"
echo "║                                                         ║"
echo "║     This script will:                                   ║"
echo "║     1. Check prerequisites                              ║"
echo "║     2. Clean up any existing installations              ║"
echo "║     3. Setup environment                                ║"
echo "║     4. Build and start services                         ║"
echo "║     5. Run migrations and setup                         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check prerequisites
print_step "Step 1: Checking Prerequisites"

check_command docker
print_success "Docker is installed"

check_command docker-compose
print_success "Docker Compose is installed"

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker daemon is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker daemon is running"

# Step 2: Cleanup
print_step "Step 2: Cleaning Up Previous Installations"

print_info "Stopping existing containers..."
docker-compose down -v 2>/dev/null || true
print_success "Stopped existing containers"

# Optional: Clean Docker system (commented out for safety)
# read -p "Do you want to clean Docker system (removes unused data)? [y/N]: " -n 1 -r
# echo
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#     docker system prune -f
#     print_success "Docker system cleaned"
# fi

# Step 3: Environment Setup
print_step "Step 3: Setting Up Environment"

if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
    print_warning "Please review .env file and update credentials if needed!"

    read -p "Do you want to edit .env now? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    print_success ".env file already exists"
fi

# Verify wait_for_db.py exists
if [ ! -f wait_for_db.py ]; then
    print_warning "wait_for_db.py not found. Creating it..."
    cat > wait_for_db.py << 'EOF'
#!/usr/bin/env python
import os
import sys
import time
import MySQLdb
from decouple import config

def wait_for_db():
    db_host = config('DB_HOST', default='mysql')
    db_port = config('DB_PORT', default='3306', cast=int)
    db_name = config('DB_NAME', default='taskdb')
    db_user = config('DB_USER', default='taskuser')
    db_password = config('DB_PASSWORD', default='taskpass123')

    max_retries = 30
    retry_interval = 2

    print(f"Waiting for MySQL at {db_host}:{db_port}...")

    for attempt in range(max_retries):
        try:
            connection = MySQLdb.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                passwd=db_password,
                db=db_name
            )
            connection.close()
            print("✅ MySQL is ready!")
            return True
        except MySQLdb.Error as e:
            print(f"Attempt {attempt + 1}/{max_retries}: MySQL not ready - {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("❌ Failed to connect to MySQL")
                sys.exit(1)

    return False

if __name__ == '__main__':
    wait_for_db()
EOF
    chmod +x wait_for_db.py
    print_success "Created wait_for_db.py"
fi

# Step 4: Build and Start Services
print_step "Step 4: Building and Starting Services"

print_info "Building Docker images (this may take a few minutes)..."
if docker-compose build --no-cache; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

print_info "Starting services..."
if docker-compose up -d; then
    print_success "Services started"
else
    print_error "Failed to start services"
    exit 1
fi

# Step 5: Wait for Services
print_step "Step 5: Waiting for Services to be Ready"

print_info "This may take 30-60 seconds..."

# Wait for MySQL
if wait_for_service mysql; then
    sleep 5  # Extra wait for MySQL to be fully ready
else
    print_error "MySQL failed to start properly"
    print_info "Checking MySQL logs:"
    docker-compose logs --tail=20 mysql
    exit 1
fi

# Wait for Redis
if wait_for_service redis; then
    sleep 2
else
    print_error "Redis failed to start properly"
    print_info "Checking Redis logs:"
    docker-compose logs --tail=20 redis
    exit 1
fi

# Step 6: Database Setup
print_step "Step 6: Setting Up Database"

print_info "Running database migrations..."
if docker-compose exec -T api python manage.py migrate --noinput; then
    print_success "Migrations completed successfully"
else
    print_error "Migration failed"
    print_info "Checking API logs:"
    docker-compose logs --tail=30 api
    exit 1
fi

# Step 7: Collect Static Files
print_step "Step 7: Collecting Static Files"

if docker-compose exec -T api python manage.py collectstatic --noinput; then
    print_success "Static files collected"
else
    print_warning "Failed to collect static files (non-critical)"
fi

# Step 8: Create Superuser
print_step "Step 8: Creating Superuser Account"

echo -e "${YELLOW}You will now create an admin account.${NC}"
echo -e "${YELLOW}This account will have full access to the system.${NC}\n"

if docker-compose exec api python manage.py createsuperuser; then
    print_success "Superuser created successfully"
else
    print_warning "Superuser creation skipped or failed"
    print_info "You can create one later with: docker-compose exec api python manage.py createsuperuser"
fi

# Step 9: Verify Installation
print_step "Step 9: Verifying Installation"

print_info "Checking service status..."
docker-compose ps

print_info "\nTesting health check endpoint..."
sleep 5

if curl -f http://localhost:8000/api/health/ 2>/dev/null; then
    print_success "API is responding correctly!"
else
    print_warning "API health check failed. The service may still be starting up."
    print_info "Wait 30 seconds and try: curl http://localhost:8000/api/health/"
fi

# Final Summary
print_step "✨ Setup Complete!"

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             Setup Completed Successfully!              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Your API is now running at:${NC}"
echo -e "   ${GREEN}API Base URL:${NC}      http://localhost:8000/api/v1/"
echo -e "   ${GREEN}Admin Panel:${NC}       http://localhost:8000/admin/"
echo -e "   ${GREEN}Swagger Docs:${NC}      http://localhost:8000/api/docs/"
echo -e "   ${GREEN}ReDoc:${NC}             http://localhost:8000/api/redoc/"
echo -e "   ${GREEN}Health Check:${NC}      http://localhost:8000/api/health/"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo -e "   ${YELLOW}View logs:${NC}         docker-compose logs -f api"
echo -e "   ${YELLOW}Stop services:${NC}     docker-compose down"
echo -e "   ${YELLOW}Restart API:${NC}       docker-compose restart api"
echo -e "   ${YELLOW}Run tests:${NC}         docker-compose exec api pytest"
echo -e "   ${YELLOW}Shell access:${NC}      docker-compose exec api bash"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "   ${YELLOW}README:${NC}            cat README.md"
echo -e "   ${YELLOW}API Docs:${NC}          cat API_DOCUMENTATION.md"
echo -e "   ${YELLOW}Troubleshoot:${NC}      cat TROUBLESHOOTING.md"
echo ""
echo -e "${GREEN}🎉 Happy coding!${NC}"
echo ""

# Optional: Open browser
read -p "Do you want to open the API documentation in your browser? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8000/api/docs/
    elif command -v open &> /dev/null; then
        open http://localhost:8000/api/docs/
    else
        print_info "Please open http://localhost:8000/api/docs/ in your browser"
    fi
fi