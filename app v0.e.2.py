from modules.utilities import *
from modules.DB_util import *
from modules.GPTs import *

model = SentenceTransformer('all-MiniLM-L6-v2')
chromadb_path = os.path.join('chromadb', 'chromaDB.db')
KB_DB_Path = os.path.join('chromadb', 'KB_DB.db')

st.set_page_config(layout="wide")
# Adding the current date and time at the top of the chatlog
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

def response_generator(msg_content):
    for word in msg_content.split():
        yield word + " "
        time.sleep(0.1)

def append_to_chatlog(message):
    # Check if the chatlog file exists, create it if it doesn't
    try:
        open(Chatlog_loc, "r").close()
    except FileNotFoundError:
        open(Chatlog_loc, "w").close()
    
    with open(Chatlog_loc, "a") as chatlog_file:
        chatlog_file.write(message + "\n")

def fetch_journal_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(chromadb_path)
    query = "SELECT id, date, content FROM journal_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # print(f"Fetched {len(df)} entries")  # Debug print
    return df

def fetch_KB_entries():
    """Fetch all journal entries from the database."""
    conn = sqlite3.connect(KB_DB_Path)
    query = "SELECT id, Title, content FROM KB_entries"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # print(f"Fetched {len(df)} entries")  # Debug print
    return df

def Journal_similarity(user_prompt, entries, similarity_threshold=1.5):
    # Convert user prompt and entries to embeddings
    prompt_embedding = model.encode([user_prompt])
    entry_embeddings = np.array(model.encode(entries['content'].tolist()))
    
    # Create a FAISS index for the entry embeddings
    index = create_faiss_index(entry_embeddings)
    
    # Search the index for the most similar entries
    D, I = index.search(prompt_embedding, 1)  # Search for the top 1 closest entries
    
    # Get the most similar entry details
    if len(I) > 0 and D[0][0] < similarity_threshold:
        most_similar_entry_index = I[0][0]
        most_similar_distance = D[0][0]
        memory = f"{entries.iloc[most_similar_entry_index]['date']}\n{entries.iloc[most_similar_entry_index]['content']}"
    else:
        memory = "You don't have any relevant memories."
    
    return memory

def update_profile():
    # Read the original user profile data from the file
    with open(userprofile, "r") as file:
        original_data = file.read()

    # Prepare the data to be sent to the profiling module
    update_data = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]

    # Send the user profile data to the profiling module and get the response
    User_profile_updated, tokens_risk = GPT3(update_data)

    # Compare the lengths of the original data and the updated data
    if len(User_profile_updated) < len(original_data):
        # Restore the original data from a backup file
        with open(backup_userprofile, "r") as backup_file:
            restored_data = backup_file.read()
        
        # Save the restored data back to the user profile file
        with open(userprofile, "w") as file:
            file.write(restored_data)
    else:
        # Save the updated data to the user profile file
        with open(userprofile, "w") as file:
            file.write(User_profile_updated)

def backup_profile():
    profile_temp = open_file(userprofile)
    with open(backup_userprofile, "w") as backupfile:
        backupfile.write(profile_temp)   

def update_matrix():
    Update_Person_matrix = [{'role': 'system', 'content': Matrix_writer}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    Matrix_updated, tokens_risk = GPT4(Update_Person_matrix)   
    with open(User_matrix, "w") as file:
        file.write(Matrix_updated)

def write_journal():
    Prev_Chatlog = open_file(Chatlog_loc)
    if len(Prev_Chatlog) > 50:  # Check if Prev_Chatlog is not empty
        Journal_writer= open_file(Journaler)
        # st.write(Prev_Chatlog)
        Journal = [{'role': 'system', 'content': Journal_writer}, {'role': 'user', 'content': Prev_Chatlog}]
        # st.write(Journal)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=Journal, temperature=0, max_tokens=4000)
        Update_Journal = response['choices'][0]['message']['content']
        # st.write(Update_Journal)        
        try:
            open(Journal_loc, "r").close()
        except FileNotFoundError:
            open(Journal_loc, "w").close()
        
        with open(Journal_loc, "a") as Journal_file:  # Changed mode to "a" for appending to the end
            Journal_file.write("\n" + Update_Journal +"\n")

        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")
    else:
        with open(Chatlog_loc, "w", encoding='utf-8') as chat_log_file:
            chat_log_file.write("")

def write_KB():
    Prev_Chatlog = open_file(Chatlog_loc)
    if len(Prev_Chatlog) > 50:   # Check if Prev_Chatlog is not empty
        KB_entry_writer= open_file(KB_writer)
        # st.write(Prev_Chatlog)
        KB_info = [{'role': 'system', 'content': KB_entry_writer}, {'role': 'user', 'content': Prev_Chatlog}]
        # st.write(Journal)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=KB_info, temperature=0, max_tokens=4000)
        text = response['choices'][0]['message']['content']
        # st.write(Update_Journal)
        KB_temp = text
        
        try:
            open(Scratchpad, "r").close()
        except FileNotFoundError:
            open(Scratchpad, "w").close()
        
        with open(Scratchpad, "a") as Scratchpad_file:  # Changed mode to "a" for appending to the end
            Scratchpad_file.write(KB_temp +"\n\n")

def Pic_Memory():
    Update_Person_matrix = [{'role': 'system', 'content': Thinker}, {'role': 'user', 'content': prompt}]
    mem_choice, tokens_risk = GPT4(Update_Person_matrix)
    return mem_choice   


#=================================================================#

load_dotenv()

ensure_userprofile_exists(os.path.join('Memories', 'user_profile.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'user_profile_backup.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'chatlog.txt'))
ensure_Journal_exists(os.path.join('Memories', 'Journal.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'scratchpad.txt'))
ensure_userprofile_exists(os.path.join('Memories', 'user_person_matrix.txt'))
openai.api_key = os.getenv("OPENAI_API_KEY")
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

os.makedirs(os.path.dirname(chromadb_path), exist_ok=True)

os.makedirs(os.path.dirname(KB_DB_Path), exist_ok=True)
#============================JOURNALING FUNCTION =====================================#

if "Journal" not in st.session_state:
    st.session_state['Journal'] = "done"
    backup_profile()
    write_KB()

    write_journal()

#============================DB FUNCTION =====================================#
if "DB Jorunal" not in st.session_state:
    st.session_state['DB Jorunal'] = 'done'
    process_journal_entries(chromadb_path, Journal_loc)


if "KB_create" not in st.session_state:
    st.session_state['KB_create'] = 'done'
    process_entries(KB_DB_Path, Scratchpad)


if "timestamp" not in st.session_state:
    append_date_time_to_chatlog()
    st.session_state['timestamp'] = 'done'
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if "chat_log" not in st.session_state:
    st.session_state["chat_log"] = ""

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        # For assistant messages, use the custom avatar
        with st.chat_message("assistant", avatar=portrait_path):
            st.write(msg["content"])
    else:
        # For user messages, display as usual
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
if st.sidebar.radio("Show thinking", ["yes", "no"]) == "yes":
    st.session_state["show thinking"] = "yes"
else:
    st.session_state["show thinking"] = "no"
#============================CHATBOT FUNCTION =====================================#
if prompt:
    choice = Pic_Memory()
    if choice == "KB":
        KB_entries = fetch_KB_entries()
        memory = "KB entry: \n" + KB_chat_similarity(prompt, KB_entries)
        
    elif choice == "Journal":
        jorunal_entries = fetch_journal_entries()
        memory = "Journal Entry:\n" + Journal_similarity(prompt, jorunal_entries) 
        
    # elif choice == "User":
    #     memory = User_pro + Matrix_content 
    else:
        memory = " you don't have any memories about this" 

    # jorunal_entries = fetch_journal_entries()
    # KB_entries = fetch_KB_entries()
    # retrieved_journal = "Journal Entry:\n" + Journal_similarity(prompt, jorunal_entries) 
    # retrieved_KB = "KB entry: \n" + KB_chat_similarity(prompt, KB_entries)
    # memory = retrieved_journal + "\n" + retrieved_KB
    if st.session_state["show thinking"] == "yes":
        st.sidebar.header("What type of memory I'm using" )
        st.sidebar.write(choice)
        st.sidebar.header("The memory")
        st.sidebar.write(memory)
        st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user",):
        st.write(prompt)

    # followed by the actual chat messages exchanged in the session.
    time_right_now = "current time:"+"\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_prompt = {
        "role": "system",
        "content": time_right_now + Content  + memory
    }
    messages_for_api = [system_prompt] + st.session_state.messages
     
    # Call the OpenAI API with the prepared messages, including the hidden system prompt.
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=messages_for_api
    )
    msg_content = response.choices[0].message["content"]
    
    # Display assistant response in chat message container with streamed output
    with st.chat_message("assistant", avatar=portrait_path):
        st.write_stream(response_generator(msg_content))
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": msg_content, })


        # Convert the chat log into a string, store it in the session state.
    chat_log = "<<BEGIN CHATLOG>>" +"\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])+ "<<END CHATLOG>>"
    st.session_state['chat_log'] = chat_log
    
    update_profile()
    update_matrix()

    # Append the latest user and assistant messages to the chatlog file
    append_to_chatlog(f"User: {prompt}")
    append_to_chatlog(f"Assistant: {msg_content}")

    current_Chatlog = open_file(Chatlog_loc)
    if len(current_Chatlog) > 2500:
        write_KB()
        write_journal()
        append_date_time_to_chatlog()