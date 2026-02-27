# Alembic Migration Guide

## Setup Complete ✓

Alembic is now configured and your current database schema has been captured.

## Common Commands

### Create a new migration (after changing models)
```bash
./venv/bin/alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
./venv/bin/alembic upgrade head
```

### Rollback last migration
```bash
./venv/bin/alembic downgrade -1
```

### View migration history
```bash
./venv/bin/alembic history
```

### Check current version
```bash
./venv/bin/alembic current
```

## Workflow Example

1. Modify your models (e.g., add a column to `User` model)
2. Generate migration: `./venv/bin/alembic revision --autogenerate -m "add phone column to users"`
3. Review the generated migration file in `alembic/versions/`
4. Apply migration: `./venv/bin/alembic upgrade head`

## Notes

- Migration files are in `alembic/versions/`
- Always review auto-generated migrations before applying
- You can now delete the old migration scripts: `add_expired_status.py`, `add_is_active_column.py`
- The `create_admin.py` script is still useful for seeding data
