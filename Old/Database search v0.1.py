
import streamlit as st
import sqlite3
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer, util
import numpy as np
import os

model = SentenceTransformer('all-MiniLM-L6-v2')
chromadb_path = os.path.join('chromadb', 'chromaDB.db')

# Define the path to your SQLite database
db_path = 'e:/OneDrive/Documents/GitHub/WIP/Zara/chromadb/chromaDB.db'

def fetch_journal_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(chromadb_path)
    query = "SELECT id, date, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(f"Fetched {len(df)} entries")  # Debug print
    return df

def create_faiss_index(embeddings):
    # Dimension of embeddings
    d = embeddings.shape[1]
    
    # Creating a FAISS index
    index = faiss.IndexFlatL2(d)  # Using L2 distance for similarity search
    
    # Adding the embeddings to the index
    index.add(embeddings)
    
    return index
def calculate_similarity(user_prompt, entries, threshold=1.5):
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode(entries['content'].tolist()))
    
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    
    # Search the index for the top 5 most similar entries
    D, I = index.search(prompt_embedding, 5)  # Search for the top 5 closest entries
    
    # Filter results based on the threshold
    filtered_entries = []
    for i in range(0, len(I[0])):
        distance = D[0][i]  # Similarity score (distance)
        if distance <= threshold:  # Check if distance is within the threshold
            idx = I[0][i]  # Index of the similar entry
            filtered_entries.append({
                'date': entries.iloc[idx]['date'],
                'content': entries.iloc[idx]['content'],
                'similarity_score': distance
            })
    
    # Convert to DataFrame for easier handling
    if filtered_entries:
        similar_entries_df = pd.DataFrame(filtered_entries)
    else:
        similar_entries_df = pd.DataFrame()  # Return an empty DataFrame if no entries meet the criteria
    
    return similar_entries_df



def show_all_entries():
    """Display all journal entries."""
    entries = fetch_journal_entries()
    if not entries.empty:
        st.sidebar.write("All Journal Entries")
        for _, row in entries.iterrows():
            st.sidebar.write(f"**ID:** {row['id']}, **Date:** {row['date']}, **Content:** {row['content']}")


# Streamlit UI
st.title('Journal Entry Similarity Search')

user_prompt = st.text_area("Enter your search prompt:", height=100)
search_button = st.button("Search")
st.sidebar.button("Show All Entries", on_click=show_all_entries)
if search_button and user_prompt:
    entries = fetch_journal_entries()
    similar_entries = calculate_similarity(user_prompt, entries)
    if not similar_entries.empty:
        for _, row in similar_entries.iterrows():
            st.write(f"**Date:** {row['date']}, **Similarity Score:** {row['similarity_score']}")
            st.write(f"**Content:** {row['content']}")
    else:
        st.write("No entries found.")
