"""Tests for MCP server tools."""

import os
import pytest

os.environ["ZENITH_TEST_MODE"] = "1"

from src.zenith.database.connection import get_database_path
from src.zenith.database.schema import initialize_database
from src.zenith.database import create_account as db_create_account


# Import the actual tool functions (unwrapped)
from src.zenith.server import mcp


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create a fresh test database for each test."""
    db_path = get_database_path()
    
    if db_path.exists():
        db_path.unlink()
    
    initialize_database()
    
    yield
    
    if db_path.exists():
        db_path.unlink()


def call_tool(name: str, arguments: dict) -> dict:
    """Helper to call MCP tools synchronously for testing."""
    import asyncio
    import json
    
    async def _call():
        result = await mcp._tool_manager.call_tool(name, arguments)
        # Extract the text content from ToolResult
        if hasattr(result, 'content') and result.content:
            for item in result.content:
                if hasattr(item, 'text'):
                    return json.loads(item.text)
        return {}
    
    return asyncio.run(_call())


class TestCreateAccountTool:
    """Tests for create_account MCP tool."""
    
    def test_create_account_success(self):
        """Should create account and return details."""
        result = call_tool("create_account", {"holder_name": "Alice"})
        
        assert result["message"] == "Account created successfully"
        assert "account_id" in result
        assert result["holder_name"] == "Alice"
        assert result["balance"] == 0.0


class TestDepositTool:
    """Tests for deposit MCP tool."""
    
    def test_deposit_success(self):
        """Should add funds to account."""
        account = db_create_account("Bob")
        
        result = call_tool("deposit", {
            "account_id": account.account_id,
            "amount": 100.0,
        })
        
        assert result["message"] == "Deposit successful"
        assert result["deposited"] == 100.0
        assert result["new_balance"] == 100.0
    
    def test_deposit_invalid_amount(self):
        """Should reject non-positive amounts."""
        account = db_create_account("Bob")
        
        result = call_tool("deposit", {
            "account_id": account.account_id,
            "amount": -50.0,
        })
        
        assert "error" in result
        assert result["error"] == "Amount must be positive"
    
    def test_deposit_invalid_account(self):
        """Should error for non-existent account."""
        result = call_tool("deposit", {
            "account_id": "invalid-id",
            "amount": 100.0,
        })
        
        assert result["error"] == "Account not found"


class TestWithdrawTool:
    """Tests for withdraw MCP tool."""
    
    def test_withdraw_success(self):
        """Should remove funds from account."""
        account = db_create_account("Charlie")
        call_tool("deposit", {"account_id": account.account_id, "amount": 100.0})
        
        result = call_tool("withdraw", {
            "account_id": account.account_id,
            "amount": 30.0,
        })
        
        assert result["message"] == "Withdrawal successful"
        assert result["withdrawn"] == 30.0
        assert result["new_balance"] == 70.0
    
    def test_withdraw_insufficient_funds(self):
        """Should reject withdrawal exceeding balance."""
        account = db_create_account("Dave")
        call_tool("deposit", {"account_id": account.account_id, "amount": 50.0})
        
        result = call_tool("withdraw", {
            "account_id": account.account_id,
            "amount": 100.0,
        })
        
        assert result["error"] == "Insufficient funds"
        assert result["balance"] == 50.0
        assert result["requested"] == 100.0


class TestGetBalanceTool:
    """Tests for get_balance MCP tool."""
    
    def test_get_balance_success(self):
        """Should return current balance."""
        account = db_create_account("Eve")
        call_tool("deposit", {"account_id": account.account_id, "amount": 75.0})
        
        result = call_tool("get_balance", {"account_id": account.account_id})
        
        assert result["balance"] == 75.0
        assert result["holder_name"] == "Eve"


class TestGetTransactionsTool:
    """Tests for get_transactions MCP tool."""
    
    def test_get_transactions_success(self):
        """Should return transaction history."""
        account = db_create_account("Frank")
        call_tool("deposit", {"account_id": account.account_id, "amount": 100.0})
        call_tool("withdraw", {"account_id": account.account_id, "amount": 25.0})
        
        result = call_tool("get_transactions", {"account_id": account.account_id})
        
        assert result["transaction_count"] == 2
        assert len(result["transactions"]) == 2
        assert result["transactions"][0]["type"] == "WITHDRAWAL"  # Most recent
