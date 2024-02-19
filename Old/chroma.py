import os
import sqlite3

# Define the file paths
journal_path = 'e:/OneDrive/Documents/GitHub/WIP/Zara/memories/Journal.txt'
chromadb_path = 'e:/OneDrive/Documents/GitHub/WIP/Zara/chromadb/chromaDB.db'

# Ensure the chromaDB directory exists
os.makedirs(os.path.dirname(chromadb_path), exist_ok=True)

# Connect to the SQLite database (this will create the database if it does not exist)
conn = sqlite3.connect(chromadb_path)
cursor = conn.cursor()

# Create a table to store journal entries if it doesn't exist
cursor.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY,
    date TEXT,
    content TEXT
)""")

# Clear the table to ensure the database will only contain the latest entries
cursor.execute("DELETE FROM journal_entries")

# Open the journal file and read its content
with open(journal_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Splitting the entire content by two newlines, assuming this pattern reliably separates entries
entries_raw = content.strip().split('\n\n')

entries = []
for entry_raw in entries_raw:
    parts = entry_raw.split('\n', 2)  # Split into 3 parts: date, title, and content
    if len(parts) == 2:
        date, content = parts
    else:
        # Handle potential formatting issues or incomplete entries
        print(f"Skipping incomplete entry: {parts[0]}")
        continue

    entries.append((date, content))

# Insert the parsed journal entries into the database
cursor.executemany("INSERT INTO journal_entries (date, content) VALUES (?, ?)", entries)

# Commit changes and close the connection
conn.commit()
conn.close()
