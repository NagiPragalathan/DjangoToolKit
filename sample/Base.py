from Host import base_edit_settings_file, edit_urls_file, get_app_name, t_size,find_views_folder
import os, re
from Designer.BackGroundColor import *
from Designer.ForeGroundColor import *
from templatetage import Data

def create_templatetags():
    path = os.path.join(os.getcwd(),find_views_folder())
    tag_path = os.path.join(path,'templatetags')
    if not os.path.exists('templatetags'):
            # Create the folder
            os.makedirs(tag_path)
            print(f"Folder '{blue('templatetags')}' created successfully. - {green('OK')}")
    else:
        print(f"{red('Folder')} '{blue('templatetags')}'{red(' already exists.')}")
    Create_template = open(os.path.join(tag_path,'django_tags.py'),'w')
    Create_template.write(Data)
    Create_template.close()
    print(f"The file { blue('django_tags.py') } are created into TemplateTages - {green('OK')}")
    
    
def create_folders():
    # Replace 'folder_name' with the name of the folder you want to create
    print((brown(" Base File Creations ".center(t_size()[0],'-'))))
    for folder_name in ['templates','static']:
        # Check if the folder already exists
        if not os.path.exists(folder_name):
            # Create the folder
            os.makedirs(folder_name)
            print(f"Folder '{blue(folder_name)}' created successfully. - {green('OK')}")
        else:
            print(f"{red('Folder')} '{blue(folder_name)}'{red(' already exists.')}")
    print(brown('-')*t_size()[0])
    
    # Define the regular expression pattern to match the 'DIRS' list
    pattern = r"'DIRS': \[\s*\]"
    
    root_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),get_app_name())

    settings_file_path = os.path.join(root_directory, 'settings.py')
    with open(settings_file_path,'r') as f:
        settings_data = f.read()
        # Check if the 'DIRS' list is empty
        if re.search(pattern, settings_data):
            # If it is empty, add 'templates' to the 'DIRS' list using re.sub()
            modified_settings_data = re.sub(pattern, "'DIRS': ['templates']", settings_data)
            with open(settings_file_path, 'w') as f:
                f.write(modified_settings_data)
        else:
            modified_settings_data = settings_data
            
    # The Modifications are start from here...
    
    base_edit_settings_file(settings_file_path)
    edit_urls_file(os.path.join(root_directory, 'urls.py'))
    create_templatetags()
    

create_folders()