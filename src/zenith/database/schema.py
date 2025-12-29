"""Database schema definitions and initialization."""

from .connection import get_connection


ACCOUNTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    holder_name TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0.0
)
"""

TRANSACTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts (account_id)
)
"""


def initialize_database() -> None:
    """Create database tables if they don't exist."""
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(ACCOUNTS_TABLE_SQL)
    cursor.execute(TRANSACTIONS_TABLE_SQL)
    
    connection.commit()
    connection.close()
