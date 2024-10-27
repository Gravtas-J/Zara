import os
from datetime import datetime
import streamlit as st
import time
from modules.profile_OLL import update_profile, update_matrix
from modules.journal_OLL import write_journal, process_DB_Entries
from modules.faiss import init_FAISS
from modules.journal import chromadb_path
from modules.utils import Chatlog_loc, profile_template, matrix_template, chromadb_path, persona_content, User_pro



def init_states():
    if "timestamp" not in st.session_state:
        append_date_time_to_chatlog()
        st.session_state['timestamp'] = 'done'
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if "chat_log" not in st.session_state:
        st.session_state["chat_log"] = ""
    if 'last_action_timestamp' not in st.session_state:
        st.session_state['last_action_timestamp'] = datetime.now()
    if 'has_timeout_run' not in st.session_state:
        st.session_state['has_timeout_run'] = "yes"

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



