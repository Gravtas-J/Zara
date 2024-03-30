import faiss
import numpy as np
import time
from sentence_transformers import SentenceTransformer, util
import streamlit as st
from modules.journal import fetch_journal_entries

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]  # Assuming embeddings is a 2D numpy array
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def init_FAISS():
        start_time = time.time()  # Record the start time
    # if 'initialized' not in st.session_state:
        # Fetch or load entries
        entries = fetch_journal_entries() if 'journal_entries' not in st.session_state else st.session_state['journal_entries']
        
        # Generate embeddings for the entries
        entries_embeddings = np.array(model.encode(entries['content'].tolist()))
        
        # Create and store FAISS index
        st.session_state['faiss_index'] = create_faiss_index(entries_embeddings)
        
        # Mark the program as initialized
        st.session_state['initialized'] = True
        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration
        print(f'FAISS initalised in {duration:.2f} seconds')

def calculate_similarity(user_prompt):
    print(f"Calculating similarity")
    start_time = time.time()  # Record the start time
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
    end_time = time.time()  # Record the end time
    duration = end_time - start_time  # Calculate the duration
    print(f'Processing complete in {duration:.2f} seconds')
    return memory
