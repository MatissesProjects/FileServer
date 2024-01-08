import os

def get_parent_directory():
    # Returns the path of the parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    return parent_dir

def get_path(filename, path):
    # Generates the correct path to a file
    parent_dir = get_parent_directory()
    new_path = os.path.join(parent_dir, path, filename)
    return new_path

def path_only(path):
    # Returns the path without the filename
    return os.path.dirname(path)