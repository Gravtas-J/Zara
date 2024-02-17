# import streamlit as st
# import sqlite3
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# # Define the path to your SQLite database
# db_path = 'e:/OneDrive/Documents/GitHub/WIP/Zara/chromadb/chromaDB.db'

# def fetch_journal_entries():
#     """Fetch all journal entries from the database."""
#     conn = sqlite3.connect(db_path)
#     query = "SELECT id, date, title, content FROM journal_entries"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df

# def calculate_similarity(user_prompt, entries):
#     """Calculate similarity between user prompt and journal entries."""
#     if entries.empty:
#         return pd.DataFrame()
#     tfidf_vectorizer = TfidfVectorizer()
#     # Concatenate the user prompt with the entries' content
#     all_texts = entries['content'].tolist() + [user_prompt]
#     tfidf_matrix = tfidf_vectorizer.fit_transform(all_texts)
#     cosine_sim = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
#     entries['similarity'] = cosine_sim[0]
#     return entries.sort_values(by='similarity', ascending=False)


# # Streamlit UI
# st.title('Journal Entry Similarity Search')

# user_prompt = st.text_area("Enter your search prompt:", height=100)
# search_button = st.button("Search")

# if search_button and user_prompt:
#     entries = fetch_journal_entries()
#     similar_entries = calculate_similarity(user_prompt, entries)
#     if not similar_entries.empty:
#         for _, row in similar_entries.iterrows():
#             # st.write(f"### {row['title']}")
#             st.write(f"**Date:** {row['date']}")
#             st.write(f"**Content:** {row['content']}")
#             # st.write(f"**Similarity Score:** {row['similarity']:.4f}")
#             # st.write("---")
#     else:
#         st.write("No entries found.")


import streamlit as st
import sqlite3
import pandas as pd
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_md")  # Make sure to use a model with word vectors

# Define the path to your SQLite database
db_path = 'e:/OneDrive/Documents/GitHub/WIP/Zara/chromadb/chromaDB.db'

def fetch_journal_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(db_path)
    query = "SELECT id, date, title, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(f"Fetched {len(df)} entries")  # Debug print
    return df

def calculate_similarity(user_prompt, entries):
    """Calculate similarity between user prompt and journal entries using spaCy."""
    if entries.empty:
        print("Entries dataframe is empty")  # Debug print
        return pd.DataFrame()
    prompt_doc = nlp(user_prompt)
    entries['similarity'] = entries['content'].apply(lambda x: prompt_doc.similarity(nlp(x)))
    print(entries[['content', 'similarity']].head())  # Debug print to check similarities
    return entries.sort_values(by='similarity', ascending=False)

# Streamlit UI
st.title('Journal Entry Similarity Search')

user_prompt = st.text_area("Enter your search prompt:", height=100)
search_button = st.button("Search")

if search_button and user_prompt:
    print("Search button pressed")  # Debug print
    entries = fetch_journal_entries()
    similar_entries = calculate_similarity(user_prompt, entries)
    if not similar_entries.empty:
        print(f"Displaying {len(similar_entries)} similar entries")  # Debug print
        for _, row in similar_entries.iterrows():
            st.write(f"**Date:** {row['date']}")
            st.write(f"**Content:** {row['content']}")
    else:
        st.write("No entries found.")