"""
Integration tests for citydb-3dtiler database connections
Tests that require actual database connection
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.pg_connection import (
    pg_establish, pg_create_session, pg_check_session,
    get_query_results, run_sql
)


class MockArgs:
    """Mock args object for database functions"""
    def __init__(self, host="localhost", port=5432, dbname="citydb_test",
                 user="testuser", password="testpass", schema="citydb"):
        self.db_host = host
        self.db_port = port
        self.db_name = dbname
        self.db_username = user
        self.db_password = password
        self.db_schema = schema


@pytest.mark.integration
@pytest.mark.postgres
class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_connection_establish(self, db_connection):
        """Test database connection can be established"""
        assert db_connection.conn is not None
        assert db_connection.conn.autocommit is True
    
    def test_postgres_version(self, db_connection):
        """Test can retrieve PostgreSQL version"""
        version = db_connection.get_postgres_version()
        assert version is not None
        assert "PostgreSQL" in version
    
    def test_postgis_version(self, db_connection):
        """Test can retrieve PostGIS version"""
        version = db_connection.get_postgis_version()
        assert version is not None
        assert "PostGIS" in version
    
    def test_connection_status(self, db_connection):
        """Test connection status check"""
        status = db_connection.cur.connection.status
        # psycopg2.extensions.STATUS_READY = 1
        assert status in [0, 1, 2]  # Various valid states


@pytest.mark.integration
@pytest.mark.postgres
class TestDatabaseOperations:
    """Test database operations"""
    
    def test_schema_exists(self, db_connection):
        """Test citydb schema exists"""
        db_connection.execute("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'citydb'
        """)
        result = db_connection.fetchone()
        assert result is not None
        assert result[0] == "citydb"
    
    def test_tables_exist(self, db_connection):
        """Test required tables exist"""
        required_tables = ["cityobject", "building", "surface_geometry"]
        
        for table in required_tables:
            db_connection.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'citydb' AND table_name = %s
            """, (table,))
            result = db_connection.fetchone()
            assert result is not None, f"Table {table} not found"
    
    def test_test_data_exists(self, db_connection):
        """Test test data was inserted"""
        db_connection.execute("SELECT COUNT(*) FROM citydb.cityobject")
        count = db_connection.fetchone()[0]
        assert count >= 3, "Expected at least 3 test cityobjects"
    
    def test_building_count(self, db_connection):
        """Test building count"""
        db_connection.execute("SELECT COUNT(*) FROM citydb.building")
        count = db_connection.fetchone()[0]
        assert count >= 3, "Expected at least 3 test buildings"


@pytest.mark.integration
@pytest.mark.postgres
class TestQueryExecution:
    """Test query execution functions"""
    
    def test_run_sql_insert(self, db_connection, empty_db):
        """Test SQL insert operation"""
        query = """
            INSERT INTO citydb.cityobject (gmlid, class, name)
            VALUES ('TEST_001', 'TestObject', 'Test Object')
        """
        run_sql(db_connection, query, "test_insert")
        
        # Verify insert
        db_connection.execute(
            "SELECT COUNT(*) FROM citydb.cityobject WHERE gmlid = 'TEST_001'"
        )
        count = db_connection.fetchone()[0]
        assert count == 1
    
    def test_run_sql_select(self, db_connection):
        """Test SQL select operation"""
        query = "SELECT COUNT(*) FROM citydb.building"
        db_connection.execute(query)
        result = db_connection.fetchone()
        assert result is not None
        assert result[0] >= 0
    
    def test_run_sql_update(self, db_connection, test_data):
        """Test SQL update operation"""
        building_id = test_data["building_id"]
        
        query = f"""
            UPDATE citydb.building 
            SET function = 'UpdatedFunction'
            WHERE id = {building_id}
        """
        run_sql(db_connection, query, "test_update")
        
        # Verify update
        db_connection.execute(
            f"SELECT function FROM citydb.building WHERE id = {building_id}"
        )
        result = db_connection.fetchone()
        assert result[0] == "UpdatedFunction"
    
    def test_run_sql_delete(self, db_connection):
        """Test SQL delete operation"""
        # Insert test record
        db_connection.execute("""
            INSERT INTO citydb.cityobject (gmlid, class)
            VALUES ('DELETE_TEST', 'Test')
            RETURNING id
        """)
        test_id = db_connection.fetchone()[0]
        
        # Delete
        query = f"DELETE FROM citydb.cityobject WHERE id = {test_id}"
        run_sql(db_connection, query, "test_delete")
        
        # Verify delete
        db_connection.execute(
            "SELECT COUNT(*) FROM citydb.cityobject WHERE gmlid = 'DELETE_TEST'"
        )
        count = db_connection.fetchone()[0]
        assert count == 0


@pytest.mark.integration
@pytest.mark.slow
class TestMultiVersionPostgreSQL:
    """Test across multiple PostgreSQL versions"""
    
    def test_version_specific_connection(self, version_specific_db):
        """Test connection to version-specific database"""
        assert version_specific_db.conn is not None
        
        version = version_specific_db.get_postgres_version()
        assert "PostgreSQL" in version
    
    def test_version_specific_schema(self, version_specific_db):
        """Test schema exists in version-specific database"""
        version_specific_db.execute("""
            SELECT schema_name FROM information_schema.schemata 
            WHERE schema_name = 'citydb'
        """)
        result = version_specific_db.fetchone()
        assert result is not None


@pytest.mark.integration
class TestTransactionHandling:
    """Test transaction handling"""
    
    def test_autocommit_enabled(self, db_connection):
        """Test autocommit is enabled"""
        assert db_connection.conn.autocommit is True
    
    def test_manual_transaction(self, db_connection, empty_db):
        """Test manual transaction control"""
        # Disable autocommit
        db_connection.conn.autocommit = False
        
        try:
            # Insert
            db_connection.execute("""
                INSERT INTO citydb.cityobject (gmlid, class)
                VALUES ('TX_TEST', 'Test')
            """)
            
            # Rollback
            db_connection.conn.rollback()
            
            # Verify rollback
            db_connection.execute(
                "SELECT COUNT(*) FROM citydb.cityobject WHERE gmlid = 'TX_TEST'"
            )
            count = db_connection.fetchone()[0]
            assert count == 0
            
        finally:
            # Re-enable autocommit
            db_connection.conn.autocommit = True
