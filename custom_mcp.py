"""MCP server with Supabase PostgreSQL database integration."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import asyncpg
from mcp.server.fastmcp import Context, FastMCP


class SupabaseDatabase:
    """Supabase PostgreSQL database connection manager."""

    def __init__(self):
        self.connection: Optional[asyncpg.Connection] = None

    @classmethod
    async def connect(cls) -> "SupabaseDatabase":
        """Connect to Supabase PostgreSQL database."""
        instance = cls()
        
        # Get connection details from environment variables
        db_url = os.getenv("SUPABASE_DB_URL")
        if not db_url:
            # Construct URL from individual components if SUPABASE_DB_URL not provided
            host = os.getenv("SUPABASE_HOST", "localhost")
            port = int(os.getenv("SUPABASE_PORT", "5432"))
            database = os.getenv("SUPABASE_DATABASE", "postgres")
            user = os.getenv("SUPABASE_USER", "postgres")
            password = os.getenv("SUPABASE_PASSWORD", "")
            
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        try:
            instance.connection = await asyncpg.connect(db_url)
            return instance
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase database: {e}")

    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self.connection:
            await self.connection.close()

    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        try:
            rows = await self.connection.fetch(query, *args)
            return [dict(row) for row in rows]
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")

    async def execute_command(self, command: str, *args) -> str:
        """Execute an INSERT/UPDATE/DELETE command and return status."""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        try:
            result = await self.connection.execute(command, *args)
            return result
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}")

    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch a single row from query."""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        try:
            row = await self.connection.fetchrow(query, *args)
            return dict(row) if row else None
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")

    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a table."""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = $1
        ORDER BY ordinal_position;
        """
        return await self.execute_query(query, table_name)

    async def list_tables(self) -> List[str]:
        """List all tables in the current schema."""
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        rows = await self.execute_query(query)
        return [row['table_name'] for row in rows]


@dataclass
class AppContext:
    """Application context with typed dependencies."""
    db: SupabaseDatabase


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context."""
    # Initialize on startup
    db = await SupabaseDatabase.connect()
    try:
        yield AppContext(db=db)
    finally:
        # Cleanup on shutdown
        await db.disconnect()


# Pass lifespan to server
mcp = FastMCP("Supabase MCP Server", lifespan=app_lifespan)


@mcp.tool()
async def execute_query(ctx: Context, query: str) -> Dict[str, Any]:
    """Execute a SELECT query on the Supabase database."""
    db = ctx.request_context.lifespan_context.db
    try:
        results = await db.execute_query(query)
        return {
            "success": True,
            "row_count": len(results),
            "data": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def execute_command(ctx: Context, command: str) -> Dict[str, Any]:
    """Execute an INSERT/UPDATE/DELETE command on the Supabase database."""
    db = ctx.request_context.lifespan_context.db
    try:
        result = await db.execute_command(command)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def get_table_schema(ctx: Context, table_name: str) -> Dict[str, Any]:
    """Get schema information for a specific table."""
    db = ctx.request_context.lifespan_context.db
    try:
        schema = await db.get_table_schema(table_name)
        return {
            "success": True,
            "table_name": table_name,
            "columns": schema
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def list_tables(ctx: Context) -> Dict[str, Any]:
    """List all tables in the database."""
    db = ctx.request_context.lifespan_context.db
    try:
        tables = await db.list_tables()
        return {
            "success": True,
            "tables": tables
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def fetch_table_data(ctx: Context, table_name: str, limit: int = 100) -> Dict[str, Any]:
    """Fetch data from a specific table with optional limit."""
    db = ctx.request_context.lifespan_context.db
    try:
        query = f"SELECT * FROM {table_name} LIMIT $1"
        results = await db.execute_query(query, limit)
        return {
            "success": True,
            "table_name": table_name,
            "row_count": len(results),
            "data": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Example usage - you would typically run this through MCP
    import asyncio
    
    async def test_connection():
        """Test the database connection."""
        try:
            db = await SupabaseDatabase.connect()
            tables = await db.list_tables()
            print(f"Connected successfully! Found tables: {tables}")
            await db.disconnect()
        except Exception as e:
            print(f"Connection failed: {e}")
    
    # Uncomment to test connection
    # asyncio.run(test_connection())