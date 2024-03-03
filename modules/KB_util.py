from modules.utilities import *

KB_DB_Path = os.path.join('chromadb', 'KB_DB.db')
model = SentenceTransformer('all-MiniLM-L6-v2')

def write_KB():
    Prev_Chatlog = open_file(Chatlog_loc)
    if len(Prev_Chatlog) > 50:   # Check if Prev_Chatlog is not empty
        KB_entry_writer= open_file(KB_writer)
        # st.write(Prev_Chatlog)
        KB_info = [{'role': 'system', 'content': KB_entry_writer}, {'role': 'user', 'content': Prev_Chatlog}]
        # st.write(Journal)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=KB_info, temperature=0, max_tokens=4000)
        text = response['choices'][0]['message']['content']
        # st.write(Update_Journal)
        KB_temp = text
        
        try:
            open(Scratchpad, "r").close()
        except FileNotFoundError:
            open(Scratchpad, "w").close()
        
        with open(Scratchpad, "a") as Scratchpad_file:  # Changed mode to "a" for appending to the end
            Scratchpad_file.write(KB_temp +"\n\n")

def fetch_KB_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(KB_DB_Path)
    query = "SELECT id, Title, content FROM KB_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # print(f"Fetched {len(df)} entries")  # Debug print
    return df

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

def KB_similarity(new_entry_content, entries, similarity_threshold=0.8):
    if len(entries) == 0:  # If no entries in DB, no need to calculate similarity
        return False, None
    # Convert new entry content to embedding
    prompt_embedding = model.encode([new_entry_content])
    # Convert existing entries to embeddings
    entry_embeddings = np.array(model.encode([entry[1] for entry in entries]))
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    # Search the index for the most similar entry
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entry
    # Check if the most similar entry is below the similarity threshold
    if D[0][0] < similarity_threshold:
        return True, entries[I[0][0]]  # Similar entry found
    return False, None  # No similar entry found

def KB_chat_similarity(user_prompt, entries, similarity_threshold=1.5):
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode([entry[1] for entry in entries]))
    
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    
    # Search the index for the most similar entries
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entries
    
    # Ensure the result index is within the DataFrame bounds and similarity threshold is met
    if I.size > 0 and I[0][0] < len(entries) and D[0][0] < similarity_threshold:
        most_similar_entry_index = I[0][0]
        memory = f"{entries.iloc[most_similar_entry_index]['Title']}\n{entries.iloc[most_similar_entry_index]['content']}"
    else:
        memory = "You don't have any relevant memories."
    
    return memory