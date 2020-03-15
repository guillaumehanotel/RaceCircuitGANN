import os
from tkinter import filedialog
from numpy import ones, vstack
from numpy.linalg import lstsq
from shapely.geometry import LineString, Point


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


def get_equation_line(ax, ay, bx, by):
    points = [(ax, ay), (bx, by)]
    x_coords, y_coords = zip(*points)
    A = vstack([x_coords, ones(len(x_coords))]).T
    m, c = lstsq(A, y_coords, rcond=-1)[0]
    # print("y = {m}x + {c}".format(m=round(m, 2), c=round(c, 2)))
    return [round(m, 2), round(c, 2)]


def get_segments_intersection_point(segment1, segment2):
    line1 = LineString([(segment1[0], segment1[1]), (segment1[2], segment1[3])])
    line2 = LineString([(segment2[0], segment2[1]), (segment2[2], segment2[3])])
    intersection_point = line1.intersection(line2)
    if isinstance(intersection_point, Point):
        return [intersection_point.x, intersection_point.y]
    else:
        return False

