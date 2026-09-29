from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy import inspect, text
from alembic.config import Config
from alembic import command
from app.core.logging import logger
from app.core.database import engine

def find_alembic_ini() -> Path:
    """Locate alembic.ini relative to this module or current working directory."""
    candidate_paths = [
        Path(__file__).resolve().parents[1] / "alembic.ini",        # apps/api/alembic.ini
        Path(__file__).resolve().parents[3] / "alembic.ini",        # repo_root/alembic.ini
        Path.cwd() / "alembic.ini",                                # cwd/alembic.ini
        Path.cwd().parent / "alembic.ini",
        Path.cwd().parent.parent / "alembic.ini",
    ]
    for path in candidate_paths:
        if path.exists():
            return path
    raise FileNotFoundError(f"Could not locate alembic.ini in candidates: {[str(p) for p in candidate_paths]}")

def get_db_migration_status(db_engine=engine) -> Dict[str, Any]:
    """
    Inspects the actual database schema to determine table presence and Alembic revision state.
    Never exposes database passwords or connection secrets.
    """
    inspector = inspect(db_engine)
    existing_tables = set(inspector.get_table_names())
    
    has_conversations = "conversation_messages" in existing_tables
    has_preferences = "user_preferences" in existing_tables
    has_alembic_version = "alembic_version" in existing_tables
    
    current_rev: Optional[str] = None
    if has_alembic_version:
        with db_engine.connect() as conn:
            try:
                result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).fetchone()
                if result:
                    current_rev = str(result[0])
            except Exception as e:
                logger.warning(f"Could not query alembic_version: {e}")
                
    return {
        "existing_tables": sorted(list(existing_tables)),
        "conversation_messages_exists": has_conversations,
        "user_preferences_exists": has_preferences,
        "alembic_version_exists": has_alembic_version,
        "current_revision": current_rev,
        "migration_applied": has_conversations and has_preferences and (current_rev == "b2c3d4e5f6a7")
    }

def run_safe_migration(db_engine=engine) -> Dict[str, Any]:
    """
    Performs safe Alembic migration against the production database:
    1. Determines whether conversation_messages and user_preferences tables actually exist.
    2. If missing, runs 'alembic upgrade head' to apply the proper Alembic migration.
    3. If tables already exist but alembic_version is not stamped, stamps head.
    4. Never modifies schema using create_all as a substitute for Alembic migrations.
    """
    status_before = get_db_migration_status(db_engine)
    
    if status_before["migration_applied"]:
        logger.info("Database migration already applied (b2c3d4e5f6a7). Tables present.")
        return {"action": "already_applied", "status": status_before}
        
    alembic_ini_path = find_alembic_ini()
    cfg = Config(str(alembic_ini_path))
    
    # If tables do not exist, run proper Alembic upgrade
    if not status_before["conversation_messages_exists"] or not status_before["user_preferences_exists"]:
        logger.info("Tables conversation_messages or user_preferences missing. Executing proper Alembic upgrade to head...")
        command.upgrade(cfg, "head")
        logger.info("Alembic upgrade to head completed successfully.")
        action_taken = "upgraded"
    else:
        # Tables exist but alembic_version may not be at head
        logger.info("Tables exist; aligning Alembic revision to head...")
        command.stamp(cfg, "head")
        action_taken = "stamped"
        
    status_after = get_db_migration_status(db_engine)
    return {"action": action_taken, "status": status_after}
