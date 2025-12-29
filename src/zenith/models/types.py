"""Type definitions and constants for the banking system."""

from dataclasses import dataclass


class TransactionType:
    """Constants for transaction types."""
    
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


@dataclass
class Account:
    """Represents a bank account."""
    
    account_id: str
    holder_name: str
    balance: float


@dataclass
class Transaction:
    """Represents a transaction record."""
    
    transaction_id: str
    account_id: str
    type: str
    amount: float
    created_at: str
