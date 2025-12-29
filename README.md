# Zenith Banking MCP Server

MCP (Model Context Protocol) server exposing banking operations as tools. Built with FastMCP and SQLite.

## Features

- **Account Management**: Create accounts, check balances
- **Transactions**: Deposits and withdrawals with validation
- **History**: View recent transactions ordered by date
- **Persistence**: SQLite database with accounts and transactions tables

## Quick Start

```bash
uv add fastmcp    # Install dependencies
uv run python main.py    # Start server (SSE transport)
```

## MCP Tools

| Tool               | Input                  | Description                      |
| ------------------ | ---------------------- | -------------------------------- |
| `create_account`   | `holder_name`          | Create account, returns UUID     |
| `deposit`          | `account_id`, `amount` | Add funds                        |
| `withdraw`         | `account_id`, `amount` | Remove funds (validates balance) |
| `get_balance`      | `account_id`           | Current balance                  |
| `get_transactions` | `account_id`, `limit?` | Recent transactions              |

## Project Structure

```
src/zenith/
├── server.py              # MCP server + tools
├── database/
│   ├── connection.py      # SQLite connection
│   ├── schema.py          # Table definitions
│   └── operations.py      # CRUD operations
└── models/
    └── types.py           # Account, Transaction dataclasses
```

## Database Schema

**accounts**: `account_id` (PK), `holder_name`, `balance`

**transactions**: `transaction_id` (PK), `account_id` (FK), `type`, `amount`, `created_at`

## Testing

```bash
uv run pytest tests/ -v    # 16 tests (database + server tools)
```

## Error Handling

- Invalid account ID → `{"error": "Account not found"}`
- Insufficient funds → `{"error": "Insufficient funds", "balance": X, "requested": Y}`
- Invalid amount → `{"error": "Amount must be positive"}`

## Docker Deployment

```bash
# Build and run
docker compose up -d

# Or manually
docker build -t zenith-banking .
docker run -p 8000:8000 -v ./data:/app/data zenith-banking
```

Server accessible at `http://localhost:8000`
