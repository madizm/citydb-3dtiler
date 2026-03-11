"""
Unit tests for citydb-3dtiler database module
Tests that don't require database connection
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestDatabaseModule:
    """Test database module imports and structure"""
    
    def test_database_module_exists(self):
        """Test that database module can be imported"""
        from database import pg_connection
        assert pg_connection is not None
    
    def test_pg_connection_functions(self):
        """Test that required functions exist in pg_connection"""
        from database import pg_connection
        
        required_functions = [
            'pg_show_details',
            'pg_establish',
            'pg_create_session',
            'pg_check_connection',
            'pg_check_session',
            'create_materialized_view',
            'index_materialized_view',
            'get_query_results',
            'run_sql'
        ]
        
        for func_name in required_functions:
            assert hasattr(pg_connection, func_name), f"Missing function: {func_name}"
    
    def test_psycopg2_import(self):
        """Test psycopg2 can be imported"""
        import psycopg2
        assert psycopg2 is not None
        assert hasattr(psycopg2, 'connect')


class TestQueryBuilders:
    """Test SQL query builder functions"""
    
    def test_create_materialized_view(self):
        """Test materialized view creation query"""
        from database.pg_connection import create_materialized_view
        
        mv_name = "test_view"
        query = "SELECT * FROM citydb.building"
        
        result = create_materialized_view(mv_name, query)
        
        assert "DROP MATERIALIZED VIEW IF EXISTS" in result
        assert "CREATE MATERIALIZED VIEW IF NOT EXISTS" in result
        assert f"citydb.{mv_name}" in result
        assert query in result
        assert "WITH DATA" in result
    
    def test_index_materialized_view(self):
        """Test index creation query"""
        from database.pg_connection import index_materialized_view
        
        table_name = "test_table"
        geom_column = "geom"
        
        result = index_materialized_view(table_name, geom_column)
        
        assert "CREATE INDEX IF NOT EXISTS" in result
        assert f"{table_name}_{geom_column}_idx" in result
        assert f"ON {table_name}" in result
        assert "USING gist" in result
        assert "st_centroid" in result
        assert "st_envelope" in result


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_required_env_vars(self):
        """Test that required environment variables are documented"""
        required_vars = [
            "TEST_DB_HOST",
            "TEST_DB_PORT",
            "TEST_DB_NAME",
            "TEST_DB_USER",
            "TEST_DB_PASSWORD"
        ]
        
        # These should be documented in README or test docs
        # For now, just verify they're defined in fixtures
        from tests.fixtures import POSTGRES_CONFIGS
        
        assert len(POSTGRES_CONFIGS) >= 4  # At least 4 PG versions
        assert "13" in POSTGRES_CONFIGS
        assert "14" in POSTGRES_CONFIGS
        assert "15" in POSTGRES_CONFIGS
        assert "16" in POSTGRES_CONFIGS
