import re
import os

from Designer.BackGroundColor import *
from Designer.ForeGroundColor import *

def t_size():
    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines
    return [terminal_width, terminal_height]


def convert_to_django_html(input_file, output_file):
    with open(input_file, 'r') as f:
        html_content = f.read()

    # Use regular expressions to find all href and src attributes
    href_pattern = r'href="((?!https:|{% static ).+?)"'
    src_pattern = r'src="((?!https:|{% static ).+?)"'

    # Convert href attributes to Django static tags
    django_html_content = re.sub(href_pattern, r'''href="{% static '\1' %}"''', html_content)

    # Convert src attributes to Django static tags, skipping if already in the format {% static '' %}
    django_html_content = re.sub(src_pattern, r'''src="{% static '\1' %}"''', django_html_content)

    with open(output_file, 'w') as f:
        f.write(django_html_content)

def djangotemp():
    input_directory = input("Enter the directory path where HTML files are located: ")
    output_directory = "output_html_files"

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get the list of file names in the input directory
    file_names = os.listdir(input_directory)

    # Loop through each file in the input directory
    
    for file_name in file_names:
        if file_name.endswith(".html"):
            input_file_path = os.path.join(input_directory, file_name)
            output_file_path = os.path.join(output_directory, file_name)
            convert_to_django_html(input_file_path, output_file_path)

    print(grey("Conversion completed. Django HTML files are saved in the 'output_html_files' directory.")+" - "+green("OK"))
