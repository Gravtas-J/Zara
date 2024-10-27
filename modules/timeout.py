from datetime import datetime, timedelta
from modules.profile_OLL import update_profile, update_matrix
from modules.journal_OLL import write_journal, process_DB_Entries
from modules.faiss import init_FAISS
import streamlit as st

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
