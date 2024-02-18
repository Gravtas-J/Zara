import streamlit as st
from dotenv import load_dotenv
import os
import openai
from time import time
from dotenv import load_dotenv
from datetime import datetime
import time
import sqlite3
import spacy
import pandas as pd


nlp = spacy.load("en_core_web_md")  # Make sure to use a model with word vectors
chromadb_path = os.path.join('chromadb', 'chromaDB.db')


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
            f.write('Journal Start')  # Write an empty string or initial content

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

def calculate_similarity(user_prompt, entries):
    # """Calculate similarity between user prompt and journal entries using spaCy and return top result."""
    # if entries.empty:
    #     print("Entries dataframe is empty")  # Debug print
    #     return ""
    
    # Calculate similarity
    prompt_doc = nlp(user_prompt)
    entries['similarity'] = entries['content'].apply(lambda x: prompt_doc.similarity(nlp(x)))
    
    # Sort the entries based on similarity
    sorted_entries = entries.sort_values(by='similarity', ascending=False)
    
    # # Debug print to check similarities of top entries
    print(sorted_entries[['content', 'similarity']].head()) 
    
    # Extract the content of the most similar entry
    if not sorted_entries.empty:
        memory = sorted_entries.iloc[0]['content']
    else:
        memory = ""
    
    return memory



#=================================================================#

load_dotenv()

ensure_userprofile_exists(os.path.join('Memories', 'user_profile.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'chatlog.txt'))
ensure_Journal_exists(os.path.join('Memories', 'Journal.txt'))
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





prompt = st.chat_input()
Profile_update = open_file(Update_user)
persona_content = open_file(Persona)
User_pro = open_file(userprofile)
Content = persona_content + User_pro
Profile_check = Profile_update+User_pro


os.makedirs(os.path.dirname(chromadb_path), exist_ok=True)
#============================JOURNALING FUNCTION =====================================#

if "Journal" not in st.session_state:
    st.session_state['Journal'] = "done"
    Prev_Chatlog = open_file(Chatlog_loc)
    if Prev_Chatlog.strip():  # Check if Prev_Chatlog is not empty
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
            Journal_file.write("\n" + Update_Journal)

        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")

#============================EMBEDDING FUNCTION =====================================#
if "embed" not in st.session_state:
    st.session_state['Journal'] = 'done'
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
        parts = entry_raw.split('\n', 2)  # Split into 3 parts: date, title, and content
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
    # print("Search button pressed")  # Debug print
    entries = fetch_journal_entries()
    memory = calculate_similarity(prompt, entries)
    # if not similar_entries.empty:
    #     print(f"Displaying {len(similar_entries)} similar entries")  # Debug print
    #     for _, row in similar_entries.iterrows():
    #         st.write(f"**Date:** {row['date']}")
    #         st.write(f"**Content:** {row['content']}")
    # else:
    #     st.write("No entries found.")
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user",):
        st.write(prompt)

    # followed by the actual chat messages exchanged in the session.
    system_prompt = {
        "role": "system",
        "content": Content  + memory
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
    
    Update_user_profile = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    User_profile_updated, tokens_risk = chatbotGPT4(Update_user_profile)   
    with open(userprofile, "w") as file:
        file.write(User_profile_updated)

    # Append the latest user and assistant messages to the chatlog file
    append_to_chatlog(f"User: {prompt}")
    append_to_chatlog(f"Assistant: {msg_content}")



