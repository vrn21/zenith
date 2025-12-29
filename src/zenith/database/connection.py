"""Database connection management."""

import sqlite3
from pathlib import Path


def get_database_path() -> Path:
    """Get the path to the SQLite database file.
    
    Returns:
        Path to data/bank.db relative to project root.
    """
    # Get the project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent
    database_path = project_root / "data" / "bank.db"
    
    # Ensure data directory exists
    database_path.parent.mkdir(parents=True, exist_ok=True)
    
    return database_path


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory enabled.
    
    Returns:
        SQLite connection object with Row factory for dict-like access.
    """
    database_path = get_database_path()
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection
