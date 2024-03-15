# from modules.utilities import *
# from modules.Generatives import *
import streamlit as st
from dotenv import load_dotenv
import os
import openai
from time import time
from dotenv import load_dotenv
from datetime import datetime
import time
import sqlite3
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np
import difflib



model = SentenceTransformer('all-MiniLM-L6-v2')
chromadb_path = os.path.join('chromadb', 'chromaDB.db')


st.set_page_config(layout="wide")

# Basic Utilities 
# Adding the current date and time at the top of the chatlog
def append_date_time_to_chatlog():
    with open(Chatlog_loc, "r+") as chatlog_file:
        content = chatlog_file.read()
        chatlog_file.seek(0, 0)
        chatlog_file.write("Chatlog created at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n" + content)

def timestamp():
    Prev_Chatlog = open_file(Chatlog_loc)
    if len(Prev_Chatlog) < 1:  # Check if Prev_Chatlog is not empty
        append_date_time_to_chatlog()


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


# Generative functions

def assessor():
    # Prepare the data to be sent to the profiling module
    update_data = [{'role': 'system', 'content': Assessment_full}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    
    # Send the user profile data to the profiling module and get the response
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=update_data, temperature=0, max_tokens=4000)
    update_assessment = response['choices'][0]['message']['content']
    # update_assessment, tokens_risk = GPT3(update_data)
    with open(cb_assess_loc, "w") as file:
        file.write(update_assessment + "\n")

def update_profile():
    # Read the original user profile data from the file
    with open(userprofile, "r") as file:
        original_data = file.read()

    # Prepare the data to be sent to the profiling module
    update_data = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=update_data, temperature=0, max_tokens=4000)
    User_profile_updated = response['choices'][0]['message']['content']
    # Send the user profile data to the profiling module and get the response
    # User_profile_updated, tokens_risk = GPT3(update_data)

    # Calculate the number of differences between the original data and the updated data
    diff = difflib.ndiff(original_data, User_profile_updated)
    num_differences = len([d for d in diff if d[0] != ' '])

    # Check if the number of differences exceeds 200
    if num_differences > 200:
        # Restore the original data from a backup file
        with open(backup_userprofile, "r") as backup_file:
            restored_data = backup_file.read()
        
        # Save the restored data back to the user profile file
        with open(userprofile, "w") as file:
            file.write(restored_data)
    else:
        # Save the updated data to the user profile file
        with open(userprofile, "w") as file:
            file.write(User_profile_updated)

def backup_profile():
    profile_temp = open_file(userprofile)
    with open(backup_userprofile, "w") as backupfile:
        backupfile.write(profile_temp)   

def update_matrix():
    Update_Person_matrix = [{'role': 'system', 'content': Matrix_writer}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=Update_Person_matrix, temperature=0, max_tokens=4000)
    Matrix_updated = response['choices'][0]['message']['content']
    # Matrix_updated, tokens_risk = GPT3(Update_Person_matrix)   
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
        Update_Journal = response['choices'][0]['message']['content']
        # st.write(Update_Journal)        
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


# DB functions

def fetch_journal_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(chromadb_path)
    query = "SELECT id, date, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # print(f"Fetched {len(df)} entries")  # Debug print
    return df


# Retrieval functions 

def process_journal_entries():
    # Connect to the SQLite database (this will create the database if it does not exist)
    conn = sqlite3.connect(chromadb_path)
    cursor = conn.cursor()
    # # Create a table to store journal entries if it doesn't exist
    cursor.execute("""CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY,
        date TEXT,
        content TEXT
    )""")
    # Open the journal file and read its content
    with open(Journal_loc, 'r', encoding='utf-8') as file:
        content = file.read()

    # Append the journal file's content to the journal_entries table
    # Assuming each entry is separated by two newlines and contains a date and content separated by a newline
    entries = [tuple(entry.split('\n', 1)) for entry in content.strip().split('\n\n') if '\n' in entry]
    cursor.executemany("INSERT INTO journal_entries (date, content) VALUES (?, ?)", entries)

    # Clear the journal file's contents
    with open(Journal_loc, 'w', encoding='utf-8') as file:
        file.write('')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

def create_faiss_index(embeddings):
    # Dimension of embeddings
    d = embeddings.shape[1]
    
    # Creating a FAISS index
    index = faiss.IndexFlatL2(d)  # Using L2 distance for similarity search
    
    # Adding the embeddings to the index
    index.add(embeddings)
    
    return index

def calculate_similarity(user_prompt, entries, similarity_threshold=1.5):
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



#=================================================================#

load_dotenv()
ensure_userprofile_exists(os.path.join('Memories', 'user_profile.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'chatlog.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'user_person_matrix.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'CB_assess.txt'))
ensure_Journal_exists(os.path.join('Memories', 'Journal.txt'))
openai.api_key = os.getenv("OPENAI_API_KEY")
Journaler = os.path.join('system prompts', 'Journaler.md')
Chatlog_loc = os.path.join('Memories', 'chatlog.txt')
Journal_loc = os.path.join('Memories', 'Journal.txt')
userprofile=os.path.join('Memories', 'user_profile.txt')
portrait_path = os.path.join('Portrait', 'T.png')
Thinker_loc = os.path.join('system prompts', 'Thinker.md')
User_matrix = os.path.join('Memories', 'user_person_matrix.txt')
backup_userprofile = os.path.join('Memories', 'user_profile_backup.txt')
cb_assess_loc =  os.path.join('Memories', 'CB_assess.txt')
CB_assess = open_file((os.path.join('Memories', 'CB_assess.txt')))
assessor_loc = os.path.join('system prompts', 'assessor.md')
assess_content = open_file(assessor_loc)
Assessment_full = assess_content + CB_assess

prompt = st.chat_input(key="propmt")
Profile_update = os.path.join('system prompts', 'User_update.md')
persona_content = os.path.join('Personas', 'Zara.md')
User_pro = open_file(userprofile)
Matrix_writer_content = open_file(os.path.join('system prompts', 'Personality_matrix.md'))
Matrix_content = open_file(os.path.join('Memories', 'user_person_matrix.txt'))
Matrix_writer = Matrix_writer_content + Matrix_content
Content = persona_content + User_pro + Matrix_content
Profile_check = Profile_update+User_pro

#============================//Startup Function\\=====================================#

if "Startup" not in st.session_state:
    os.makedirs(os.path.dirname(chromadb_path), exist_ok=True)

    st.session_state['Startup'] = "done"
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'chat_log' not in st.session_state:
        st.session_state["chat_log"] = ""
    backup_profile()
    write_journal()
    timestamp()
    process_journal_entries()

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        # For assistant messages, use the custom avatar
        with st.chat_message("assistant", avatar=portrait_path):
            st.write(msg["content"])
    else:
        # For user messages, display as usual
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

#============================//CHATBOT FUNCTION\\=====================================#

if prompt:
    time_right_now = "current time:"+"\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entries = fetch_journal_entries()
    memory = "Memory" + "\n" + calculate_similarity(prompt, entries)
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
    assessor()

    # Append the latest user and assistant messages to the chatlog file
    append_to_chatlog(f"User: {prompt}")
    append_to_chatlog(f"Assistant: {msg_content}")

    current_Chatlog = open_file(Chatlog_loc)
    if len(current_Chatlog) > 2500:
        write_journal()
        append_date_time_to_chatlog()