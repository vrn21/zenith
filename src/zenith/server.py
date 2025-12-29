"""FastMCP server with banking tools."""

from fastmcp import FastMCP

from .database import (
    initialize_database,
    create_account as db_create_account,
    get_account_by_id,
    update_account_balance,
    record_transaction,
    get_transactions_by_account,
)
from .models import TransactionType


# Initialize the MCP server
mcp = FastMCP("Banking Server")


@mcp.tool()
def create_account(holder_name: str) -> dict:
    """Create a new bank account.
    
    Args:
        holder_name: Name of the account holder.
        
    Returns:
        Account details including the generated account ID.
    """
    account = db_create_account(holder_name)
    
    return {
        "message": "Account created successfully",
        "account_id": account.account_id,
        "holder_name": account.holder_name,
        "balance": account.balance,
    }


@mcp.tool()
def deposit(account_id: str, amount: float) -> dict:
    """Add funds to an existing account.
    
    Args:
        account_id: The unique account identifier.
        amount: The amount to deposit (must be positive).
        
    Returns:
        Updated account balance or error message.
    """
    # Validate amount
    if amount <= 0:
        return {"error": "Amount must be positive"}
    
    # Find account
    account = get_account_by_id(account_id)
    if account is None:
        return {"error": "Account not found", "account_id": account_id}
    
    # Update balance
    new_balance = account.balance + amount
    update_account_balance(account_id, new_balance)
    
    # Record transaction
    record_transaction(account_id, TransactionType.DEPOSIT, amount)
    
    return {
        "message": "Deposit successful",
        "account_id": account_id,
        "deposited": amount,
        "new_balance": new_balance,
    }


@mcp.tool()
def withdraw(account_id: str, amount: float) -> dict:
    """Remove funds from an existing account.
    
    Args:
        account_id: The unique account identifier.
        amount: The amount to withdraw (must be positive).
        
    Returns:
        Updated account balance or error message.
    """
    # Validate amount
    if amount <= 0:
        return {"error": "Amount must be positive"}
    
    # Find account
    account = get_account_by_id(account_id)
    if account is None:
        return {"error": "Account not found", "account_id": account_id}
    
    # Check sufficient funds
    if account.balance < amount:
        return {
            "error": "Insufficient funds",
            "balance": account.balance,
            "requested": amount,
        }
    
    # Update balance
    new_balance = account.balance - amount
    update_account_balance(account_id, new_balance)
    
    # Record transaction
    record_transaction(account_id, TransactionType.WITHDRAWAL, amount)
    
    return {
        "message": "Withdrawal successful",
        "account_id": account_id,
        "withdrawn": amount,
        "new_balance": new_balance,
    }


@mcp.tool()
def get_balance(account_id: str) -> dict:
    """Check the current balance of an account.
    
    Args:
        account_id: The unique account identifier.
        
    Returns:
        Current balance or error message.
    """
    account = get_account_by_id(account_id)
    if account is None:
        return {"error": "Account not found", "account_id": account_id}
    
    return {
        "account_id": account_id,
        "holder_name": account.holder_name,
        "balance": account.balance,
    }


@mcp.tool()
def get_transactions(account_id: str, limit: int = 10) -> dict:
    """View recent transactions for an account.
    
    Args:
        account_id: The unique account identifier.
        limit: Maximum number of transactions to return (default 10).
        
    Returns:
        List of recent transactions or error message.
    """
    # Verify account exists
    account = get_account_by_id(account_id)
    if account is None:
        return {"error": "Account not found", "account_id": account_id}
    
    transactions = get_transactions_by_account(account_id, limit)
    
    return {
        "account_id": account_id,
        "transaction_count": len(transactions),
        "transactions": [
            {
                "transaction_id": txn.transaction_id,
                "type": txn.type,
                "amount": txn.amount,
                "created_at": txn.created_at,
            }
            for txn in transactions
        ],
    }


# Initialize database when module loads
initialize_database()
