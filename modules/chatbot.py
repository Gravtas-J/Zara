
import openai
import time
import streamlit as st
from modules.utils import portrait_path

def chatbotGPT4(conversation, model="gpt-4", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

def chatbotGPT3(conversation, model="gpt-3.5-turbo-0125", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

def response_generator(msg_content):
    for word in msg_content.split():
        yield word + " "
        time.sleep(0.1)

def show_msgs():
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            # For assistant messages, use the custom avatar
            with st.chat_message("assistant", avatar=portrait_path):
                st.write(msg["content"])
        else:
            # For user messages, display as usual
            with st.chat_message(msg["role"]):
                st.write(msg["content"])