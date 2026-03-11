#!/bin/bash
# Test runner script for citydb-3dtiler
# Usage: ./run_tests.sh [OPTIONS]
#
# Options:
#   --version VERSION   Test specific PostgreSQL version (13|14|15|16)
#   --all               Test all PostgreSQL versions
#   --unit              Run only unit tests
#   --integration       Run only integration tests
#   --coverage          Generate coverage report
#   --help              Show this help message

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PG_VERSION=""
RUN_ALL=false
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_COVERAGE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            PG_VERSION="$2"
            shift 2
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        --unit)
            RUN_UNIT=true
            shift
            ;;
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --coverage)
            RUN_COVERAGE=true
            shift
            ;;
        --help)
            head -15 "$0" | tail -13
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# If no options specified, run unit tests
if ! $RUN_ALL && [ -z "$PG_VERSION" ] && ! $RUN_UNIT && ! $RUN_INTEGRATION; then
    RUN_UNIT=true
fi

# Function to start PostgreSQL container
start_postgres() {
    local version=$1
    echo -e "${YELLOW}Starting PostgreSQL $version...${NC}"
    docker-compose -f docker-compose.test.yml up -d postgres-$version
    echo -e "${YELLOW}Waiting for database to be ready...${NC}"
    sleep 10
    
    # Wait for healthcheck
    local max_attempts=30
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker inspect --format='{{.State.Health.Status}}' "citydb-test-pg$version" 2>/dev/null | grep -q "healthy"; then
            echo -e "${GREEN}PostgreSQL $version is ready${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}PostgreSQL $version failed to start${NC}"
    return 1
}

# Function to stop PostgreSQL container
stop_postgres() {
    local version=$1
    echo -e "${YELLOW}Stopping PostgreSQL $version...${NC}"
    docker-compose -f docker-compose.test.yml down -v
}

# Function to run tests
run_tests() {
    local version=$1
    local port=""
    
    case $version in
        13) port=5432 ;;
        14) port=5433 ;;
        15) port=5434 ;;
        16) port=5435 ;;
    esac
    
    export TEST_DB_HOST="localhost"
    export TEST_DB_PORT="$port"
    export TEST_DB_NAME="citydb_test"
    export TEST_DB_USER="testuser"
    export TEST_DB_PASSWORD="testpass"
    
    local pytest_args="-v"
    
    if $RUN_UNIT; then
        pytest_args="$pytest_args -m unit"
    elif $RUN_INTEGRATION; then
        pytest_args="$pytest_args -m integration"
    fi
    
    if $RUN_COVERAGE; then
        pytest_args="$pytest_args --cov --cov-report=html:coverage_report_pg$version"
    fi
    
    echo -e "${GREEN}Running tests for PostgreSQL $version on port $port${NC}"
    pytest $pytest_args tests/
}

# Run tests for specific version
if [ -n "$PG_VERSION" ]; then
    start_postgres "$PG_VERSION"
    run_tests "$PG_VERSION"
    stop_postgres "$PG_VERSION"
    exit 0
fi

# Run tests for all versions
if $RUN_ALL; then
    for version in 13 14 15 16; do
        echo -e "\n${GREEN}========================================${NC}"
        echo -e "${GREEN}Testing PostgreSQL $version${NC}"
        echo -e "${GREEN}========================================${NC}\n"
        
        start_postgres "$version"
        run_tests "$version"
        stop_postgres "$version"
    done
    exit 0
fi

# Run unit tests only (no database required)
if $RUN_UNIT; then
    echo -e "${GREEN}Running unit tests...${NC}"
    pytest -v -m unit tests/
    exit 0
fi

# Run integration tests only (requires database)
if $RUN_INTEGRATION; then
    echo -e "${YELLOW}Integration tests require a running database${NC}"
    echo -e "${YELLOW}Start with: docker-compose -f docker-compose.test.yml up -d postgres-15${NC}"
    export TEST_DB_PORT=5434
    pytest -v -m integration tests/
    exit 0
fi
