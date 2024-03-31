import sqlite3
import pandas as pd
import time
import streamlit as st
import openai
from modules.utils import chromadb_path, Chatlog_loc, Journal_loc, Journaler, open_file

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
    startup_message = st.empty()
    startup_message.info('Updating profile', icon=None)
    start_time = time.time()  # Record the start time
    conn = sqlite3.connect(chromadb_path)
    query = "SELECT id, date, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(f"Fetched {len(df)} entries")  # Debug print
    end_time = time.time()  # Record the end time
    duration = end_time - start_time  # Calculate the duration
    startup_message.empty()
    completed_message = st.empty()
    completed_message.info(f'Entries fetched in in {duration:.2f} seconds', icon=None)
    time.sleep(2)
    completed_message.empty()
    print(f'Entries fetched in in {duration:.2f} seconds')
    st.session_state['# of entries'] = df
    st.session_state['journal_entries'] = df
    return df

def process_DB_Entries():
    start_time = time.time()  # Record the start time
    print(f'Processing Jorunal into DB')
    # startup_message = st.empty()
    # startup_message.info('Processing Jorunal into DB', icon=None)
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
    entries = [tuple(entry.split('\n', 1)) for entry in content.strip().split('\n\n') if '\n' in entry]
    cursor.executemany("INSERT INTO journal_entries (date, content) VALUES (?, ?)", entries)

    # Clear the journal file's contents
    with open(Journal_loc, 'w', encoding='utf-8') as file:
        file.write('')

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    end_time = time.time()  # Record the end time
    duration = end_time - start_time  # Calculate the duration
    # startup_message.empty()
    # completed_message = st.empty()
    # completed_message.info(f'Processing complete in {duration:.2f} seconds', icon=None)
    # time.sleep(2)
    # completed_message.empty()
    print(f'Processing complete in {duration:.2f} seconds')

def write_journal():
    print(f"Writing Journal")
    # startup_message = st.empty()
    # startup_message.info('Writing Journal', icon=None)
    Prev_Chatlog = open_file(Chatlog_loc)
    if Prev_Chatlog.strip():  # Check if Prev_Chatlog is not empty
        start_time = time.time()  # Record the start time
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
        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration
        # startup_message.empty()
        # completed_message = st.empty()
        # completed_message.info(f'Journal written in {duration:.2f} seconds', icon=None)
        # time.sleep(2)
        # completed_message.empty()
        print(f'Journal written in {duration:.2f} seconds')
