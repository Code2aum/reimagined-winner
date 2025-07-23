"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import os

# Create an MCP server
mcp = FastMCP("AI Sticky Notes")
NOTES_FILE="notes.txt"

def ensure_notes_file_exists():
    """Ensure the notes file exists."""
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, 'w') as f:
            f.write("")
@mcp.tool()
def add_note(note: str)->str:
    """Add a note to the notes file."""
    ensure_notes_file_exists()
    with open(NOTES_FILE, 'a') as f:
        f.write(note + "\n")
    return f"Note added: {note}"