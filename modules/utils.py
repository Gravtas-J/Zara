
import os



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


Chatlog_loc = os.path.join('Memories', 'chatlog.txt')
profile_template = open_file(os.path.join('modules', 'STARTUP', 'userprofile.txt'))
matrix_template = open_file(os.path.join('modules', 'STARTUP', 'usermatrix.txt'))

chromadb_path = os.path.join('chromadb', 'chromaDB.db')
Chatlog_loc = os.path.join('Memories', 'chatlog.txt')
Journal_loc = os.path.join('Memories', 'Journal.txt')
Journaler = os.path.join('system prompts', 'Journaler.md')


backup_userprofile = os.path.join('Memories', 'user_profile_backup.txt')
User_matrix = os.path.join('Memories', 'user_matrix.txt')
userprofile=os.path.join('Memories', 'user_profile.txt')
Update_user = os.path.join('system prompts', 'User_update.md')
Persona=os.path.join('Personas', 'Zara.md')
backup_user_matrix = os.path.join('Memories', 'user_matrix_backup.txt')
Matrix_writer_prompt = os.path.join('system prompts', 'Personality_matrix.md')
Matrix_content = open_file(User_matrix)
Matrix_writer_content = open_file(Matrix_writer_prompt)
Profile_update = open_file(Update_user)
User_pro = open_file(userprofile)
Profile_check = Profile_update+User_pro
persona_content = open_file(Persona)
Matrix_writer = Matrix_writer_content + Matrix_content

chromadb_path = os.path.join('chromadb', 'chromaDB.db')
