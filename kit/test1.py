import os


def generate_files():
    files = ['vercel.json','requirements.txt','build_files.sh','README.md']
    # Get the current directory path
    current_directory = os.getcwd()
    # Get the list of file names in the current directory
    file_names = os.listdir(current_directory)
    
    if 'manage.py' in file_names:
        vercel_json = open(current_directory+files[0],'w')
        vercel_json.write()
