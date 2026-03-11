#!/bin/bash
# scripts/update-citydb-schema.sh
# Fetch latest 3DCityDB schema from official repository

set -e

CITYDB_REPO="https://github.com/3dcitydb/3dcitydb.git"
CITYDB_VERSION="${1:-master}"  # Allow specifying version/tag
SCHEMA_DIR="tests/fixtures/init-db"
TEMP_DIR="/tmp/3dcitydb-schema"

echo "🔄 Fetching 3DCityDB schema from official repository..."
echo "   Version: $CITYDB_VERSION"

# Clean up temp directory
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Clone official repository (shallow clone for speed)
git clone --depth 1 --branch "$CITYDB_VERSION" "$CITYDB_REPO" "$TEMP_DIR" 2>/dev/null || {
    echo "⚠️  Failed to clone branch $CITYDB_VERSION, trying master..."
    git clone --depth 1 "$CITYDB_REPO" "$TEMP_DIR"
}

# Copy schema files
echo "📁 Copying schema files..."
cp "$TEMP_DIR/database/postgresql/schema/"*.sql "$SCHEMA_DIR/" 2>/dev/null || {
    echo "⚠️  No schema files found in official repo"
    exit 1
}

# Create minimal test schema from official files
echo "📝 Creating minimal test schema..."
cat > "$SCHEMA_DIR/01-init-schema.sql" << 'EOF'
-- 3DCityDB Schema (Auto-extracted from official repository)
-- Source: https://github.com/3dcitydb/3dcitydb
-- Updated: $(date -Iseconds)

-- Enable PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Include official schema
\i database/postgresql/schema/3dcitydb.sql
\i database/postgresql/schema/3dcitydb_additional_functions.sql

-- Grant permissions for test user
GRANT ALL PRIVILEGES ON SCHEMA citydb TO testuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA citydb TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA citydb TO testuser;
EOF

# Clean up
rm -rf "$TEMP_DIR"

echo "✅ Schema updated successfully!"
echo "   Location: $SCHEMA_DIR/01-init-schema.sql"
echo ""
echo "⚠️  Remember to:"
echo "   1. Review schema changes"
echo "   2. Update test data if needed"
echo "   3. Run full test suite"
