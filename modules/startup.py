import os
from datetime import datetime
import streamlit as st
import time
from modules.profile import update_profile, update_matrix
from modules.journal import write_journal, process_DB_Entries, append_to_chatlog
from modules.faiss import init_FAISS, calculate_similarity
from modules.journal import chromadb_path
from modules.utils import Chatlog_loc, profile_template, matrix_template, chromadb_path, persona_content, User_pro


def startup():
    if "Startup" not in st.session_state:
        os.makedirs(os.path.dirname(chromadb_path), exist_ok=True)
        # Create a placeholder for the startup message
        startup_message = st.empty()
        # Display the startup message
        startup_message.info('Beginning startup', icon=None)
        print(f'Beginning startup')
        start_time = time.time()  # Record the start time
        st.session_state['Startup'] = "done"
        st.session_state['# of entries'] = ""
        update_profile()
        update_matrix()
        write_journal()
        process_DB_Entries()
        init_FAISS()
        # Calculate and print the duration
        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration
        # Wait for 3 seconds
        time.sleep(3)
        # Clear the initial startup message
        startup_message.empty()
        # Optionally, show a new message that the startup has completed, then clear it
        completed_message = st.empty()
        completed_message.info(f'Startup completed in {duration:.2f} seconds, Ready to rock and roll', icon=None)
        print(f'Startup completed in {duration:.2f} seconds, Ready to rock and roll')
        # Wait for another duration before clearing the completed message
        time.sleep(3)
        completed_message.empty()

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
