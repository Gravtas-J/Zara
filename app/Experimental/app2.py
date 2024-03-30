import streamlit as st
import anthropic
from anthropic import HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

st.title("💬 Chatbot")

# Initialize the Anthropic client with the API key
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Initialize session state for messages if it does not exist
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display each message in the chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input for new messages
if prompt := st.chat_input():
    # Append the user's message to the session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
   
    # Create a completion using the Anthropic API
    response = client.completions.create(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        model="claude-3-opus-20240229",
        max_tokens_to_sample=1000,
    )
   
    # Extract text from the response, adjust based on actual response format
    response_text = response.completion
    
    # Append the assistant's response to the session state and display it
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.chat_message("assistant").write(response_text)