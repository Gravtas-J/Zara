import streamlit as st
import os
icon = os.path.join('app', 'Portrait', 'icon.ico')
st.set_page_config(layout="wide", page_title='Zara', page_icon= icon)



from datetime import datetime
from dotenv import load_dotenv
from modules.initial import ensure_chatlog_exists, ensure_userprofile_exists, ensure_usermatrix_exists, ensure_Journal_exists


ensure_chatlog_exists(os.path.join('app', 'Memories', 'chatlog.txt'))
ensure_userprofile_exists(os.path.join('app', 'Memories', 'user_profile.txt'))
ensure_userprofile_exists(os.path.join('app', 'Memories', 'user_profile_backup.txt'))
ensure_usermatrix_exists(os.path.join('app', 'Memories', 'user_matrix.txt'))
ensure_usermatrix_exists(os.path.join('app', 'Memories', 'user_matrix_backup.txt'))
ensure_Journal_exists(os.path.join('app', 'Memories', 'Journal.txt'))

from modules.startup_OLL import init_states, startup, append_date_time_to_chatlog
from modules.chatbot import response_generator, show_msgs, chat_with_ollama, greet_OLL
from modules.journal_OLL import write_journal, append_to_chatlog
from modules.faiss import calculate_similarity
from modules.profile_OLL import update_profile, update_matrix
from modules.timeout import timeout_tasks
from modules.utils import open_file, Chatlog_loc, Content, portrait_path


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

def add_bg_image():
    # image_path = os.path.join('app', 'Portrait', 'Background.png')
    # with open(image_path, "rb") as image_file:
    #     base64_image = b64encode(image_file.read()).decode('utf-8')
    st.markdown(
        f"""
        <style>
        [data-testid="stChatMessage"] {{
            background-color : white;
            border : double;
        }}

        /* Making the header transparent */
        [data-testid="stHeader"] {{
            background-color: transparent !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Call the function to add the background image


def main():
    # st.set_page_config(layout="wide", page_title='Zara')
    add_bg_image()
    load_dotenv()
    init_states() 
    if "Startup" not in st.session_state:
        startup()    
    show_msgs()
    greet_OLL()
    timeout_tasks()
    prompt = st.chat_input()

 







    #============================CHATBOT FUNCTION =====================================#
    if prompt:
        st.session_state['has_timeout_run'] = "no"
        with st.chat_message("user",):
            st.write(prompt)
        time_right_now = "current time:"+"\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # entries = fetch_journal_entries()
        je = st.session_state['# of entries']
        memory = "Memory" + "\n" + calculate_similarity(prompt)
        # st.sidebar.write(memory)
        # st.sidebar.write(len(je))
        st.session_state.messages.append({"role": "user", "content": prompt})
        # followed by the actual chat messages exchanged in the session.
        system_prompt = {
            "role": "system",
            "content": time_right_now + Content  + memory
        }
        messages_for_api = [system_prompt] + st.session_state.messages
        # Call the OLLAMA LIBRARY with the prepared messages, including the hidden system prompt.
        response = chat_with_ollama(messages=messages_for_api)



        msg_content = response#.choices[0].message["content"]
        # Display assistant response in chat message container with streamed output
        with st.chat_message("assistant", avatar=portrait_path):
            st.write_stream(response_generator(msg_content))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": msg_content, })
        # Convert the chat log into a string, store it in the session state.
        chat_log = "<<BEGIN CHATLOG>>" +"\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])+ "<<END CHATLOG>>"
        st.session_state['chat_log'] = chat_log
        # Append the latest user and assistant messages to the chatlog file
        append_to_chatlog(f"User: {prompt}")
        append_to_chatlog(f"Assistant: {msg_content}")
        current_Chatlog = open_file(Chatlog_loc)
        if len(current_Chatlog) > 2500: #TODO - I have to change this to a time based function that will split the chatlog into chunks of 2500 char then run each function. I want it to do it when there ahsn't been a response of about 5 min or soemthign so it happens when the user isn't there to experience the slowness
            write_journal()
            append_date_time_to_chatlog()
            update_profile()
            update_matrix()

if __name__ == "__main__":
    main()
