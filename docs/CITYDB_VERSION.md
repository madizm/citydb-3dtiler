# 3DCityDB Version Compatibility

## Current Version

- **3DCityDB Version:** v5.2.0 (or latest stable)
- **Schema Version:** 2024-01
- **Tested PostgreSQL Versions:** 13, 14, 15, 16
- **Tested PostGIS Versions:** 3.1, 3.2, 3.3, 3.4

## Official Resources

- **3DCityDB Repository:** https://github.com/3dcitydb/3dcitydb
- **3DCityDB Documentation:** https://3dcitydb-docs.readthedocs.io/
- **Schema Location:** `database/postgresql/schema/`

## Schema Structure (v5.x)

| Table | Purpose |
|-------|---------|
| `feature` | Main features table (replaces `cityobject` from v3.x) |
| `objectclass` | Object class definitions with hierarchy |
| `namespace` | XML namespace definitions |
| `datatype` | Property datatype definitions |
| `property` | Feature properties (key-value pairs) |
| `geometry_data` | Geometry references per LOD |
| `surface_geometry` | Surface geometry storage |
| `_materials_for_features` | Material/styling table (citydb-3dtiler specific) |

## Update Procedure

When 3DCityDB releases a new version:

### 1. Check for Updates

```bash
# Check latest release
curl -s https://api.github.com/repos/3dcitydb/3dcitydb/releases/latest | jq '.tag_name'

# Or visit: https://github.com/3dcitydb/3dcitydb/releases
```

### 2. Update Schema

```bash
# Fetch latest schema from official repository
./scripts/update-citydb-schema.sh

# Or specify a version/tag
./scripts/update-citydb-schema.sh v5.2.0
```

### 3. Review Changes

```bash
# Compare with previous version
git diff tests/fixtures/init-db/01-init-schema.sql
```

### 4. Update Test Data

If schema changes affect test data:

```bash
# Edit test fixtures
vim tests/fixtures/init-db/02-test-data.sql

# Update integration tests if table structure changed
vim tests/integration/test_*.py
```

### 5. Run Full Test Suite

```bash
# Run tests against all PostgreSQL versions
./scripts/run-tests.sh --all-versions

# Or specific version
./scripts/run-tests.sh --postgres-version 15
```

### 6. Update Documentation

```bash
# Update this file with new version
vim docs/CITYDB_VERSION.md

# Commit changes
git add -A
git commit -m "chore: update to 3DCityDB v5.x.x"
git push
```

## CI/CD Integration

The GitHub Actions workflow automatically tests against multiple PostgreSQL versions:

```yaml
# .github/workflows/ci.yml
strategy:
  matrix:
    postgres: [13, 14, 15, 16]
    postgis: [3.1, 3.2, 3.3, 3.4]
```

## Version Compatibility Matrix

| citydb-3dtiler | 3DCityDB | PostgreSQL | PostGIS |
|----------------|----------|------------|---------|
| v0.1.x         | v5.0.x   | 13-15      | 3.1-3.3 |
| v0.2.x         | v5.1.x   | 13-16      | 3.1-3.4 |
| **current**    | **v5.2.x** | **13-16**  | **3.1-3.4** |

## Monitoring for Updates

### GitHub Notifications

1. Watch the 3DCityDB repository: https://github.com/3dcitydb/3dcitydb
2. Enable "Releases" notifications

### Automated Check (Optional)

Add to your CI workflow:

```yaml
- name: Check for 3DCityDB updates
  run: |
    LATEST=$(curl -s https://api.github.com/repos/3dcitydb/3dcitydb/releases/latest | jq -r '.tag_name')
    CURRENT=$(cat CITYDB_VERSION)
    if [ "$LATEST" != "$CURRENT" ]; then
      echo "⚠️ New version available: $LATEST (current: $CURRENT)"
    fi
```

## Troubleshooting

### Schema Mismatch Errors

If tests fail with "column does not exist" or "table does not exist":

```bash
# Verify schema version
psql -h localhost -U testuser -d citydb_test -c "SELECT version FROM citydb.citydb_version;"

# Re-run schema update
./scripts/update-citydb-schema.sh

# Rebuild test containers
docker-compose -f docker-compose.test.yml down -v
docker-compose -f docker-compose.test.yml up -d
```

### Test Data Issues

If test data doesn't match new schema:

```bash
# Review test data file
vim tests/fixtures/init-db/02-test-data.sql

# Check for deprecated columns/tables
# Update INSERT statements to match new schema
```

## References

- [3DCityDB v5 Migration Guide](https://3dcitydb-docs.readthedocs.io/en/latest/migration.html)
- [3DCityDB PostgreSQL Schema](https://github.com/3dcitydb/3dcitydb/tree/master/database/postgresql/schema)
- [PostGIS Documentation](https://postgis.net/documentation/)
