"""Migration template for database schema changes.

This is a template for creating new migration scripts. Copy this file and modify
for each new migration needed. Migration scripts should be idempotent and include
both upgrade and rollback capabilities.
"""

from sqlalchemy import Engine


def migrate(engine: Engine) -> None:
    """Run the migration.
    
    Args:
        engine: SQLAlchemy engine to use
        
    Raises:
        RuntimeError: If migration fails
    """
    # Example migration steps:
    # 1. Create new tables
    # 2. Add columns to existing tables
    # 3. Modify column types
    # 4. Add constraints or indexes
    # 5. Migrate data if needed
    raise NotImplementedError("Migration not implemented")
