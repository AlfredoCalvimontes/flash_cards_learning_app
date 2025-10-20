"""Database migration utilities and version tracking.

This module provides tools for handling database schema migrations and version tracking.
It ensures proper upgrades and downgrades between versions, with validation and
rollback support.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from database.init_db import get_schema_version, set_schema_version

logger = logging.getLogger(__name__)


def get_available_migrations() -> Dict[str, Dict[str, str]]:
    """Get all available migration paths.
    
    Returns:
        Dict mapping source versions to dict of {target_version: migration_name}
    """
    # This will be populated by migration scripts
    return {}


def run_migration(
    engine: Engine,
    target_version: str,
    current_version: Optional[str] = None,
) -> bool:
    """Run database migration to target version.
    
    Args:
        engine: SQLAlchemy engine to use
        target_version: Version to migrate to
        current_version: Current version override (if None, reads from DB)
        
    Returns:
        True if migration was successful
        
    Raises:
        RuntimeError: If migration fails
    """
    session = Session(engine)
    
    try:
        with session.begin():
            if current_version is None:
                current_version = get_schema_version(session)
                
            if current_version == target_version:
                logger.info("Database already at version %s", target_version)
                return True
                
            # Get migration path
            migrations = get_available_migrations()
            if current_version not in migrations:
                raise RuntimeError(
                    f"No migration path from version {current_version}"
                )
                
            targets = migrations[current_version]
            if target_version not in targets:
                raise RuntimeError(
                    f"No migration path from {current_version} to {target_version}"
                )
                
            # Run migration
            logger.info(
                "Migrating database from %s to %s",
                current_version,
                target_version,
            )
            
            migration_name = targets[target_version]
            # Import and run migration
            module = __import__(
                f"database.migrations.{migration_name}",
                fromlist=["migrate"],
            )
            module.migrate(engine)  # type: ignore
            
            # Update version
            set_schema_version(session, target_version)
            logger.info("Migration complete")
            return True
            
    except Exception as e:
        logger.error("Migration failed: %s", str(e))
        raise RuntimeError(f"Failed to migrate database: {str(e)}") from e
