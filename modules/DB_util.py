from modules.utilities import *



def merge_with_AI(existing_content, new_content):
    # Prepare the prompt for the AI
    KB_out = [
        {'role': 'system', 'content': 'Please merge the following two KB entries into a single, coherent entry:'},
        {'role': 'user', 'content': f'<Existing KB> {existing_content} </Existing KB>\n<new KB> {new_content} </new KB>'}
    ]
    
    # Call OpenAI API for merging
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=KB_out, 
        temperature=0,  # Adjust temperature as needed for creativity vs accuracy
        max_tokens=4000  # Adjust based on expected length of merged content
    )
    
    # Extract merged content from response
    merged_content = response.choices[0].message.content
    return merged_content

def split_content_with_AI(merged_content):
    # Prepare the prompt for the AI to split the content
    prompt = "Please split the following content into two distinct, coherent parts:"
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': merged_content}
    ]

    # Call OpenAI API for splitting
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,  # Adjust temperature as needed
        max_tokens=1024  # Adjust based on expected length
    )

    # Assuming the AI returns two parts separated by a specific delimiter, e.g., "\n\n"
    parts = response.choices[0].message.content.split("\n\n", 1)
    if len(parts) < 2:
        # Fallback in case splitting didn't work as expected
        parts = [merged_content[:len(merged_content)//2], merged_content[len(merged_content)//2:]]

    return parts[0], parts[1]

def process_journal_entries(chromadb_path, Journal_loc):
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
    with open(Journal_loc, 'r', encoding='utf-8') as file:
        content = file.read()

    # Splitting the entire content by two newlines, assuming this pattern reliably separates entries
    entries_raw = content.strip().split('\n\n')

    entries = []
    for entry_raw in entries_raw:
        parts = entry_raw.split('\n', 2)  # Split into 2 parts: date and content
        if len(parts) == 2:
            date, content = parts
        else:
            # Handle potential formatting issues or incomplete entries
            # print(f"Skipping incomplete entry: {parts[0]}")
            continue

        entries.append((date, content))

    # Insert the parsed journal entries into the database
    cursor.executemany("INSERT INTO journal_entries (date, content) VALUES (?, ?)", entries)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def process_entries(KB_DB_Path, Scratchpad):
    conn = sqlite3.connect(KB_DB_Path)  # Ensure this path is correctly specified
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS KB_entries (
        id INTEGER PRIMARY KEY,
        Title TEXT,
        content TEXT
    )""")

    # Check if Scratchpad file exists and has content
    if os.path.exists(Scratchpad) and os.path.getsize(Scratchpad) > 0:
        with open(Scratchpad, 'r', encoding='utf-8') as file:
            content = file.read()

        entries_raw = content.strip().split('\n\n')

        cursor.execute("SELECT Title, content FROM KB_entries")
        existing_entries = cursor.fetchall()

        for entry_raw in entries_raw:
            parts = entry_raw.split('\n', 1)
            if len(parts) == 2:
                Title, content = parts
                is_similar, similar_entry = KB_similarity(content, existing_entries)

                if not is_similar:
                    cursor.execute("INSERT INTO KB_entries (Title, content) VALUES (?, ?)", (Title, content))
                else:
                    merged_content = merge_with_AI(similar_entry[1], content)
                    if len(merged_content) > 2000:
                        part1, part2 = split_content_with_AI(merged_content)
                        cursor.execute("INSERT INTO KB_entries (Title, content) VALUES (?, ?)", (Title + " Part 1", part1))
                        cursor.execute("INSERT INTO KB_entries (Title, content) VALUES (?, ?)", (Title + " Part 2", part2))
                    else:
                        cursor.execute("UPDATE KB_entries SET content = ? WHERE Title = ?", (merged_content, similar_entry[0]))
            else:
                continue
    
    with open(Scratchpad, "w", encoding='utf-8') as Scratchpad_file:
        Scratchpad_file.write("")

    conn.commit()
    conn.close()

