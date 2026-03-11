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
class TestFeatureQueries:
    """Test queries against feature table (3DCityDB v5.x)"""
    
    def test_count_features(self, db_connection):
        """Test counting features"""
        db_connection.execute("SELECT COUNT(*) FROM citydb.feature")
        count = db_connection.fetchone()[0]
        assert count >= 4  # At least test data
    
    def test_query_by_class(self, db_connection):
        """Test querying by object class"""
        db_connection.execute("""
            SELECT COUNT(*) FROM citydb.feature 
            WHERE class = 'Building'
        """)
        count = db_connection.fetchone()[0]
        assert count >= 3
    
    def test_query_by_gmlid(self, db_connection):
        """Test querying by GML ID"""
        db_connection.execute("""
            SELECT id, gmlid, class FROM citydb.feature 
            WHERE gmlid LIKE 'TEST_%'
        """)
        results = db_connection.fetchall()
        assert len(results) >= 4
    
    def test_query_by_objectclass(self, db_connection):
        """Test querying by objectclass"""
        db_connection.execute("""
            SELECT f.id, f.gmlid, oc.classname 
            FROM citydb.feature f
            JOIN citydb.objectclass oc ON f.objectclass_id = oc.id
            WHERE oc.classname = 'Building'
        """)
        results = db_connection.fetchall()
        assert len(results) >= 3


@pytest.mark.integration
class TestObjectClassQueries:
    """Test queries against objectclass table"""
    
    def test_count_objectclasses(self, db_connection):
        """Test counting objectclasses"""
        db_connection.execute("SELECT COUNT(*) FROM citydb.objectclass")
        count = db_connection.fetchone()[0]
        assert count >= 4  # Building, BuildingPart, CityFurniture, LandUse
    
    def test_objectclass_attributes(self, db_connection):
        """Test objectclass has required attributes"""
        db_connection.execute("""
            SELECT id, classname, is_top_level 
            FROM citydb.objectclass 
            WHERE classname = 'Building'
        """)
        result = db_connection.fetchone()
        
        assert result is not None
        assert result[0] == 26  # Building ID
        assert result[1] == 'Building'
        assert result[2] is True
    
    def test_top_level_objectclasses(self, db_connection):
        """Test filtering top-level objectclasses"""
        db_connection.execute("""
            SELECT COUNT(*) FROM citydb.objectclass 
            WHERE is_top_level = TRUE
        """)
        count = db_connection.fetchone()[0]
        assert count >= 3


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
        db_connection.execute("SELECT COUNT(*) FROM citydb.feature")
        db_connection.fetchone()
        elapsed = time.time() - start
        
        # Query should complete in under 1 second
        assert elapsed < 1.0
    
    def test_index_usage(self, db_connection):
        """Test that indexes are being used"""
        db_connection.execute("""
            EXPLAIN ANALYZE 
            SELECT * FROM citydb.feature 
            WHERE class = 'Building'
        """)
        result = db_connection.fetchone()
        
        # EXPLAIN should return a plan
        assert result is not None
