from tkinter import *
import math
import time

WIDTH = 400
HEIGHT = 400
CANVAS_MID_X = WIDTH / 2
CANVAS_MID_Y = HEIGHT / 2
SIDE = WIDTH / 4

root = Tk()
canvas = Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

vertices = [
    [CANVAS_MID_X - SIDE / 2, CANVAS_MID_Y - SIDE / 2],
    [CANVAS_MID_X + SIDE / 4, CANVAS_MID_Y - SIDE / 2],
    [CANVAS_MID_X + SIDE / 4, CANVAS_MID_Y + SIDE / 2],
    [CANVAS_MID_X - SIDE / 2, CANVAS_MID_Y + SIDE / 2],
]

print(vertices)

angle = 1


def rotate(points, angle, center):
    angle = math.radians(angle)
    cos_val = math.cos(angle)
    sin_val = math.sin(angle)
    cx, cy = center
    new_points = []
    for x_old, y_old in points:
        x_old -= cx
        y_old -= cy
        x_new = x_old * cos_val - y_old * sin_val
        y_new = x_old * sin_val + y_old * cos_val
        new_points.append([x_new + cx, y_new + cy])
    return new_points


def draw_square(points, color="red"):
    rect = canvas.create_polygon(points, fill=color)
    canvas.itemconfig(rect, tags=("tmp"))


def launch_right_rotation(event):
    canvas.delete("tmp")
    global angle
    new_square = rotate(vertices, angle, center)
    draw_square(new_square)
    angle = angle + 8


def launch_left_rotation(event):
    canvas.delete("tmp")
    global angle
    new_square = rotate(vertices, angle, center)
    draw_square(new_square)
    angle = angle - 8


root.bind("<KeyPress-Left>", launch_left_rotation)
root.bind("<KeyPress-Right>", launch_right_rotation)

draw_square(vertices, "blue")
center = (CANVAS_MID_X - 12.5, CANVAS_MID_Y)
canvas.create_oval(CANVAS_MID_X - 12.5, CANVAS_MID_Y, CANVAS_MID_X - 12.5, CANVAS_MID_Y, width=2, fill='black')

mainloop()
