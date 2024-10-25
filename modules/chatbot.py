
import openai
import time
import streamlit as st
import os
from modules.utils import portrait_path
import ollama
# portrait_path = os.path.join('app', 'Protrait', 'T.png')

def chatbotGPT4(conversation, model="gpt-4", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

def chatbotGPT3(conversation, model="gpt-3.5-turbo-0125", temperature=0, max_tokens=4000):
    response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
    text = response['choices'][0]['message']['content']
    return text, response['usage']['total_tokens']

def chat_with_ollama(messages, model='phi3'):
    try:
        response = ollama.chat(model=model, messages=messages)
        # Access the content based on Ollama's response structure
        content = response['message']['content']
        return content
    except Exception as e:
        error_message = str(e).lower()
        if "not found" in error_message:
            return f"Model '{model}' not found. Please refer to the documentation at https://ollama.com/library."
        else:
            return f"An unexpected error occurred with model '{model}': {str(e)}"


def response_generator(msg_content):
    lines = msg_content.split('\n')  # Split the content into lines to preserve paragraph breaks.
    for line in lines:
        words = line.split()  # Split the line into words to introduce a delay for each word.
        for word in words:
            yield word + " "
            time.sleep(0.1)
        yield "\n"  # After finishing a line, yield a newline character to preserve paragraph breaks.

def show_msgs():
    portrait_path = os.path.join('app', 'Portrait', 'T.png')
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            # For assistant messages, use the custom avatar
            with st.chat_message("assistant", avatar=portrait_path):
                st.write(msg["content"])
        else:
            # For user messages, display as usual
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

def greet():
    if "greet" not in st.session_state:
        system_prompt = {
            "role": "system",
            "content": persona_content + "greet the user and ask a about something you don't know about them, something you haven't talked about before" + User_pro 
        }
        messages_for_api = [system_prompt] + st.session_state.messages
        # Call the OpenAI API with the prepared messages, including the hidden system prompt.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=messages_for_api
        )
        greeting = response.choices[0].message["content"]

        with st.chat_message("assistant", avatar=portrait_path):
            st.write_stream(response_generator(greeting))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": greeting, })
        # Convert the chat log into a string, store it in the session state.
        chat_log = "<<BEGIN CHATLOG>>" +"\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in st.session_state.messages])+ "<<END CHATLOG>>"
        st.session_state['chat_log'] = chat_log
        # Append the latest user and assistant messages to the chatlog file
        append_to_chatlog(f"Assistant: {greeting}")
        st.session_state["greet"] = True