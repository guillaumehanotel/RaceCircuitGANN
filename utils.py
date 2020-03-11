import os
from tkinter import filedialog
from numpy import ones, vstack
from numpy.linalg import lstsq


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
    f = filedialog.asksaveasfile(initialdir=default_dir, initialfile=default_name, mode='w', defaultextension=".txt",
                                 title='Save File')
    if f is None:
        return
    f.write(text)
    f.close()


def choose_file(default_dir):
    file_path = filedialog.askopenfilename(initialdir=default_dir, title="Select File", defaultextension="txt")
    return file_path


def to_line(ax, ay, bx, by):
    return [ax, ay], [bx, by]


def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


# Return true if line segments AB and CD intersect
def intersect(line1, line2):
    A = line1[0]
    B = line1[1]
    C = line2[0]
    D = line2[1]
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
