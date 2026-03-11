-- 3DCityDB Minimal Schema for Testing
-- This creates a minimal schema required for citydb-3dtiler tests

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create citydb schema
CREATE SCHEMA IF NOT EXISTS citydb;

-- Create minimal tables required for testing
CREATE TABLE IF NOT EXISTS citydb.cityobject (
    id SERIAL PRIMARY KEY,
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
    creation_date TIMESTAMP,
    termination_date TIMESTAMP,
    external_reference_oid VARCHAR(4000),
    external_reference_uri VARCHAR(4000),
    genericattrib_id INTEGER,
    geometry_id INTEGER,
    surface_geometry_id INTEGER,
    address_id INTEGER,
    cityobjectgroup_id INTEGER,
    citymodel_id INTEGER
);

CREATE TABLE IF NOT EXISTS citydb.building (
    id SERIAL PRIMARY KEY,
    objectclass_id INTEGER,
    class VARCHAR(1000),
    function VARCHAR(4000),
    usage VARCHAR(4000),
    year_of_construction INTEGER,
    year_of_demolition INTEGER,
    roof_type VARCHAR(256),
    measured_height NUMERIC,
    storeys_above_ground INTEGER,
    storeys_below_ground INTEGER,
    lod1_solid_id INTEGER,
    lod2_solid_id INTEGER,
    lod3_solid_id INTEGER,
    lod4_solid_id INTEGER,
    lod1_terrain_intersection_curve_id INTEGER,
    lod2_terrain_intersection_curve_id INTEGER,
    lod3_terrain_intersection_curve_id INTEGER,
    lod4_terrain_intersection_curve_id INTEGER,
    lod1_multi_surface_id INTEGER,
    lod2_multi_surface_id INTEGER,
    lod3_multi_surface_id INTEGER,
    lod4_multi_surface_id INTEGER,
    lod1_multi_curve_id INTEGER,
    lod2_multi_curve_id INTEGER,
    lod3_multi_curve_id INTEGER,
    lod4_multi_curve_id INTEGER,
    lod1_multi_point_id INTEGER,
    lod2_multi_point_id INTEGER,
    lod3_multi_point_id INTEGER,
    lod4_multi_point_id INTEGER,
    lod1_geometry_id INTEGER,
    lod2_geometry_id INTEGER,
    lod3_geometry_id INTEGER,
    lod4_geometry_id INTEGER,
    lod1_implicit_representation_id INTEGER,
    lod2_implicit_representation_id INTEGER,
    lod3_implicit_representation_id INTEGER,
    lod4_implicit_representation_id INTEGER,
    building_parent_id INTEGER,
    building_part_parent_id INTEGER,
    address_id INTEGER,
    cityobject_id INTEGER
);

CREATE TABLE IF NOT EXISTS citydb.surface_geometry (
    id SERIAL PRIMARY KEY,
    gmlid VARCHAR(4000),
    gmlid_codespace VARCHAR(1000),
    parent_id INTEGER,
    root_id INTEGER,
    geometry_geometry GEOMETRY,
    solid_geometry GEOMETRY,
    implicit_geometry GEOMETRY,
    tin_geometry GEOMETRY,
    linestring_geometry GEOMETRY,
    geometry_envelope GEOMETRY
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS cityobject_class_idx ON citydb.cityobject(class);
CREATE INDEX IF NOT EXISTS cityobject_gmlid_idx ON citydb.cityobject(gmlid);
CREATE INDEX IF NOT EXISTS building_objectclass_id_idx ON citydb.building(objectclass_id);

-- Insert test data
INSERT INTO citydb.cityobject (gmlid, class, name) VALUES 
    ('TEST_BUILDING_001', 'Building', 'Test Building 1'),
    ('TEST_BUILDING_002', 'Building', 'Test Building 2'),
    ('TEST_BUILDING_003', 'Building', 'Test Building 3');

INSERT INTO citydb.building (objectclass_id, class, name) VALUES 
    (26, 'Building', 'Test Building 1'),
    (26, 'Building', 'Test Building 2'),
    (26, 'Building', 'Test Building 3');

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA citydb TO testuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA citydb TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA citydb TO testuser;
