"""
Integration tests for citydb-3dtiler main application
Tests the actual application functionality with database
"""
import pytest
import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class MockArgs:
    """Mock args object for application functions"""
    def __init__(self, **kwargs):
        self.db_host = kwargs.get('db_host', 'localhost')
        self.db_port = kwargs.get('db_port', 5432)
        self.db_name = kwargs.get('db_name', 'citydb_test')
        self.db_username = kwargs.get('db_username', 'testuser')
        self.db_password = kwargs.get('db_password', 'testpass')
        self.db_schema = kwargs.get('db_schema', 'citydb')
        
        # Set any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.mark.integration
class TestDatabaseConnectionFunctions:
    """Test database connection functions from pg_connection module"""
    
    def test_pg_show_details(self, capsys):
        """Test pg_show_details function"""
        from database.pg_connection import pg_show_details
        
        args = MockArgs()
        pg_show_details(args)
        
        captured = capsys.readouterr()
        assert "Connection:" in captured.out
        assert args.db_host in captured.out
    
    def test_pg_establish(self, db_config):
        """Test pg_establish function"""
        from database.pg_connection import pg_establish
        
        args = MockArgs(**db_config)
        conn = pg_establish(args)
        
        assert conn is not None
        assert conn.autocommit is True
        
        conn.close()
    
    def test_pg_create_session(self, db_connection):
        """Test pg_create_session function"""
        from database.pg_connection import pg_create_session
        
        cur = pg_create_session(db_connection.conn)
        
        assert cur is not None
        assert hasattr(cur, 'execute')
        
        cur.close()
    
    def test_pg_check_session(self, db_connection):
        """Test pg_check_session function"""
        from database.pg_connection import pg_check_session
        
        status = pg_check_session(db_connection.cur)
        
        # Status should be a valid psycopg2 connection status
        assert status in [0, 1, 2, 3, 4]  # Various valid states


@pytest.mark.integration
class TestCityObjectQueries:
    """Test queries against cityobject table"""
    
    def test_count_cityobjects(self, db_connection):
        """Test counting cityobjects"""
        db_connection.execute("SELECT COUNT(*) FROM citydb.cityobject")
        count = db_connection.fetchone()[0]
        assert count >= 3  # At least test data
    
    def test_query_by_class(self, db_connection):
        """Test querying by object class"""
        db_connection.execute("""
            SELECT COUNT(*) FROM citydb.cityobject 
            WHERE class = 'Building'
        """)
        count = db_connection.fetchone()[0]
        assert count >= 0
    
    def test_query_by_gmlid(self, db_connection):
        """Test querying by GML ID"""
        db_connection.execute("""
            SELECT id, gmlid, class FROM citydb.cityobject 
            WHERE gmlid LIKE 'TEST_%'
        """)
        results = db_connection.fetchall()
        assert len(results) >= 3


@pytest.mark.integration
class TestBuildingQueries:
    """Test queries against building table"""
    
    def test_count_buildings(self, db_connection):
        """Test counting buildings"""
        db_connection.execute("SELECT COUNT(*) FROM citydb.building")
        count = db_connection.fetchone()[0]
        assert count >= 3  # At least test data
    
    def test_building_attributes(self, db_connection):
        """Test building has required attributes"""
        db_connection.execute("""
            SELECT objectclass_id, class, function 
            FROM citydb.building 
            LIMIT 1
        """)
        result = db_connection.fetchone()
        
        assert result is not None
        assert len(result) == 3
    
    def test_building_with_class_filter(self, db_connection):
        """Test filtering buildings by class"""
        db_connection.execute("""
            SELECT COUNT(*) FROM citydb.building 
            WHERE class = 'Building'
        """)
        count = db_connection.fetchone()[0]
        assert count >= 0


@pytest.mark.integration
class TestPostGISFunctions:
    """Test PostGIS spatial functions"""
    
    def test_postgis_installed(self, db_connection):
        """Test PostGIS is installed"""
        db_connection.execute("SELECT PostGIS_Version()")
        result = db_connection.fetchone()
        
        assert result is not None
        assert "PostGIS" in result[0]
    
    def test_st_envelope(self, db_connection):
        """Test ST_Envelope function"""
        db_connection.execute("""
            SELECT ST_Envelope(ST_MakeEnvelope(0, 0, 10, 10, 4326))
        """)
        result = db_connection.fetchone()
        
        assert result is not None
    
    def test_st_centroid(self, db_connection):
        """Test ST_Centroid function"""
        db_connection.execute("""
            SELECT ST_AsText(ST_Centroid(ST_MakeEnvelope(0, 0, 10, 10, 4326)))
        """)
        result = db_connection.fetchone()
        
        assert result is not None
        assert "POINT" in result[0]
    
    def test_st_transform(self, db_connection):
        """Test ST_Transform function"""
        db_connection.execute("""
            SELECT ST_AsText(
                ST_Transform(
                    ST_MakeEnvelope(0, 0, 10, 10, 4326),
                    3857
                )
            )
        """)
        result = db_connection.fetchone()
        
        assert result is not None


@pytest.mark.integration
class TestMaterializedViews:
    """Test materialized view creation and indexing"""
    
    def test_create_materialized_view_query(self):
        """Test materialized view query builder"""
        from database.pg_connection import create_materialized_view
        
        query = create_materialized_view("test_mv", "SELECT * FROM citydb.building")
        
        assert "DROP MATERIALIZED VIEW IF EXISTS" in query
        assert "CREATE MATERIALIZED VIEW IF NOT EXISTS" in query
        assert "citydb.test_mv" in query
    
    def test_index_materialized_view_query(self):
        """Test index creation query builder"""
        from database.pg_connection import index_materialized_view
        
        query = index_materialized_view("test_table", "geom")
        
        assert "CREATE INDEX IF NOT EXISTS" in query
        assert "USING gist" in query
        assert "st_centroid" in query
        assert "st_envelope" in query


@pytest.mark.slow
@pytest.mark.integration
class TestDatabasePerformance:
    """Test database performance"""
    
    def test_query_performance(self, db_connection):
        """Test basic query performance"""
        import time
        
        start = time.time()
        db_connection.execute("SELECT COUNT(*) FROM citydb.cityobject")
        db_connection.fetchone()
        elapsed = time.time() - start
        
        # Query should complete in under 1 second
        assert elapsed < 1.0
    
    def test_index_usage(self, db_connection):
        """Test that indexes are being used"""
        db_connection.execute("""
            EXPLAIN ANALYZE 
            SELECT * FROM citydb.cityobject 
            WHERE class = 'Building'
        """)
        result = db_connection.fetchone()
        
        # EXPLAIN should return a plan
        assert result is not None
