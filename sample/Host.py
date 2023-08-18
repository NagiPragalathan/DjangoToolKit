import os
import re
import json
import ast
import importlib.metadata as metadata
from Designer.BackGroundColor import *
from Designer.ForeGroundColor import *
import djangify
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> find and get the imported package and there versions >>>>>>>>>>>>>>>>>>>>>>>>

def find_views_folder():
    current_directory = os.getcwd()

    for root, dirs, files in os.walk(current_directory):
        if 'models.py' in files:
            return os.path.basename(root)

    return None

def t_size():
    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines
    return [terminal_width, terminal_height]

def get_imported_modules(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    # Parse the Python source code
    tree = ast.parse(content)

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if node.module:
                    imported_modules.add(f"{node.module}.{alias.name}")
                else:
                    imported_modules.add(alias.name)

    return imported_modules

def find_imported_modules(root_dir):
    out = []
    imported_modules = set()
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                imported_modules.update(get_imported_modules(file_path))
    for module in imported_modules:
        out.append(module)
    return out
        
def get_modules_version(module_datas):        
    module_versions = {}
    for name in module_datas:
        module_name = name.split(".")[0]
        try:
            # Use importlib.metadata to get the version information
            version = metadata.version(module_name)
            module_versions[module_name] = version
        except metadata.PackageNotFoundError:
            pass
    return module_versions

def shortcut_version(root_dir):
    imported_modules = find_imported_modules(root_dir)
    versions = get_modules_version(imported_modules)
    return versions
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Getting App name of django >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def get_app_name():
    root_directory = os.path.dirname(os.path.abspath(__file__))
    file_names = os.listdir(root_directory)
    if 'manage.py' in file_names:
        manage_py_path = os.path.join(root_directory, 'manage.py')
        with open(manage_py_path, 'r') as fs:
            lines = fs.readlines()

        for line in lines:
            if 'DJANGO_SETTINGS_MODULE' in line:
                pattern = r"os\.environ\.setdefault\('DJANGO_SETTINGS_MODULE', '(.*?)'\)"
                match = re.search(pattern, line)
                if match:
                    django_settings_module = match.group(1)
                    return django_settings_module.split('.')[0]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Createing the needed files to deployment >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Define the data as a dictionary
vercel_data_dict = {
    "version": 2,
    "builds": [
        {
            "src": f"{get_app_name()}/wsgi.py",
            "use": "@vercel/python",
            "config": {"maxLambdaSize": "15mb", "runtime": "python3.9"}
        },
        {
            "src": "build_files.sh",
            "use": "@vercel/static-build",
            "config": {
                "distDir": "staticfiles_build"
            }
        }
    ],
    "routes": [
        {
            "src": "/static/(.*)",
            "dest": "/static/$1"
        },
        {
            "src": "/(.*)",
            "dest": f"{get_app_name()}/wsgi.py"
        }
    ]
}
build_data = '''# build_files.sh
pip install -r requirements.txt
python3.9 manage.py collectstatic'''

def generate_files():
    files = ['vercel.json','requirements.txt','build_files.sh','README.md']
    # Get the current directory path
    current_directory = os.getcwd()
    # Get the list of file names in the current directory
    file_names = os.listdir(current_directory)
    vercel_data = json.dumps(vercel_data_dict, indent=2)
    if 'manage.py' in file_names:
        # create vercel file
        vercel_json = open(os.path.join(current_directory,files[0]),'w')
        vercel_json.write(vercel_data)
        vercel_json.close()
        print(f"The {blue('vercel.json')} are Created - {green('OK')}. ")
        # create build.sh file 
        build = open(os.path.join(current_directory,'build_files.sh'),'w')
        build.write(build_data)
        build.close()
        print(f"The {blue('build_files.sh')} are Created - {green('OK')}. ")
        # create requirements.txt
        req = open(os.path.join(current_directory,'requirements.txt'),'w')
        req_data = '\n'.join([ f'{i}=={j}' for i,j in shortcut_version(current_directory).items() ])
        req.write(req_data)
        req.close()
        print(f"The {blue('requirements.txt')} are Created - {green('OK')}. ")
    else:
        print(("-"*t_size[0])+f"\nThe '{blue('manage.py')}' are not found - {red('404')}.\n{greybg('Note :')}{red(style=3,text=' make sure you are in the root dir of your project in the Terminal.')}\n"+("-"*t_size[0]))
        
        

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Edit Files >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> App SetUp >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def add_to_installed_apps(file_path, app_name):
    # Read the content of the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Check if the app name is already in INSTALLED_APPS
    if f"'{app_name}'" in content:
        print(f"{ yellow('Warning ') }: {yellow1bg(f' The app ')+yellow1bg(app_name)+yellow1bg(' is already in INSTALLED_APPS.')}")
        return

    # Define the new app to be added
    new_app = f"    '{app_name}',\n"

    # Use regular expression to find the INSTALLED_APPS list and add the new app
    pattern = r'INSTALLED_APPS\s*=\s*\[\s*[\s\S]*?\]'
    new_content = re.sub(pattern, lambda match: match.group()[:-2] + f"\n{new_app}]", content, count=1)

    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(new_content)

def set_allowed_hosts(file_path, desired_allowed_hosts):
    # Read the content of the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Use regular expression to find the ALLOWED_HOSTS line and replace its value
    pattern = r'ALLOWED_HOSTS\s*=\s*\[[^\]]*\]'
    new_content = re.sub(pattern, f'ALLOWED_HOSTS = {desired_allowed_hosts}', content)

    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(new_content)

def comment_out_databases(file_path):
    # Read the content of the file
    with open(file_path, 'r') as f:
        content = f.read()
    pattern = r"'''(\s*DATABASES\s*=\s*{\s*[\s\S]*?\s*}\s*)'''"
    match = re.search(pattern, content)

    if not match:
        # Use regular expression to find the DATABASES dictionary and comment it out
        pattern = r'(DATABASES\s*=\s*\{[\s\S]*?\}\s})'
        new_content = re.sub(pattern, r"''' \1 '''", content)
        # Write the updated content back to the file
        with open(file_path, 'w') as f:
            f.write(new_content)
    else:
        print(f"{ yellow('Warning ') }: {yellow1bg(f' The DATABASES ')+yellow1bg(' is already in Commentd.')}")

    
        
def update_static_settings(file_path):
    # Read the content of the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Define the new content to replace the old string
    new_content = """import os

STATIC_URL = 'static/'
STATICFILES_DIRS = os.path.join(BASE_DIR, 'static'),
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
"""

    # Use regular expression to find and replace the old string with the new content
    if new_content not in content:
        pattern = r'STATIC_URL\s*=\s*\'static/\''
        content = re.sub(pattern, new_content, content)
        # Write the updated content back to the file
        with open(file_path, 'w') as f:
            f.write(content)
    else:
        print(f"{ yellow('Warning ') }: {yellow1bg('Static settings are up-to-date.')}")
        
def update_wsgi_file(file_path):
    # Read the content of the file
    with open(file_path, 'r') as f:
        content = f.read()

    # If the line "app = application" does not exist in the content, add it as the last line
    if 'app = application' not in content:
        content += '\napp = application\n'

    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)

def update_urlpatterns(file_path, content_to_add):
    check = '''urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)'''
    # Read the content of the file
    with open(file_path, 'r') as f:
        content = f.read()

    # Check if the content already exists in urlpatterns
    if re.search(re.escape(content_to_add), content):
        print(f"{ yellow('Warning ') }: {yellow1bg('Content already exists in urlpatterns.')}")
    else:
        with open(file_path, 'r') as f:
            content = f.read()
        obj=content
        if check not in obj:
            with open(file_path, 'a') as f:
                f.write(obj+content_to_add)
        print(f"In the '{blue('url.py')}' URL's are updated - {green('OK')}")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def base_edit_settings_file(settings_file_path):
    app_name = find_views_folder()  
    desired_allowed_hosts = "['127.0.0.1', '.vercel.app', '.now.sh']"  
    # Add the app to INSTALLED_APPS
    add_to_installed_apps(settings_file_path, app_name)
    # Set the desired ALLOWED_HOSTS
    set_allowed_hosts(settings_file_path, desired_allowed_hosts)
    
    update_static_settings(settings_file_path)
    print(f"Base Settings are updated in the {blue('settings.py')} - {green('OK')}")
    

# Function to edit the settings.py file
def edit_settings_file(settings_file_path):
    desired_allowed_hosts = "['127.0.0.1', '.vercel.app', '.now.sh']"  
    # Add the app to INSTALLED_APPS
    add_to_installed_apps(settings_file_path, find_views_folder())
    # Set the desired ALLOWED_HOSTS
    set_allowed_hosts(settings_file_path, desired_allowed_hosts)
    
    comment_out_databases(settings_file_path)
    
    update_static_settings(settings_file_path)
    print(f"Vercel Hosting Base Settings are updated in the {blue('settings.py') - {green('OK')}}")
    
# Function to edit the wsgi.py file
def edit_wsgi_file(wsgi_file_path):
    update_wsgi_file(wsgi_file_path)

def edit_urls_file(file_path):
    content_to_add = f"""from django.conf.urls.static import static
from {get_app_name()} import settings

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)"""
    update_urlpatterns(file_path, content_to_add)

def Change_the_files():
    # Get the root directory of your Django project
    Name = get_app_name()
    if Name:
        root_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)),Name)
        # Update the settings.py file
        settings_file_path = os.path.join(root_directory, 'settings.py')
        edit_settings_file(settings_file_path)
        # Update the wsgi.py file
        wsgi_file_path = os.path.join(root_directory, 'wsgi.py')
        edit_wsgi_file(wsgi_file_path)
        # Update the urls.py file
        urls_file_path = os.path.join(root_directory, 'urls.py')
        edit_urls_file(urls_file_path)
    else:
        print(f'''{red(f"The {blue('manage.py')}")}{red(' are not exist your current location')} - {green1('Please provide a name for your application')}''')
    
# generate_files()
# Change_the_files()

