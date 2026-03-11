"""
Pytest fixtures for citydb-3dtiler tests
Provides database connections and test utilities
"""
import pytest
import psycopg2
import os
import time
from typing import Generator, Dict, Any


# PostgreSQL version configurations
POSTGRES_CONFIGS = {
    "13": {
        "image": "postgis/postgis:13-3.1",
        "port": 5432,
        "container_name": "citydb-test-pg13"
    },
    "14": {
        "image": "postgis/postgis:14-3.2",
        "port": 5433,
        "container_name": "citydb-test-pg14"
    },
    "15": {
        "image": "postgis/postgis:15-3.3",
        "port": 5434,
        "container_name": "citydb-test-pg15"
    },
    "16": {
        "image": "postgis/postgis:16-3.4",
        "port": 5435,
        "container_name": "citydb-test-pg16"
    }
}


class DatabaseConnection:
    """Database connection wrapper for testing"""
    
    def __init__(self, host: str = "localhost", port: int = 5432,
                 dbname: str = "citydb_test", user: str = "testuser",
                 password: str = "testpass"):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = None
        self.cur = None
    
    def connect(self, timeout: int = 30) -> bool:
        """Establish database connection with retry"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password
                )
                self.conn.autocommit = True
                self.cur = self.conn.cursor()
                return True
            except psycopg2.OperationalError:
                time.sleep(1)
        return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    def execute(self, query: str, params: tuple = None):
        """Execute SQL query"""
        if params:
            self.cur.execute(query, params)
        else:
            self.cur.execute(query)
        return self.cur
    
    def fetchone(self):
        """Fetch single row"""
        return self.cur.fetchone()
    
    def fetchall(self):
        """Fetch all rows"""
        return self.cur.fetchall()
    
    def get_postgres_version(self) -> str:
        """Get PostgreSQL version"""
        self.cur.execute("SELECT version();")
        return self.cur.fetchone()[0]
    
    def get_postgis_version(self) -> str:
        """Get PostGIS version"""
        self.cur.execute("SELECT PostGIS_Version();")
        return self.cur.fetchone()[0]


@pytest.fixture(scope="session")
def db_config() -> Dict[str, Any]:
    """Default database configuration"""
    return {
        "host": os.getenv("TEST_DB_HOST", "localhost"),
        "port": int(os.getenv("TEST_DB_PORT", 5432)),
        "dbname": os.getenv("TEST_DB_NAME", "citydb_test"),
        "user": os.getenv("TEST_DB_USER", "testuser"),
        "password": os.getenv("TEST_DB_PASSWORD", "testpass")
    }


@pytest.fixture(scope="session")
def db_connection(db_config: Dict[str, Any]) -> Generator[DatabaseConnection, None, None]:
    """
    Create database connection for tests.
    Requires database to be running (start with docker-compose first).
    """
    db = DatabaseConnection(**db_config)
    if not db.connect():
        pytest.skip(f"Cannot connect to database at {db_config['host']}:{db_config['port']}")
    
    yield db
    db.disconnect()


@pytest.fixture
def db_cursor(db_connection: DatabaseConnection):
    """Provide database cursor for tests"""
    yield db_connection.cur


@pytest.fixture(params=["13", "14", "15", "16"], scope="session")
def postgres_version(request) -> str:
    """Parametrize tests for different PostgreSQL versions"""
    return request.param


@pytest.fixture(scope="session")
def version_specific_db(postgres_version: str) -> Generator[DatabaseConnection, None, None]:
    """
    Create database connection for specific PostgreSQL version.
    Requires docker-compose to start the specific version.
    """
    config = POSTGRES_CONFIGS.get(postgres_version)
    if not config:
        pytest.skip(f"PostgreSQL version {postgres_version} not configured")
    
    db = DatabaseConnection(port=config["port"])
    if not db.connect(timeout=60):
        pytest.skip(f"Cannot connect to PostgreSQL {postgres_version} at port {config['port']}")
    
    yield db
    db.disconnect()


@pytest.fixture
def test_data(db_connection: DatabaseConnection):
    """Insert test data and cleanup after test"""
    # Insert test building
    db_connection.execute("""
        INSERT INTO citydb.building (objectclass_id, class, function)
        VALUES (26, 'TestBuilding', 'TestFunction')
        RETURNING id;
    """)
    building_id = db_connection.fetchone()[0]
    
    yield {"building_id": building_id}
    
    # Cleanup
    db_connection.execute("DELETE FROM citydb.building WHERE id = %s;", (building_id,))


@pytest.fixture
def empty_db(db_connection: DatabaseConnection):
    """Clean database state for tests"""
    # Truncate all tables
    tables = ["citydb.building", "citydb.cityobject", "citydb.surface_geometry"]
    for table in tables:
        try:
            db_connection.execute(f"TRUNCATE TABLE {table} CASCADE;")
        except psycopg2.Error:
            pass
    
    yield
    
    # Cleanup after test
    for table in tables:
        try:
            db_connection.execute(f"TRUNCATE TABLE {table} CASCADE;")
        except psycopg2.Error:
            pass
