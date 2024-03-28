import streamlit as st
from dotenv import load_dotenv
import os
import openai
from time import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import sqlite3
# import spacy
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np
import difflib


model = SentenceTransformer('all-MiniLM-L6-v2')
chromadb_path = os.path.join('chromadb', 'chromaDB.db')


st.set_page_config(layout="wide")

def append_date_time_to_chatlog():
        # Adding the current date and time at the top of the chatlog
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
            f.write(profile_template)  # Write initial content

def ensure_usermatrix_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write(matrix_template)  # Write initial content

def ensure_chatlog_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write('')  # Write an empty string
            
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
    print(f"Fetching entries")
    conn = sqlite3.connect(chromadb_path)
    query = "SELECT id, date, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(f"Fetched {len(df)} entries")  # Debug print
    st.session_state['# of entries'] = df
    st.session_state['journal_entries'] = df
    return df

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]  # Assuming embeddings is a 2D numpy array
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def init_FAISS():
    # if 'initialized' not in st.session_state:
        # Fetch or load entries
        entries = fetch_journal_entries() if 'journal_entries' not in st.session_state else st.session_state['journal_entries']
        
        # Generate embeddings for the entries
        # Assuming model is already defined and can process batch inputs
        entries_embeddings = np.array(model.encode(entries['content'].tolist()))
        
        # Create and store FAISS index
        st.session_state['faiss_index'] = create_faiss_index(entries_embeddings)
        
        # Mark the program as initialized
        st.session_state['initialized'] = True
        
def calculate_similarity(user_prompt):
    print(f"Calculating similarity")
    # Ensure the program is initialized
    if 'initialized' not in st.session_state:
        init_FAISS()
    
    # Convert user prompt to embedding
    prompt_embedding = model.encode([user_prompt])
    
    # Access the FAISS index from st.session_state
    index = st.session_state['faiss_index']
    entries = st.session_state['journal_entries']
    
    # Search the index for the most similar entries
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entries
    
    # Process and return the most similar entry details
    if len(I) > 0:
        most_similar_entry_index = I[0][0]
        memory = f"{entries.iloc[most_similar_entry_index]['date']}\n{entries.iloc[most_similar_entry_index]['content']}"
    else:
        memory = "You don't have any relevant memories."
    
    print(f"Most similar entry: {memory}")  # Debug print
    return memory

# def calculate_similarity(user_prompt, entries):
#     print(f"Calculating similarity")
#     # Convert user prompt and entries to embeddings
#     prompt_embedding = model.encode([user_prompt])
#     entry_embeddings = np.array(model.encode(entries['content'].tolist()))
    
#     # Create a FAISS index for the entry embeddings
#     index = create_faiss_index(entry_embeddings)
    
#     # Search the index for the most similar entries
#     D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entries
    
#     # Get the most similar entry details
#     if len(I) > 0:
#         most_similar_entry_index = I[0][0]
#         most_similar_distance = D[0][0]
#         memory = f"{entries.iloc[most_similar_entry_index]['date']}\n{entries.iloc[most_similar_entry_index]['content']}"
#     else:
#         memory = "You don't have any relevent memories."
#     print(f"Most similar entry: {memory}")  # Debug print
#     return memory

def backup_profile():
    profile_temp = open_file(userprofile)
    with open(backup_userprofile, "w") as backupfile:
        backupfile.write(profile_temp)   
def backup_matrix():
    matrix_temp = open_file(User_matrix)
    with open(backup_userprofile, "w") as backupfile:
        backupfile.write(matrix_temp)  
def update_profile():
    print(f"Updating Profile")
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
    print(f"profile updated")
    

def update_matrix():
    print(f"Updating Matrix")
    with open(User_matrix, "r") as file:
        original_data = file.read()
    Update_Person_matrix = [{'role': 'system', 'content': Matrix_writer}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    Matrix_updated, tokens_risk = chatbotGPT4(Update_Person_matrix)   
    # Calculate the number of differences between the original data and the updated data
    diff = difflib.ndiff(original_data, Matrix_updated)
    num_differences = len([d for d in diff if d[0] != ' '])

    # Check if the number of differences exceeds 200
    if num_differences > 200:
        # Restore the original data from a backup file
        with open(backup_user_matrix, "r") as backup_file:
            restored_data = backup_file.read()
        
        # Save the restored data back to the user profile file
        with open(User_matrix, "w") as file:
            file.write(restored_data)
    else:
        # Save the updated data to the user profile file
        with open(User_matrix, "w") as file:
            file.write(Matrix_updated)
    print(f"Matrix updated")

def write_journal():
    print(f"Writing Journal")
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
        print(f"Journal written")

def process_DB_Entries():
        print(f'Processing Jorunal into DB')
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
        print(f'Processing complete')

def timeout_tasks():
    # Check if the 'last_action_timestamp' is set in the session state
    if 'last_action_timestamp' in st.session_state:
        # Calculate the time elapsed since the last action
        elapsed_time = datetime.now() - st.session_state['last_action_timestamp']
        # Check if more than 5 minutes have elapsed
        if elapsed_time > timedelta(minutes=5) and st.session_state.get('has_timeout_run') == 'no':
            update_profile()
            update_matrix()
            write_journal()
            process_DB_Entries()
            init_FAISS()
            # Optionally, you can update the 'last_action_timestamp' to the current time
            st.session_state['last_action_timestamp'] = datetime.now()
            st.session_state['has_timeout_run'] = "yes"
            print("Tasks executed after 5 minutes of inactivity.")
    else:
        # If 'last_action_timestamp' is not set, initialize it to the current time
        st.session_state['last_action_timestamp'] = datetime.now()

#=================================================================#

load_dotenv()

ensure_userprofile_exists(os.path.join('Memories', 'user_profile.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'chatlog.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'user_person_matrix.txt'))
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
User_matrix = os.path.join('Memories', 'user_person_matrix.txt')
Matrix_writer_prompt = os.path.join('system prompts', 'Personality_matrix.md')
backup_userprofile = os.path.join('Memories', 'user_profile_backup.txt')
backup_user_matrix = os.path.join('Memories', 'user_matrix_backup.txt')
profile_template = open_file(os.path.join('modules', 'STARTUP', 'userprofile.txt'))
matrix_template = open_file(os.path.join('modules', 'STARTUP', 'usermatrix.txt'))

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
def main():
    if 'last_action_timestamp' not in st.session_state:
        st.session_state['last_action_timestamp'] = datetime.now()
    if 'has_timeout_run' not in st.session_state:
        st.session_state['has_timeout_run'] = "no"    
    timeout_tasks()
    #============================Startup FUNCTION =====================================#

    if "Startup" not in st.session_state:
        st.session_state['Startup'] = "done"
        st.session_state['# of entries'] = ""
        update_profile()
        update_matrix()
        write_journal()
        process_DB_Entries()
        init_FAISS()
        print(f'Ready')

    #============================EMBEDDING FUNCTION =====================================#

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
        st.session_state['has_timeout_run'] = "no"
        with st.chat_message("user",):
            st.write(prompt)
        time_right_now = "current time:"+"\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # entries = fetch_journal_entries()
        je = st.session_state['# of entries']
        memory = "Memory" + "\n" + calculate_similarity(prompt)
        st.sidebar.write(memory)
        st.sidebar.write(len(je))
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container


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
        
        # Append the latest user and assistant messages to the chatlog file
        append_to_chatlog(f"User: {prompt}")
        append_to_chatlog(f"Assistant: {msg_content}")

        current_Chatlog = open_file(Chatlog_loc)
        if len(current_Chatlog) > 2500: #TODO - I have to change this to a time based function that will split the chatlog into chunks of 2500 char then run each function. I want it to do it when there ahsn't been a response of about 5 min or soemthign so it happens when the user isn't there to experience the slowness
            write_journal()
            append_date_time_to_chatlog()
            update_profile()
            update_matrix()

if __name__ == "__main__":
    main()


