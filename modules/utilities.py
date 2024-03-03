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
from modules.sim_search_util import *

def GPT4(conversation, model="gpt-4", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

def GPT3(conversation, model="gpt-3.5-turbo-0125", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

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

Update_user = os.path.join('system prompts', 'User_update.md')
Journaler = os.path.join('system prompts', 'Journaler.md')
Chatlog_loc = os.path.join('Memories', 'chatlog.txt')
Journal_loc = os.path.join('Memories', 'Journal.txt')
Persona=os.path.join('Personas', 'Zara.md')
userprofile=os.path.join('Memories', 'user_profile.txt')
portrait_path = os.path.join('Portrait', 'T.png')
Thinker = open_file(os.path.join('system prompts', 'Thinker.md'))
embed_loc = os.path.join('Memories', 'Journal_embedded.pkl')
User_matrix = os.path.join('Memories', 'user_person_matrix.txt')
Matrix_writer_prompt = os.path.join('system prompts', 'Personality_matrix.md')
KB_writer = os.path.join('system prompts', 'KB_writer.md')
KB_entry_merger = os.path.join('system prompts', 'KB_merger.md')
Scratchpad = os.path.join('Memories', 'scratchpad.txt')
backup_userprofile = os.path.join('Memories', 'user_profile_backup.txt')

prompt = st.chat_input()
Profile_update = open_file(Update_user)
persona_content = open_file(Persona)
User_pro = open_file(userprofile)
Matrix_writer_content = open_file(Matrix_writer_prompt)
Matrix_content = open_file(User_matrix)
Matrix_writer = Matrix_writer_content + Matrix_content
Content = persona_content + User_pro + Matrix_content 
Profile_check = Profile_update+User_pro


