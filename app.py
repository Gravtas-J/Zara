import streamlit as st
import os
import openai
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
from base64 import b64encode
from modules.initial import ensure_chatlog_exists, ensure_userprofile_exists, ensure_usermatrix_exists, ensure_Journal_exists

ensure_chatlog_exists(os.path.join('app', 'Memories', 'chatlog.txt'))
ensure_userprofile_exists(os.path.join('app', 'Memories', 'user_profile.txt'))
ensure_userprofile_exists(os.path.join('app', 'Memories', 'user_profile_backup.txt'))
ensure_usermatrix_exists(os.path.join('app', 'Memories', 'user_matrix.txt'))
ensure_usermatrix_exists(os.path.join('app', 'Memories', 'user_matrix_backup.txt'))
ensure_Journal_exists(os.path.join('app', 'Memories', 'Journal.txt'))

from modules.startup import init_states, startup, append_date_time_to_chatlog
from modules.chatbot import response_generator, show_msgs, greet
from modules.journal import write_journal, append_to_chatlog
from modules.faiss import calculate_similarity
from modules.profile import update_profile, update_matrix
from modules.timeout import timeout_tasks
from modules.utils import open_file, Chatlog_loc, Content, portrait_path



st.set_page_config(layout="wide", page_title='Zara')

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
    add_bg_image()
    # image = Image.open(os.path.join("app", "Portrait", "Zara.png"))
    # col1, col2, col3= st.columns([6,1,7])

    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    init_states() 
    startup()
    # with col1:
    #     st.image(image, )
    prompt = st.chat_input()
    # with col3:
    show_msgs()
    greet()
        
    timeout_tasks()

    #============================CHATBOT FUNCTION =====================================#
    if prompt:
        st.session_state['has_timeout_run'] = "no"
        # with col3:
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
        # Call the OpenAI API with the prepared messages, including the hidden system prompt.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=messages_for_api
        )
        msg_content = response.choices[0].message["content"]
        # Display assistant response in chat message container with streamed output
        st.session_state.messages.append({"role": "assistant", "content": msg_content, })
        # with col3:
        with st.chat_message("assistant", avatar=portrait_path):
            st.write_stream(response_generator(msg_content))
        # Add assistant response to chat history

        # Convert the chat log into a string, store it in the session state.
        chat_log = "<<BEGIN CHATLOG>>" +"\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])+ "<<END CHATLOG>>"
        st.session_state['chat_log'] = chat_log
        # Append the latest user and assistant messages to the chatlog file
        append_to_chatlog(f"User: {prompt}")
        append_to_chatlog(f"Assistant: {msg_content}")
        current_Chatlog = open_file(Chatlog_loc)
        if len(current_Chatlog) > 2500: #TODO - I have to change this to a time based function that will split the chatlog into chunks of 2500 char then run each function. I want it to do it when there ahsn't been a response of about 5 min or soemthign so it happens when the user isn't there to experience the slowness
            print(f'chatlog too full, clearing')
            write_journal()
            append_date_time_to_chatlog()
            update_profile()
            update_matrix()

if __name__ == "__main__":
    main()
