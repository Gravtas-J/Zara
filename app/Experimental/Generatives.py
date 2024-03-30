from modules.utilities import *

# Generative functions

def assessor():
    # Prepare the data to be sent to the profiling module
    update_data = [{'role': 'system', 'content': Assessment_full}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    
    # Send the user profile data to the profiling module and get the response
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=update_data, temperature=0, max_tokens=4000)
    update_assessment = response['choices'][0]['message']['content']
    # update_assessment, tokens_risk = GPT3(update_data)
    with open(cb_assess_loc, "w") as file:
        file.write(update_assessment + "\n")

def update_profile():
    # Read the original user profile data from the file
    with open(userprofile, "r") as file:
        original_data = file.read()

    # Prepare the data to be sent to the profiling module
    update_data = [{'role': 'system', 'content': Profile_check}, {'role': 'user', 'content': st.session_state.get('chat_log', '')}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0125", messages=update_data, temperature=0, max_tokens=4000)
    User_profile_updated = response['choices'][0]['message']['content']
    # Send the user profile data to the profiling module and get the response
    # User_profile_updated, tokens_risk = GPT3(update_data)

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
