-- 3DCityDB v5.x Minimal Schema for Testing
-- Based on actual schema used by citydb-3dtiler
-- Reference: standalone_queries/*.sql files in the repository

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create citydb schema
CREATE SCHEMA IF NOT EXISTS citydb;

-- ============================================
-- 3DCityDB v5.x Core Tables
-- ============================================

-- ObjectClass table: stores object class definitions
CREATE TABLE IF NOT EXISTS citydb.objectclass (
    id INTEGER PRIMARY KEY,
    classname VARCHAR(256) NOT NULL,
    is_top_level BOOLEAN DEFAULT TRUE,
    parent_id INTEGER
);

-- Namespace table: stores XML namespaces
CREATE TABLE IF NOT EXISTS citydb.namespace (
    id INTEGER PRIMARY KEY,
    alias VARCHAR(256) NOT NULL,
    uri VARCHAR(1024)
);

-- Datatype table: stores property datatypes
CREATE TABLE IF NOT EXISTS citydb.datatype (
    id INTEGER PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    description TEXT
);

-- Feature table: main table for city features (replaces cityobject in v5.x)
CREATE TABLE IF NOT EXISTS citydb.feature (
    id SERIAL PRIMARY KEY,
    objectclass_id INTEGER REFERENCES citydb.objectclass(id),
    gmlid VARCHAR(4000),
    gmlid_codespace VARCHAR(1000),
    name VARCHAR(4000),
    name_codespace VARCHAR(1000),
    description VARCHAR(4000),
    class VARCHAR(1000),
    function VARCHAR(4000),
    usage VARCHAR(4000),
    creation_date TIMESTAMP,
    termination_date TIMESTAMP,
    relative_to_terrain VARCHAR(256),
    relative_to_water VARCHAR(256),
    citymodel_id INTEGER
);

-- Property table: stores feature properties
CREATE TABLE IF NOT EXISTS citydb.property (
    id SERIAL PRIMARY KEY,
    feature_id INTEGER REFERENCES citydb.feature(id),
    parent_id INTEGER,
    namespace_id INTEGER REFERENCES citydb.namespace(id),
    datatype_id INTEGER REFERENCES citydb.datatype(id),
    name VARCHAR(256) NOT NULL,
    value TEXT,
    unit VARCHAR(256)
);

-- Geometry_Data table: stores geometry references
CREATE TABLE IF NOT EXISTS citydb.geometry_data (
    id SERIAL PRIMARY KEY,
    feature_id INTEGER REFERENCES citydb.feature(id),
    geometry GEOMETRY,
    lod INTEGER,
    geometry_type VARCHAR(64)
);

-- Surface_Geometry table: stores surface geometries
CREATE TABLE IF NOT EXISTS citydb.surface_geometry (
    id SERIAL PRIMARY KEY,
    gmlid VARCHAR(4000),
    gmlid_codespace VARCHAR(1000),
    parent_id INTEGER,
    root_id INTEGER,
    geometry GEOMETRY,
    solid_geometry GEOMETRY,
    envelope GEOMETRY
);

-- ============================================
-- Material Tables (used by citydb-3dtiler)
-- ============================================

-- Materials for features table (from create_materials_for_features_table.sql)
CREATE TABLE IF NOT EXISTS citydb._materials_for_features (
    id SERIAL PRIMARY KEY,
    namespace_of_classname TEXT,
    classname TEXT,
    namespace_of_property TEXT,
    property_name TEXT,
    column_name_of_property_value TEXT,
    property_value TEXT,
    emmisive_color TEXT,
    pbr_metallic_roughness_base_color TEXT,
    pbr_metallic_roughness_metallic_roughness TEXT,
    pbr_specular_glossiness_diffuse_color TEXT,
    pbr_specular_glossiness_specular_glossiness TEXT
);

-- ============================================
-- Indexes for Performance
-- ============================================

CREATE INDEX IF NOT EXISTS feature_objectclass_id_idx ON citydb.feature(objectclass_id);
CREATE INDEX IF NOT EXISTS feature_gmlid_idx ON citydb.feature(gmlid);
CREATE INDEX IF NOT EXISTS feature_class_idx ON citydb.feature(class);
CREATE INDEX IF NOT EXISTS property_feature_id_idx ON citydb.property(feature_id);
CREATE INDEX IF NOT EXISTS geometry_data_feature_id_idx ON citydb.geometry_data(feature_id);
CREATE INDEX IF NOT EXISTS geometry_data_geom_idx ON citydb.geometry_data USING GIST(geometry);

-- ============================================
-- Test Data
-- ============================================

-- Insert object classes
INSERT INTO citydb.objectclass (id, classname, is_top_level) VALUES 
    (26, 'Building', TRUE),
    (27, 'BuildingPart', FALSE),
    (64, 'CityFurniture', TRUE),
    (83, 'LandUse', TRUE);

-- Insert namespaces
INSERT INTO citydb.namespace (id, alias, uri) VALUES 
    (1, 'core', 'http://www.opengis.net/citygml/2.0'),
    (2, 'bldg', 'http://www.opengis.net/citygml/building/2.0'),
    (3, 'frn', 'http://www.opengis.net/citygml/cityfurniture/2.0');

-- Insert datatypes
INSERT INTO citydb.datatype (id, name, description) VALUES 
    (1, 'String', 'String value'),
    (2, 'Integer', 'Integer value'),
    (3, 'Double', 'Double value'),
    (10, 'GeometryProperty', 'Geometry property'),
    (11, 'FeatureProperty', 'Feature reference');

-- Insert test features (buildings)
INSERT INTO citydb.feature (objectclass_id, gmlid, class, name) VALUES 
    (26, 'TEST_BUILDING_001', 'Building', 'Test Building 1'),
    (26, 'TEST_BUILDING_002', 'Building', 'Test Building 2'),
    (26, 'TEST_BUILDING_003', 'Building', 'Test Building 3'),
    (64, 'TEST_FURNITURE_001', 'CityFurniture', 'Test Bench 1');

-- Insert test properties
INSERT INTO citydb.property (feature_id, namespace_id, datatype_id, name, value) VALUES 
    (1, 2, 1, 'roofType', 'flat'),
    (1, 2, 2, 'storeysAboveGround', '5'),
    (2, 2, 1, 'roofType', 'gabled'),
    (2, 2, 2, 'storeysAboveGround', '3'),
    (3, 2, 1, 'roofType', 'hipped'),
    (3, 2, 2, 'storeysAboveGround', '2');

-- Insert test geometry data
INSERT INTO citydb.geometry_data (feature_id, geometry, lod, geometry_type) VALUES 
    (1, ST_MakeEnvelope(10, 10, 20, 20, 4326), 1, 'lod1Solid'),
    (2, ST_MakeEnvelope(30, 30, 40, 40, 4326), 1, 'lod1Solid'),
    (3, ST_MakeEnvelope(50, 50, 60, 60, 4326), 2, 'lod2Solid'),
    (4, ST_MakeEnvelope(70, 70, 75, 75, 4326), 1, 'lod1Solid');

-- Insert test materials
INSERT INTO citydb._materials_for_features 
    (classname, property_name, property_value, emmisive_color) VALUES 
    ('Building', 'roofType', 'flat', '[0.2, 0.2, 0.2, 1.0]'),
    ('Building', 'roofType', 'gabled', '[0.5, 0.3, 0.1, 1.0]'),
    ('CityFurniture', NULL, NULL, '[0.8, 0.8, 0.8, 1.0]');

-- ============================================
-- Permissions
-- ============================================

GRANT ALL PRIVILEGES ON SCHEMA citydb TO testuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA citydb TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA citydb TO testuser;
