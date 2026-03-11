# citydb-3dtiler Test Framework

Comprehensive test framework for testing citydb-3dtiler across multiple PostgreSQL versions.

## Features

- ✅ **Multi-Version Testing**: Test against PostgreSQL 13, 14, 15, and 16
- ✅ **PostGIS Support**: Each version includes appropriate PostGIS extension
- ✅ **Docker-Based**: Isolated test environments using Docker Compose
- ✅ **CI/CD Ready**: GitHub Actions workflow for automated testing
- ✅ **Coverage Reports**: HTML and XML coverage reports
- ✅ **Parametrized Tests**: Run same tests across all PostgreSQL versions

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- pytest and test dependencies

### Install Test Dependencies

```bash
cd citydb-3dtiler
pip install -r tests/requirements.txt
```

### Run Tests

#### Unit Tests Only (No Database Required)

```bash
./run_tests.sh --unit
# or
pytest -v -m unit tests/
```

#### Integration Tests (Single PostgreSQL Version)

```bash
# Start PostgreSQL 15
docker-compose -f docker-compose.test.yml up -d postgres-15

# Run tests
export TEST_DB_PORT=5434
pytest -v -m integration tests/

# Stop container
docker-compose -f docker-compose.test.yml down
```

#### Test All PostgreSQL Versions

```bash
./run_tests.sh --all
```

#### Test Specific PostgreSQL Version

```bash
./run_tests.sh --version 15
```

#### With Coverage Report

```bash
./run_tests.sh --unit --coverage
./run_tests.sh --integration --coverage
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── requirements.txt         # Test dependencies
├── fixtures/
│   ├── __init__.py         # Database connection fixtures
│   └── init-db/
│       └── 01-init-schema.sql  # Database initialization script
├── unit/
│   └── test_database.py    # Unit tests (no database)
└── integration/
    └── test_database.py    # Integration tests (requires database)
```

## Docker Compose Configuration

Each PostgreSQL version runs on a different port:

| Version | PostGIS | Container Name | Port |
|---------|---------|----------------|------|
| 13 | 3.1 | citydb-test-pg13 | 5432 |
| 14 | 3.2 | citydb-test-pg14 | 5433 |
| 15 | 3.3 | citydb-test-pg15 | 5434 |
| 16 | 3.4 | citydb-test-pg16 | 5435 |

### Start Specific Version

```bash
docker-compose -f docker-compose.test.yml up -d postgres-15
```

### Start Multiple Versions

```bash
docker-compose -f docker-compose.test.yml --profile pg15 --profile pg16 up -d
```

### Check Container Status

```bash
docker-compose -f docker-compose.test.yml ps
```

### View Logs

```bash
docker-compose -f docker-compose.test.yml logs -f postgres-15
```

## Environment Variables

Configure test database connection:

```bash
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5434
export TEST_DB_NAME=citydb_test
export TEST_DB_USER=testuser
export TEST_DB_PASSWORD=testpass
```

## Pytest Markers

Use markers to filter tests:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run PostgreSQL-specific tests
pytest -m postgres

# Run slow tests
pytest -m slow

# Combine markers
pytest -m "integration and postgres"
```

## Fixtures

### `db_connection`
Session-scoped database connection fixture.

```python
def test_query(db_connection):
    db_connection.execute("SELECT COUNT(*) FROM citydb.building")
    count = db_connection.fetchone()[0]
    assert count > 0
```

### `db_cursor`
Function-scoped database cursor.

```python
def test_cursor(db_cursor):
    db_cursor.execute("SELECT version()")
    version = db_cursor.fetchone()[0]
    assert "PostgreSQL" in version
```

### `postgres_version`
Parametrized fixture for testing across versions.

```python
def test_version(postgres_version):
    # Runs 4 times: 13, 14, 15, 16
    assert postgres_version in ["13", "14", "15", "16"]
```

### `version_specific_db`
Database connection for specific PostgreSQL version.

```python
def test_pg16(version_specific_db):
    # Connects to PostgreSQL 16 on port 5435
    version = version_specific_db.get_postgres_version()
    assert "PostgreSQL 16" in version
```

### `test_data`
Inserts test data and cleans up after test.

```python
def test_building(test_data):
    building_id = test_data["building_id"]
    # Test with building_id, auto-cleanup after test
```

### `empty_db`
Truncates all tables for clean test state.

```python
def test_insert(empty_db):
    # All tables are empty, safe to insert test data
```

## GitHub Actions CI

The test workflow automatically runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

### Workflow Jobs

1. **unit-tests**: Run unit tests (no database)
2. **integration-tests**: Matrix build for PostgreSQL 13-16
3. **coverage-report**: Aggregate coverage reports
4. **docker-build**: Test Docker image build

### View CI Results

Check the "Actions" tab in GitHub repository for test results.

## Coverage Reports

Generate HTML coverage report:

```bash
./run_tests.sh --coverage
```

Open in browser:

```bash
# Linux
xdg-open coverage_report/index.html

# macOS
open coverage_report/index.html
```

## Troubleshooting

### Database Connection Failed

```bash
# Check if container is running
docker ps | grep citydb-test

# Check container logs
docker logs citydb-test-pg15

# Verify health status
docker inspect --format='{{.State.Health.Status}}' citydb-test-pg15
```

### Port Already in Use

Change port in `docker-compose.test.yml`:

```yaml
ports:
  - "54340:5432"  # Use 54340 instead of 5434
```

### Test Fixtures Not Found

Ensure project root is in Python path:

```bash
export PYTHONPATH=$(pwd):$PYTHONPATH
pytest tests/
```

### Slow Tests

Skip slow tests:

```bash
pytest -m "not slow" tests/
```

## Adding New Tests

### Unit Test Example

```python
# tests/unit/test_my_feature.py
import pytest

class TestMyFeature:
    def test_something(self):
        assert True
```

### Integration Test Example

```python
# tests/integration/test_my_feature.py
import pytest

@pytest.mark.integration
class TestMyFeature:
    def test_database_operation(self, db_connection):
        db_connection.execute("SELECT 1")
        result = db_connection.fetchone()
        assert result[0] == 1
```

## Best Practices

1. **Use fixtures**: Don't create connections manually
2. **Mark tests**: Use `@pytest.mark.integration` for database tests
3. **Clean up**: Use `empty_db` or `test_data` fixtures for cleanup
4. **Parametrize**: Test across all PostgreSQL versions when possible
5. **Isolation**: Each test should be independent

## License

Same as citydb-3dtiler project license.
