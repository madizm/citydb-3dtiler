"""
Pytest configuration and shared fixtures for citydb-3dtiler tests
"""
import pytest
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Import fixtures
from tests.fixtures import (
    DatabaseConnection,
    POSTGRES_CONFIGS,
    db_config,
    db_connection,
    db_cursor,
    postgres_version,
    version_specific_db,
    test_data,
    empty_db
)

# Register markers
def pytest_configure(config):
    config.addinivalue_line("markers", "integration: Integration tests requiring database")
    config.addinivalue_line("markers", "unit: Unit tests without database")
    config.addinivalue_line("markers", "postgres: Tests for PostgreSQL connection")
    config.addinivalue_line("markers", "slow: Slow running tests")
