#!/bin/bash

# Diagnostic Script for Task Management API
# Helps identify and troubleshoot issues

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

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

check_status() {
    if [ $? -eq 0 ]; then
        print_success "$1"
        return 0
    else
        print_error "$2"
        return 1
    fi
}

clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║        Task Management API - Diagnostic Tool           ║"
echo "╚════════════════════════════════════════════════════════╝"

# 1. Check Docker
print_header "1. Checking Docker Environment"

docker --version > /dev/null 2>&1
check_status "Docker is installed" "Docker is not installed"

docker-compose --version > /dev/null 2>&1
check_status "Docker Compose is installed" "Docker Compose is not installed"

docker info > /dev/null 2>&1
check_status "Docker daemon is running" "Docker daemon is not running"

# 2. Check Files
print_header "2. Checking Required Files"

if [ -f .env ]; then
    print_success ".env file exists"
else
    print_error ".env file missing"
    print_info "Run: cp .env.example .env"
fi

if [ -f docker-compose.yml ]; then
    print_success "docker-compose.yml exists"
else
    print_error "docker-compose.yml missing"
fi

if [ -f wait_for_db.py ]; then
    print_success "wait_for_db.py exists"
else
    print_error "wait_for_db.py missing (this is critical!)"
fi

if [ -f manage.py ]; then
    print_success "manage.py exists"
else
    print_error "manage.py missing"
fi

# 3. Check Container Status
print_header "3. Checking Container Status"

echo "Container Status:"
docker-compose ps

echo -e "\n${YELLOW}Service Health Check:${NC}"

# Check MySQL
if docker-compose ps mysql | grep -q "Up"; then
    if docker-compose ps mysql | grep -q "healthy"; then
        print_success "MySQL is Up and Healthy"
    else
        print_warning "MySQL is Up but not Healthy yet"
    fi
else
    print_error "MySQL is not running"
fi

# Check Redis
if docker-compose ps redis | grep -q "Up"; then
    if docker-compose ps redis | grep -q "healthy"; then
        print_success "Redis is Up and Healthy"
    else
        print_warning "Redis is Up but not Healthy yet"
    fi
else
    print_error "Redis is not running"
fi

# Check API
if docker-compose ps api | grep -q "Up"; then
    print_success "API container is Up"

    # Check if it's restarting
    restart_count=$(docker inspect taskapi_api --format='{{.RestartCount}}' 2>/dev/null || echo "unknown")
    if [ "$restart_count" != "0" ] && [ "$restart_count" != "unknown" ]; then
        print_warning "API has restarted $restart_count times"
    fi
else
    print_error "API container is not running"
fi

# Check Celery
if docker-compose ps celery | grep -q "Up"; then
    print_success "Celery worker is Up"
else
    print_error "Celery worker is not running"
fi

# 4. Check Network Connectivity
print_header "4. Checking Network Connectivity"

# Test MySQL connection from API
if docker-compose exec -T api python wait_for_db.py > /dev/null 2>&1; then
    print_success "API can connect to MySQL"
else
    print_error "API cannot connect to MySQL"
fi

# Test Redis connection
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is responding"
else
    print_error "Redis is not responding"
fi

# 5. Check API Health
print_header "5. Checking API Health"

sleep 2  # Give API a moment to respond

if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    print_success "API health check passed"
    echo "Health status:"
    curl -s http://localhost:8000/api/health/ | python -m json.tool 2>/dev/null || echo "Could not parse JSON"
else
    print_error "API health check failed"
fi

# Check if API docs are accessible
if curl -f http://localhost:8000/api/docs/ > /dev/null 2>&1; then
    print_success "API documentation is accessible"
else
    print_error "API documentation is not accessible"
fi

# 6. Check Database
print_header "6. Checking Database"

# Check if database exists
if docker-compose exec -T mysql mysql -u taskuser -p${DB_PASSWORD:-taskpass123} -e "SHOW DATABASES LIKE 'taskdb';" 2>/dev/null | grep -q "taskdb"; then
    print_success "Database 'taskdb' exists"

    # Check for tables
    table_count=$(docker-compose exec -T mysql mysql -u taskuser -p${DB_PASSWORD:-taskpass123} taskdb -e "SHOW TABLES;" 2>/dev/null | wc -l)
    if [ "$table_count" -gt 1 ]; then
        print_success "Database has $((table_count - 1)) tables"
    else
        print_warning "Database has no tables (migrations may not have run)"
    fi
else
    print_error "Database 'taskdb' does not exist"
fi

# 7. Check Logs for Errors
print_header "7. Recent Log Analysis"

echo -e "${YELLOW}Checking for errors in API logs:${NC}"
error_count=$(docker-compose logs api --tail=100 | grep -i "error" | wc -l)
if [ "$error_count" -gt 0 ]; then
    print_warning "Found $error_count error messages in recent logs"
    echo "Recent errors:"
    docker-compose logs api --tail=50 | grep -i "error" | tail -5
else
    print_success "No recent errors in API logs"
fi

echo -e "\n${YELLOW}Checking for exceptions in API logs:${NC}"
exception_count=$(docker-compose logs api --tail=100 | grep -i "exception" | wc -l)
if [ "$exception_count" -gt 0 ]; then
    print_warning "Found $exception_count exception messages in recent logs"
    echo "Recent exceptions:"
    docker-compose logs api --tail=50 | grep -i "exception" | tail -5
else
    print_success "No recent exceptions in API logs"
fi

# 8. Check Ports
print_header "8. Checking Port Availability"

check_port() {
    local port=$1
    local service=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        print_success "Port $port is in use (by $service)"
    else
        print_error "Port $port is not in use (expected for $service)"
    fi
}

check_port 8000 "API"
check_port 3306 "MySQL"
check_port 6379 "Redis"

# 9. Check Disk Space
print_header "9. Checking System Resources"

# Docker disk usage
echo -e "${YELLOW}Docker Disk Usage:${NC}"
docker system df

# Check available memory
echo -e "\n${YELLOW}Available Memory:${NC}"
free -h 2>/dev/null || echo "Memory info not available (non-Linux system)"

# 10. Summary and Recommendations
print_header "10. Summary and Recommendations"

# Count issues
issue_count=0

# Check critical services
if ! docker-compose ps mysql | grep -q "Up.*healthy"; then
    issue_count=$((issue_count + 1))
fi

if ! docker-compose ps api | grep -q "Up"; then
    issue_count=$((issue_count + 1))
fi

if ! curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
    issue_count=$((issue_count + 1))
fi

if [ $issue_count -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              🎉 System is Healthy! 🎉                  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_success "All critical services are running correctly"
else
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║           ⚠️  Issues Detected: $issue_count                     ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_error "Found $issue_count critical issue(s)"
    echo ""
    echo -e "${YELLOW}Recommended Actions:${NC}"

    if ! docker-compose ps mysql | grep -q "Up.*healthy"; then
        echo "  1. MySQL is not healthy:"
        echo "     - Wait 30-60 seconds and run this script again"
        echo "     - Check logs: docker-compose logs mysql"
        echo "     - Try: docker-compose restart mysql"
    fi

    if ! docker-compose ps api | grep -q "Up"; then
        echo "  2. API container is not running:"
        echo "     - Check logs: docker-compose logs api"
        echo "     - Check if wait_for_db.py exists"
        echo "     - Try: docker-compose up -d api"
    fi

    if ! curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
        echo "  3. API health check failed:"
        echo "     - Wait 30 seconds and try again"
        echo "     - Run migrations: docker-compose exec api python manage.py migrate"
        echo "     - Check logs: docker-compose logs api --tail=50"
    fi
fi

echo ""
echo -e "${BLUE}For detailed troubleshooting, see TROUBLESHOOTING.md${NC}"
echo -e "${BLUE}To reset everything: docker-compose down -v && ./setup.sh${NC}"
echo ""