import difflib
import openai
import time
import streamlit as st
import os
from modules.chatbot import chatbotGPT4, ant_opus
from modules.utils import open_file, backup_userprofile, User_matrix, userprofile, backup_user_matrix,  Profile_check, Chatlog_loc

def load_user_messages_only(file_location):
    with open(file_location, "r") as file:
        user_messages = []
        current_message = ""  # Initialize an empty string to accumulate lines of the current message
        within_user_message = False  # Track whether the current line is part of a user message
        
        for line in file:
            # Convert the line to lowercase for case-insensitive comparison
            line_lower = line.lower()
            if line_lower.startswith("user:"):
                if current_message:  # If there's an accumulated message, append it to the list
                    user_messages.append(current_message.strip())
                current_message = line  # Start a new message
                within_user_message = True  # We are within a user message block
            elif line_lower.startswith("assistant:"):
                if current_message and within_user_message:  # If ending a user message block
                    # Append the last user message and prepare for the next block
                    user_messages.append(current_message.strip())
                    current_message = ""  # Reset the current message
                within_user_message = False  # We are now in an assistant message block, ignore lines
            elif within_user_message:  # If the line is a continuation of the last user message
                current_message += line  # Accumulate the line

        # Don't forget to add the last accumulated message to the list if it exists and it's a user message
        if current_message and within_user_message:
            user_messages.append(current_message.strip())
        
        # Check if user_messages list is empty, return as a single string
        if not user_messages:
            return "<there are no user messages>"
        else:
            return "\n".join(user_messages)  # Join all user messages into a single string with line breaks

def backup_profile():
    profile_temp = open_file(userprofile)
    with open(backup_userprofile, "w") as backupfile:
        backupfile.write(profile_temp)   

def backup_matrix():
    matrix_temp = open_file(User_matrix)
    with open(backup_user_matrix, "w") as backupfile:
        backupfile.write(matrix_temp)  

def update_profile():
    print(f"Updating Profile")
    # startup_message = st.empty()
    # startup_message.info('Updating profile', icon=None)
    start_time = time.time()  # Record the start time
    # Read the original user profile data from the file
    with open(userprofile, "r") as file:
        original_data = file.read()
    # Clear the initial startup message
    # Prepare the data to be sent to the profiling module
    update_data = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=update_data, temperature=0, max_tokens=4000)
    User_profile_updated = response['choices'][0]['message']['content']
    # Calculate the number of differences between the original data and the updated data
    diff = difflib.ndiff(original_data, User_profile_updated)
    num_differences = len([d for d in diff if d[0] != ' '])

    # Check if the number of differences exceeds 200
    if num_differences > 200:
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
    end_time = time.time()  # Record the end time
    duration = end_time - start_time  # Calculate the duration
    # startup_message.empty()
    # completed_message = st.empty()
    # completed_message.info(f'profile updated in {duration:.2f} seconds', icon=None)
    print(f'profile updated in {duration:.2f} seconds')
    # time.sleep(2)
    # completed_message.empty()

# def update_matrix():
#     print(f"Updating Matrix")
#     # startup_message = st.empty()
#     # startup_message.info('Updating User Matrix', icon=None)
#     start_time = time.time()  # Record the start time
#     with open(User_matrix, "r") as file:
#         original_data = file.read()
#     Update_Person_matrix = [{'role': 'system', 'content': Matrix_writer}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
#     Matrix_updated, tokens_risk = chatbotGPT4(Update_Person_matrix)   
#     # Calculate the number of differences between the original data and the updated data
#     diff = difflib.ndiff(original_data, Matrix_updated)
#     num_differences = len([d for d in diff if d[0] != ' '])

#     # Check if the number of differences exceeds 200
#     if num_differences > 200:
#         # Restore the original data from a backup file
#         with open(backup_user_matrix, "r") as backup_file:
#             restored_data = backup_file.read()
        
#         # Save the restored data back to the user profile file
#         with open(User_matrix, "w") as file:
#             file.write(restored_data)
#     else:
#         # Save the updated data to the user profile file
#         with open(User_matrix, "w") as file:
#             file.write(Matrix_updated)
#     end_time = time.time()  # Record the end time
#     duration = end_time - start_time  # Calculate the duration
#     # startup_message.empty()
#     # completed_message = st.empty()
#     # completed_message.info(f'Matrix updated in {duration:.2f} seconds', icon=None)
#     # time.sleep(2)
#     # completed_message.empty()
#     print(f'Matrix updated in {duration:.2f} seconds')

def update_matrix():
    print(f"Updating Matrix")
    # startup_message = st.empty()
    # startup_message.info('Updating User Matrix', icon=None)
    start_time = time.time()  # Record the start time
    # st.session_state["chat_log"] = load_user_messages_only(Chatlog_loc)
    chatlog = load_user_messages_only(Chatlog_loc)
    print(chatlog)
    with open(User_matrix, "r") as file:
        original_data = file.read()
    Update_Person_matrix = [{'role': 'user', 'content': chatlog}]
    Matrix_updated = ant_opus(conversation=Update_Person_matrix)   
    # Calculate the number of differences between the original data and the updated data
    diff = difflib.ndiff(original_data, Matrix_updated)
    num_differences = len([d for d in diff if d[0] != ' '])

    # Check if the number of differences exceeds 200
    if num_differences > 200:
        # Restore the original data from a backup file
        with open(backup_user_matrix, "r") as backup_file:
            restored_data = backup_file.read()
        
        # Save the restored data back to the user profile file
        with open(User_matrix, "w") as file:
            file.write(restored_data)
    else:
        # Save the updated data to the user profile file
        with open(User_matrix, "w") as file:
            file.write(Matrix_updated)
    backup_matrix()
    end_time = time.time()  # Record the end time
    duration = end_time - start_time  # Calculate the duration
    # startup_message.empty()
    # completed_message = st.empty()
    # completed_message.info(f'Matrix updated in {duration:.2f} seconds', icon=None)
    # time.sleep(2)
    # completed_message.empty()
    print(f'Matrix updated in {duration:.2f} seconds')
