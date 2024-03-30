import os
from datetime import datetime

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()
    
matrix_template = open_file(os.path.join('modules', 'STARTUP', 'usermatrix.txt'))
profile_template = open_file(os.path.join('modules', 'STARTUP', 'userprofile.txt'))

def ensure_userprofile_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write(profile_template)  # Write initial content

def ensure_usermatrix_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write(matrix_template)  # Write initial content

def ensure_chatlog_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write('')  # Write an empty string
            
def ensure_Journal_exists(filepath):
    # Check if the file exists
    if not os.path.exists(filepath):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Create the file since it doesn't exist
        with open(filepath, 'w', encoding='utf-8') as f:
            # You can initialize the file with default content if necessary
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n" + "I am Zara, I am excited to be helping whoever i am speaking with. I will be poliet but firm with who i am speaking with and trust that my memories are correct.")  # Write an empty string or initial content
