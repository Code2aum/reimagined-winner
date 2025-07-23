"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path

# Create an MCP server
mcp = FastMCP("AI Sticky Notes")
NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.txt")

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

@mcp.tool()
def delete_note(note: str) -> str:
    """Delete a note from the notes file."""
    ensure_notes_file_exists()
    with open(NOTES_FILE, 'r') as f:
        notes = f.readlines()
    with open(NOTES_FILE, 'w') as f:
        for existing_note in notes:
            if existing_note.strip() != note.strip():
                f.write(existing_note)
    return f"Note deleted: {note}"

@mcp.tool()
def modify_note(old_note: str, new_note: str) -> str:
    """Modify a note in the notes file."""
    ensure_notes_file_exists()
    with open(NOTES_FILE, 'r') as f:
        notes = f.readlines()
    with open(NOTES_FILE, 'w') as f:
        for existing_note in notes:
            if existing_note.strip() == old_note.strip():
                f.write(new_note + "\n")
            else:
                f.write(existing_note)
    return f"Note modified from '{old_note}' to '{new_note}'"

@mcp.tool()
def read_notes()->str:
    """Read all notes from the notes file."""
    ensure_notes_file_exists()
    with open(NOTES_FILE, 'r') as f:
        notes = f.readlines()
    return "Notes:\n" + "".join(notes) if notes else "No notes found."