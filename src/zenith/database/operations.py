"""Database CRUD operations for accounts and transactions."""

import uuid
from datetime import datetime, timezone

from .connection import get_connection
from ..models.types import Account, Transaction


def create_account(holder_name: str) -> Account:
    """Create a new bank account.
    
    Args:
        holder_name: Name of the account holder.
        
    Returns:
        The newly created Account object.
    """
    account_id = str(uuid.uuid4())
    initial_balance = 0.0
    
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "INSERT INTO accounts (account_id, holder_name, balance) VALUES (?, ?, ?)",
        (account_id, holder_name, initial_balance),
    )
    
    connection.commit()
    connection.close()
    
    return Account(
        account_id=account_id,
        holder_name=holder_name,
        balance=initial_balance,
    )


def get_account_by_id(account_id: str) -> Account | None:
    """Fetch an account by its ID.
    
    Args:
        account_id: The unique account identifier.
        
    Returns:
        Account object if found, None otherwise.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "SELECT account_id, holder_name, balance FROM accounts WHERE account_id = ?",
        (account_id,),
    )
    
    row = cursor.fetchone()
    connection.close()
    
    if row is None:
        return None
    
    return Account(
        account_id=row["account_id"],
        holder_name=row["holder_name"],
        balance=row["balance"],
    )


def update_account_balance(account_id: str, new_balance: float) -> None:
    """Update the balance of an account.
    
    Args:
        account_id: The unique account identifier.
        new_balance: The new balance to set.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "UPDATE accounts SET balance = ? WHERE account_id = ?",
        (new_balance, account_id),
    )
    
    connection.commit()
    connection.close()


def record_transaction(
    account_id: str,
    transaction_type: str,
    amount: float,
) -> Transaction:
    """Record a new transaction.
    
    Args:
        account_id: The account involved in the transaction.
        transaction_type: Either 'DEPOSIT' or 'WITHDRAWAL'.
        amount: The transaction amount (always positive).
        
    Returns:
        The newly created Transaction object.
    """
    transaction_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        """INSERT INTO transactions 
           (transaction_id, account_id, type, amount, created_at) 
           VALUES (?, ?, ?, ?, ?)""",
        (transaction_id, account_id, transaction_type, amount, created_at),
    )
    
    connection.commit()
    connection.close()
    
    return Transaction(
        transaction_id=transaction_id,
        account_id=account_id,
        type=transaction_type,
        amount=amount,
        created_at=created_at,
    )


def get_transactions_by_account(
    account_id: str,
    limit: int = 10,
) -> list[Transaction]:
    """Get recent transactions for an account.
    
    Args:
        account_id: The account to get transactions for.
        limit: Maximum number of transactions to return.
        
    Returns:
        List of Transaction objects, ordered by most recent first.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        """SELECT transaction_id, account_id, type, amount, created_at 
           FROM transactions 
           WHERE account_id = ? 
           ORDER BY created_at DESC 
           LIMIT ?""",
        (account_id, limit),
    )
    
    rows = cursor.fetchall()
    connection.close()
    
    return [
        Transaction(
            transaction_id=row["transaction_id"],
            account_id=row["account_id"],
            type=row["type"],
            amount=row["amount"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
