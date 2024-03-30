import difflib
import openai
import time
import streamlit as st
import os
from modules.chatbot import chatbotGPT4
from modules.utils import open_file, backup_userprofile, User_matrix, userprofile, backup_user_matrix,  Profile_check, Matrix_writer

def backup_profile():
    profile_temp = open_file(userprofile)
    with open(backup_userprofile, "w") as backupfile:
        backupfile.write(profile_temp)   

def backup_matrix():
    matrix_temp = open_file(User_matrix)
    with open(backup_userprofile, "w") as backupfile:
        backupfile.write(matrix_temp)  

def update_profile():
    print(f"Updating Profile")
    start_time = time.time()  # Record the start time
    # Read the original user profile data from the file
    with open(userprofile, "r") as file:
        original_data = file.read()

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
    print(f'profile updated in {duration:.2f} seconds')

def update_matrix():
    print(f"Updating Matrix")
    start_time = time.time()  # Record the start time
    with open(User_matrix, "r") as file:
        original_data = file.read()
    Update_Person_matrix = [{'role': 'system', 'content': Matrix_writer}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    Matrix_updated, tokens_risk = chatbotGPT4(Update_Person_matrix)   
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
    end_time = time.time()  # Record the end time
    duration = end_time - start_time  # Calculate the duration
    print(f'Matrix updated in {duration:.2f} seconds')
