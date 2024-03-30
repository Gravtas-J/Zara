
import os



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


Chatlog_loc = os.path.join('app', 'Memories', 'chatlog.txt')
Chatlog_loc = os.path.join('app', 'Memories', 'chatlog.txt')
Journal_loc = os.path.join('app', 'Memories', 'Journal.txt')

userprofile=os.path.join('app', 'Memories', 'user_profile.txt')
backup_userprofile = os.path.join('app', 'Memories', 'user_profile_backup.txt')
backup_user_matrix = os.path.join('app', 'Memories', 'user_matrix_backup.txt')
User_matrix = os.path.join('app', 'Memories', 'user_matrix.txt')

profile_template = open_file(os.path.join('modules', 'STARTUP', 'userprofile.txt'))
matrix_template = open_file(os.path.join('modules', 'STARTUP', 'usermatrix.txt'))


chromadb_path = os.path.join('app','chromadb', 'chromaDB.db')

Journaler = os.path.join('app', 'system prompts', 'Journaler.md')
Update_user = os.path.join('app', 'system prompts', 'User_update.md')
Matrix_writer_prompt = os.path.join('app', 'system prompts', 'Personality_matrix.md')
Persona=os.path.join('app', 'Personas', 'Zara.md')
portrait_path = os.path.join('app', 'Portrait', 'T.png')

Matrix_content = open_file(User_matrix)
Matrix_writer_content = open_file(Matrix_writer_prompt)
Profile_update = open_file(Update_user)
User_pro = open_file(userprofile)
Profile_check = Profile_update+User_pro
persona_content = open_file(Persona)
Matrix_writer = Matrix_writer_content + Matrix_content

Content = persona_content + User_pro + Matrix_content

