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
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np


model = SentenceTransformer('all-MiniLM-L6-v2')
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

def create_faiss_index(embeddings):
    # Dimension of embeddings
    d = embeddings.shape[1]
    
    # Creating a FAISS index
    index = faiss.IndexFlatL2(d)  # Using L2 distance for similarity search
    
    # Adding the embeddings to the index
    index.add(embeddings)
    
    return index

def calculate_similarity(user_prompt, entries):
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode(entries['content'].tolist()))
    
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    
    # Search the index for the most similar entries
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entries
    
    # Get the most similar entry details
    if len(I) > 0:
        most_similar_entry_index = I[0][0]
        most_similar_distance = D[0][0]
        memory = f"{entries.iloc[most_similar_entry_index]['date']}\n{entries.iloc[most_similar_entry_index]['content']}"
    else:
        memory = ""
    
    return memory

def update_profile():
    chatlog = st.session_state.get('chat_log', '')
    if len(chatlog) > 1500:
        # Use .find() method to find the index of a character
        trim_index = chatlog.find('}', 0, 1500) + 1
        Update_user_profile = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': chatlog[:trim_index]}]
        User_profile_updated, tokens_risk = chatbotGPT3(Update_user_profile)   
        with open(userprofile, "w") as file:
            file.write(User_profile_updated)
    else:
        Update_user_profile = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
        User_profile_updated, tokens_risk = chatbotGPT3(Update_user_profile)   
        with open(userprofile, "w") as file:
            file.write(User_profile_updated)

def write_journal():
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
            Journal_file.write("\n" + Update_Journal +"\n")

        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")


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
    write_journal()

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
    time_right_now = "current time:"+"\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entries = fetch_journal_entries()
    memory = "Memory" + "\n" + calculate_similarity(prompt, entries)
    st.sidebar.write(memory)
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
        "content": time_right_now + Content  + memory
    }
    messages_for_api = [system_prompt] + st.session_state.messages
     
    # Call the OpenAI API with the prepared messages, including the hidden system prompt.
    response = openai.ChatCompletion.create(
        model="gpt-4",
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

    # Append the latest user and assistant messages to the chatlog file
    append_to_chatlog(f"User: {prompt}")
    append_to_chatlog(f"Assistant: {msg_content}")
    current_Chatlog = open_file(Chatlog_loc)
    if len(current_Chatlog) > 2500:
        write_journal()
        append_date_time_to_chatlog()



