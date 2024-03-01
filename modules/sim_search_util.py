from modules.utilities import *

model = SentenceTransformer('all-MiniLM-L6-v2')
chromadb_path = os.path.join('chromadb', 'chromaDB.db')
KB_DB_Path = os.path.join('chromadb', 'KB_DB.db')


def create_faiss_index(embeddings):
    # Dimension of embeddings
    d = embeddings.shape[1]
    
    # Creating a FAISS index
    index = faiss.IndexFlatL2(d)  # Using L2 distance for similarity search
    
    # Adding the embeddings to the index
    index.add(embeddings)
    
    return index


def KB_similarity(new_entry_content, entries, similarity_threshold=0.8):
    if len(entries) == 0:  # If no entries in DB, no need to calculate similarity
        return False, None
    # Convert new entry content to embedding
    prompt_embedding = model.encode([new_entry_content])
    # Convert existing entries to embeddings
    entry_embeddings = np.array(model.encode([entry[1] for entry in entries]))
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    # Search the index for the most similar entry
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entry
    # Check if the most similar entry is below the similarity threshold
    if D[0][0] < similarity_threshold:
        return True, entries[I[0][0]]  # Similar entry found
    return False, None  # No similar entry found

def KB_chat_similarity(user_prompt, entries, similarity_threshold=1.5):
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode([entry[1] for entry in entries]))
    
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    
    # Search the index for the most similar entries
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entries
    
    # Ensure the result index is within the DataFrame bounds and similarity threshold is met
    if I.size > 0 and I[0][0] < len(entries) and D[0][0] < similarity_threshold:
        most_similar_entry_index = I[0][0]
        memory = f"{entries.iloc[most_similar_entry_index]['Title']}\n{entries.iloc[most_similar_entry_index]['content']}"
    else:
        memory = "You don't have any relevant memories."
    
    return memory