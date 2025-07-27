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
        notes = f.read().strip()
    return notes or "No notes found."

@mcp.resource("notes://latest")
def get_latest_notes() -> str:
    """Get the latest notes."""
    ensure_notes_file_exists()
    with open(NOTES_FILE, 'r') as f:
        notes = f.readlines()
    return "Latest Notes:\n" + "".join(notes) if notes else "No notes found."

@mcp.prompt()
def note_summary_prompt()->str:
    """
    Generate a summary of the notes.
    
    Returns:

      str: A prompt string that includes summary of all the notes and asks for summary.
           If no notes exist, a message will be shown indicating that.
    """
    ensure_notes_file_exists()
    with open(NOTES_FILE, 'r') as f:
        notes = f.read().strip()
    if not notes:
        return "No notes found. Please add some notes first."
    summary = "Here are your notes:\n" + "".join(notes)
    return f"{summary}\n\nPlease summarize these notes."