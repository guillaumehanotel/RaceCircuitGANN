import os
from tkinter import filedialog


def create_directory_if_needed(directory_path):
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)


def create_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w'):
            pass
    return file_path


def save_text_in_file(text, default_dir, default_name):
    create_directory_if_needed(default_dir)
    f = filedialog.asksaveasfile(initialdir=default_dir, initialfile=default_name, mode='w', defaultextension=".txt", title='Save File')
    if f is None:
        return
    f.write(text)
    f.close()


def choose_file(default_dir):
    file_path = filedialog.askopenfilename(initialdir=default_dir, title="Select File", defaultextension="txt")
    return file_path
