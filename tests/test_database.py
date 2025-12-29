"""Tests for database operations."""

import os
import pytest

# Use a test database
os.environ["ZENITH_TEST_MODE"] = "1"

from src.zenith.database.connection import get_database_path
from src.zenith.database.schema import initialize_database
from src.zenith.database import (
    create_account,
    get_account_by_id,
    update_account_balance,
    record_transaction,
    get_transactions_by_account,
)
from src.zenith.models import TransactionType


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a fresh test database for each test."""
    db_path = get_database_path()
    
    # Remove existing test db
    if db_path.exists():
        db_path.unlink()
    
    # Initialize fresh db
    initialize_database()
    
    yield
    
    # Cleanup after test
    if db_path.exists():
        db_path.unlink()


class TestAccountOperations:
    """Tests for account CRUD operations."""
    
    def test_create_account_returns_account_with_id(self):
        """Creating an account should return an Account with a UUID."""
        account = create_account("John Doe")
        
        assert account.account_id is not None
        assert len(account.account_id) == 36  # UUID format
        assert account.holder_name == "John Doe"
        assert account.balance == 0.0
    
    def test_get_account_by_id_returns_account(self):
        """Getting an account by ID should return the correct account."""
        created = create_account("Jane Doe")
        
        fetched = get_account_by_id(created.account_id)
        
        assert fetched is not None
        assert fetched.account_id == created.account_id
        assert fetched.holder_name == "Jane Doe"
    
    def test_get_account_by_invalid_id_returns_none(self):
        """Getting an account with invalid ID should return None."""
        result = get_account_by_id("invalid-id")
        
        assert result is None
    
    def test_update_account_balance(self):
        """Updating balance should persist the new value."""
        account = create_account("Test User")
        
        update_account_balance(account.account_id, 100.0)
        
        updated = get_account_by_id(account.account_id)
        assert updated.balance == 100.0


class TestTransactionOperations:
    """Tests for transaction CRUD operations."""
    
    def test_record_deposit_transaction(self):
        """Recording a deposit should create a transaction record."""
        account = create_account("Test User")
        
        txn = record_transaction(
            account.account_id,
            TransactionType.DEPOSIT,
            50.0,
        )
        
        assert txn.transaction_id is not None
        assert txn.account_id == account.account_id
        assert txn.type == "DEPOSIT"
        assert txn.amount == 50.0
        assert txn.created_at is not None
    
    def test_record_withdrawal_transaction(self):
        """Recording a withdrawal should create a transaction record."""
        account = create_account("Test User")
        
        txn = record_transaction(
            account.account_id,
            TransactionType.WITHDRAWAL,
            25.0,
        )
        
        assert txn.type == "WITHDRAWAL"
        assert txn.amount == 25.0
    
    def test_get_transactions_returns_ordered_by_recent(self):
        """Transactions should be returned most recent first."""
        account = create_account("Test User")
        
        record_transaction(account.account_id, TransactionType.DEPOSIT, 10.0)
        record_transaction(account.account_id, TransactionType.DEPOSIT, 20.0)
        record_transaction(account.account_id, TransactionType.WITHDRAWAL, 5.0)
        
        transactions = get_transactions_by_account(account.account_id)
        
        assert len(transactions) == 3
        assert transactions[0].type == "WITHDRAWAL"  # Most recent
        assert transactions[0].amount == 5.0
    
    def test_get_transactions_respects_limit(self):
        """Limit parameter should restrict number of results."""
        account = create_account("Test User")
        
        for i in range(5):
            record_transaction(account.account_id, TransactionType.DEPOSIT, float(i))
        
        transactions = get_transactions_by_account(account.account_id, limit=2)
        
        assert len(transactions) == 2
