import streamlit as st
import sqlite3
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np
import os

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define the path to the SQLite database
chromadb_path = os.path.join('chromadb', 'chromaDB.db')

def fetch_journal_entries():
    """Fetch all journal entries from the database."""
    # Connect to the SQLite database
    conn = sqlite3.connect(chromadb_path)
    # SQL query to select all entries
    query = "SELECT id, date, content FROM journal_entries"
    # Execute the query and convert to DataFrame
    df = pd.read_sql_query(query, conn)
    # Close the database connection
    conn.close()
    # Debug print to check the number of fetched entries
    print(f"Fetched {len(df)} entries")
    return df

def create_faiss_index(embeddings):
    """Create a FAISS index for similarity search."""
    # Dimension of the embeddings
    d = embeddings.shape[1]
    # Creating a FAISS index using L2 distance
    index = faiss.IndexFlatL2(d)
    # Adding the embeddings to the index
    index.add(embeddings)
    return index

def calculate_similarity_close(user_prompt, entries, threshold=1.5):
    """Calculate similarity with a closeness threshold."""
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode(entries['content'].tolist()))
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    # Search the index for the top 5 most similar entries
    D, I = index.search(prompt_embedding, 5)
    # Filter results based on the threshold
    filtered_entries = []
    for i in range(0, len(I[0])):
        distance = D[0][i]
        if distance <= threshold:
            idx = I[0][i]
            filtered_entries.append({
                'date': entries.iloc[idx]['date'],
                'content': entries.iloc[idx]['content'],
                'similarity_score': distance
            })
    # Convert to DataFrame for easier handling
    return pd.DataFrame(filtered_entries) if filtered_entries else pd.DataFrame()

def calculate_similarity(user_prompt, entries):
    """Calculate similarity without a closeness threshold."""
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode(entries['content'].tolist()))
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    # Search the index for the top 5 most similar entries
    D, I = index.search(prompt_embedding, 5)
    # Prepare the results
    similar_entries = []
    for i in range(0, len(I[0])):
        idx = I[0][i]
        distance = D[0][i]
        similar_entries.append({
            'date': entries.iloc[idx]['date'],
            'content': entries.iloc[idx]['content'],
            'similarity_score': distance
        })
    # Convert to DataFrame for easier handling
    return pd.DataFrame(similar_entries)

def show_all_entries():
    """Display all journal entries in the sidebar."""
    entries = fetch_journal_entries()
    if not entries.empty:
        st.sidebar.write("All Journal Entries")
        for _, row in entries.iterrows():
            st.sidebar.write(f"**ID:** {row['id']}, **Date:** {row['date']}, **Content:** {row['content']}")

# Streamlit UI setup
st.title('Journal Entry Similarity Search')

# User input for search prompt
user_prompt = st.text_area("Enter your search prompt:", height=100)

# Radio buttons for method selection
st.sidebar.write("Calculate similarity just returns a sorted list of entries. Calculate Similarity Close applies a threshold to only return sufficently close entries")
method = st.sidebar.radio("Choose a similarity calculation method:", ('Calculate Similarity', 'Calculate Similarity Close'))

# Search button
search_button = st.button("Search")

# Show all entries button in the sidebar
st.sidebar.button("Show All Entries", on_click=show_all_entries)

# Process search on button click
if search_button and user_prompt:
    entries = fetch_journal_entries()
    if method == 'Calculate Similarity':
        similar_entries = calculate_similarity(user_prompt, entries)
    else:
        similar_entries = calculate_similarity_close(user_prompt, entries, threshold=1.5)
    
    # Display the search results
    if not similar_entries.empty:
        for _, row in similar_entries.iterrows():
            st.write(f"**Date:** {row['date']}, **Similarity Score:** {row['similarity_score']}")
            st.write(f"**Content:** {row['content']}")
    else:
        st.write("No entries found.")
