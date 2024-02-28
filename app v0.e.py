import streamlit as st
from dotenv import load_dotenv
import os
import openai
from time import time
from dotenv import load_dotenv
from datetime import datetime
import time
import sqlite3
# import spacy
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np


model = SentenceTransformer('all-MiniLM-L6-v2')
chromadb_path = os.path.join('chromadb', 'chromaDB.db')
KB_DB_Path = os.path.join('chromadb', 'KB_DB.db')

st.set_page_config(layout="wide")
# Adding the current date and time at the top of the chatlog
def append_date_time_to_chatlog():
    with open(Chatlog_loc, "r+") as chatlog_file:
        content = chatlog_file.read()
        chatlog_file.seek(0, 0)
        chatlog_file.write("Chatlog created at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n" + content)

def ensure_userprofile_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write('')  # Write an empty string or initial content

def ensure_Journal_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n" + "I am Zara, I am excited to be helping whoever i am speaking with. I will be poliet but firm with who i am speaking with and trust that my memories are correct.")  # Write an empty string or initial content

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()
    
def chatbotGPT4(conversation, model="gpt-4", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

def chatbotGPT3(conversation, model="gpt-3.5-turbo-0125", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

def response_generator(msg_content):
    for word in msg_content.split():
        yield word + " "
        time.sleep(0.1)

def append_to_chatlog(message):
    # Check if the chatlog file exists, create it if it doesn't
    try:
        open(Chatlog_loc, "r").close()
    except FileNotFoundError:
        open(Chatlog_loc, "w").close()
    
    with open(Chatlog_loc, "a") as chatlog_file:
        chatlog_file.write(message + "\n")


def fetch_journal_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(chromadb_path)
    query = "SELECT id, date, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # print(f"Fetched {len(df)} entries")  # Debug print
    return df

def fetch_KB_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(KB_DB_Path)
    query = "SELECT id, Title, content FROM KB_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # print(f"Fetched {len(df)} entries")  # Debug print
    return df

def create_faiss_index(embeddings):
    # Dimension of embeddings
    d = embeddings.shape[1]
    
    # Creating a FAISS index
    index = faiss.IndexFlatL2(d)  # Using L2 distance for similarity search
    
    # Adding the embeddings to the index
    index.add(embeddings)
    
    return index

def Journal_similarity(user_prompt, entries, similarity_threshold=1.5):
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode(entries['content'].tolist()))
    
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    
    # Search the index for the most similar entries
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entries
    
    # Get the most similar entry details
    if len(I) > 0 and D[0][0] < similarity_threshold:
        most_similar_entry_index = I[0][0]
        most_similar_distance = D[0][0]
        memory = f"{entries.iloc[most_similar_entry_index]['date']}\n{entries.iloc[most_similar_entry_index]['content']}"
    else:
        memory = "You don't have any relevant memories."
    
    return memory

def update_profile():
    Update_user_profile = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    User_profile_updated, tokens_risk = chatbotGPT3(Update_user_profile)   
    with open(userprofile, "w") as file:
        file.write(User_profile_updated)

def update_matrix():
    Update_Person_matrix = [{'role': 'system', 'content': Matrix_writer}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    Matrix_updated, tokens_risk = chatbotGPT4(Update_Person_matrix)   
    with open(User_matrix, "w") as file:
        file.write(Matrix_updated)

def write_journal():
    Prev_Chatlog = open_file(Chatlog_loc)
    if len(Prev_Chatlog) > 50:  # Check if Prev_Chatlog is not empty
        Journal_writer= open_file(Journaler)
        # st.write(Prev_Chatlog)
        Journal = [{'role': 'system', 'content': Journal_writer}, {'role': 'user', 'content': Prev_Chatlog}]
        # st.write(Journal)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=Journal, temperature=0, max_tokens=4000)
        text = response['choices'][0]['message']['content']
        # st.write(Update_Journal)
        Update_Journal = text
        
        try:
            open(Journal_loc, "r").close()
        except FileNotFoundError:
            open(Journal_loc, "w").close()
        
        with open(Journal_loc, "a") as Journal_file:  # Changed mode to "a" for appending to the end
            Journal_file.write("\n" + Update_Journal +"\n")

        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")
    else:
        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")

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

#=================================================================#

load_dotenv()

ensure_userprofile_exists(os.path.join('Memories', 'user_profile.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'chatlog.txt'))
ensure_Journal_exists(os.path.join('Memories', 'Journal.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'scratchpad.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'user_person_matrix.txt'))
openai.api_key = os.getenv("OPENAI_API_KEY")
Update_user = os.path.join('system prompts', 'User_update.md')
Journaler = os.path.join('system prompts', 'Journaler.md')
Chatlog_loc = os.path.join('Memories', 'chatlog.txt')
Journal_loc = os.path.join('Memories', 'Journal.txt')
Persona=os.path.join('Personas', 'Zara.md')
userprofile=os.path.join('Memories', 'user_profile.txt')
portrait_path = os.path.join('Portrait', 'T.png')
Thinker_loc = os.path.join('system prompts', 'Thinker.md')
embed_loc = os.path.join('Memories', 'Journal_embedded.pkl')
User_matrix = os.path.join('Memories', 'user_person_matrix.txt')
Matrix_writer_prompt = os.path.join('system prompts', 'Personality_matrix.md')
KB_writer = os.path.join('system prompts', 'KB_writer.md')
KB_entry_merger = os.path.join('system prompts', 'KB_merger.md')
Scratchpad = os.path.join('Memories', 'scratchpad.txt')


prompt = st.chat_input()
Profile_update = open_file(Update_user)
persona_content = open_file(Persona)
User_pro = open_file(userprofile)
Matrix_writer_content = open_file(Matrix_writer_prompt)
Matrix_content = open_file(User_matrix)
Matrix_writer = Matrix_writer_content + Matrix_content
Content = persona_content + User_pro + Matrix_content
Profile_check = Profile_update+User_pro

os.makedirs(os.path.dirname(chromadb_path), exist_ok=True)

os.makedirs(os.path.dirname(KB_DB_Path), exist_ok=True)
#============================JOURNALING FUNCTION =====================================#

if "Journal" not in st.session_state:
    st.session_state['Journal'] = "done"
    write_KB()

    write_journal()

#============================EMBEDDING FUNCTION =====================================#
if "embed" not in st.session_state:
    st.session_state['embed'] = 'done'
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


    
if "KB_create" not in st.session_state:
    st.session_state['KB_create'] = 'done'
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

if "timestamp" not in st.session_state:
    append_date_time_to_chatlog()
    st.session_state['timestamp'] = 'done'

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if "chat_log" not in st.session_state:
    st.session_state["chat_log"] = ""
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        # For assistant messages, use the custom avatar
        with st.chat_message("assistant", avatar=portrait_path):
            st.write(msg["content"])
    else:
        # For user messages, display as usual
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

#============================CHATBOT FUNCTION =====================================#


if prompt:
    time_right_now = "current time:"+"\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    jorunal_entries = fetch_journal_entries()
    KB_entries = fetch_KB_entries()
    memory = "Journal Entry:" + "\n" + Journal_similarity(prompt, jorunal_entries) + "\n" + "KB entry:" + KB_chat_similarity(prompt, KB_entries)
    st.sidebar.write(memory)

    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user",):
        st.write(prompt)

    # followed by the actual chat messages exchanged in the session.
    system_prompt = {
        "role": "system",
        "content": time_right_now + Content  + memory
    }
    messages_for_api = [system_prompt] + st.session_state.messages
     
    # Call the OpenAI API with the prepared messages, including the hidden system prompt.
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=messages_for_api
    )
    msg_content = response.choices[0].message["content"]
    
    # Display assistant response in chat message container with streamed output
    with st.chat_message("assistant", avatar=portrait_path):
        st.write_stream(response_generator(msg_content))
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": msg_content, })


        # Convert the chat log into a string, store it in the session state.
    chat_log = "<<BEGIN CHATLOG>>" +"\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])+ "<<END CHATLOG>>"
    st.session_state['chat_log'] = chat_log
    
    update_profile()
    update_matrix()

    # Append the latest user and assistant messages to the chatlog file
    append_to_chatlog(f"User: {prompt}")
    append_to_chatlog(f"Assistant: {msg_content}")

    current_Chatlog = open_file(Chatlog_loc)
    if len(current_Chatlog) > 2500:
        write_KB()
        write_journal()
        append_date_time_to_chatlog()



########################## CODE GRAVEYARD DXDXDXDX################
        
# if "KB_create" not in st.session_state:
#     st.session_state['KB_create'] = 'done'
#     # Connect to the SQLite database (this will create the database if it does not exist)
#     conn = sqlite3.connect(KB_DB_Path)
#     cursor = conn.cursor()

#     # Create a table to store journal entries if it doesn't exist
#     cursor.execute("""CREATE TABLE IF NOT EXISTS KB_entries (
#         id INTEGER PRIMARY KEY,
#         Title TEXT,
#         content TEXT
#     )""")


#     # Open the  scratch pad and read its content
#     with open(Scratchpad, 'r', encoding='utf-8') as file:
#         content = file.read()

#     # Splitting the entire content by two newlines, assuming this pattern reliably separates entries
#     entries_raw = content.strip().split('\n\n')

#     # Fetch existing entries from the database to check for similarity
#     cursor.execute("SELECT Title, content FROM KB_entries")
#     existing_entries = cursor.fetchall()

#     for entry_raw in entries_raw:
#         parts = entry_raw.split('\n', 1)
#         if len(parts) == 2:
#             Title, content = parts
#             is_similar, similar_entry = KB_similarity(content, existing_entries)
#             if not is_similar:
#                 # Insert the new, non-similar entry into the database
#                 cursor.execute("INSERT INTO KB_entries (Title, content) VALUES (?, ?)", (Title, content))
#             else:
#                 concatenated_content = f"<Existing KB> {similar_entry['content']} </Existing KB>\n<new KB> {content} </new KB>"
#                 KB_merger= open_file(KB_entry_merger)
#                 # st.write(Prev_Chatlog)
#                 KB_out = [{'role': 'system', 'content': KB_merger}, {'role': 'user', 'content': concatenated_content}]
#                 # st.write(Journal)
#                 response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=KB_out, temperature=0, max_tokens=4000)
#                 text = response['choices'][0]['message']['content']
#                 # st.write(Update_Journal)
#                 KB_merge = text


#     # Commit changes and close the connection
#     conn.commit()
#     conn.close()