import random
from tkinter import *
import tkinter as tk
from utils import *
from datetime import datetime
from math import sin, radians, degrees, copysign
from pygame.math import Vector2
import math

saves_dir = './saves'
now = datetime.now()

delay = 20
dt = 0.2


# https://github.com/rasmaxim/pygame-car-tutorial/blob/master/game.py
class Car:

    def __init__(self, canvas):
        self.canvas = canvas

        # self.position = Vector2(100, 100)
        # self.width = 15
        # self.height = 30
        # X, Y
        self.upper_left_corner = Vector2(100, 100)
        self.upper_right_corner = Vector2(115, 100)
        self.bottom_left_corner = Vector2(100, 130)
        self.bottom_right_corner = Vector2(115, 130)

        self.velocity = Vector2(0.0, 0.0)
        self.acceleration = 0.0
        self.angle = 0.0
        self.steering = 0.0

        self.length = 4
        self.max_velocity = 5
        self.max_acceleration = 5.0
        self.max_steering = 50

        self.brake_deceleration = 10
        self.free_deceleration = 8

        self.car = None

    def show(self):
        """
        Fonction constamment appelé
        """
        self.canvas.delete(self.car)
        self.canvas.delete("center")
        self.canvas.delete("arrow")

        center = Vector2(
            (self.upper_left_corner.x + self.bottom_right_corner.x) / 2,
            (self.upper_left_corner.y + self.bottom_right_corner.y) / 2
        )

        rotated_positions = self.rotate(
            [
                self.upper_left_corner,
                self.upper_right_corner,
                self.bottom_right_corner,
                self.bottom_left_corner,
            ],
            self.angle,
            (center.x, center.y)
        )

        # print(self.upper_right_corner)
        # print(self.upper_left_corner)

        self.car = self.canvas.create_polygon(rotated_positions, fill='green')

        center_point = self.canvas.create_oval(center.x - 1, center.y - 1, center.x, center.y, fill='#FF0000')
        self.canvas.itemconfig(center_point, tags="center")
        arrow = self.canvas.create_line(center.x, center.y,
                                        (self.upper_right_corner.x + self.upper_left_corner.x) / 2,
                                        (self.upper_right_corner.y + self.upper_left_corner.y) / 2,
                                        arrow=tk.LAST)
        self.canvas.itemconfig(arrow, tags="arrow")

        self.canvas.after(delay, self.show)

    def move(self):
        """
        Fonction constamment appelé
        """
        self.velocity += (0, self.acceleration * dt)
        self.velocity.y = max(-self.max_velocity, min(self.velocity.y, self.max_velocity))




        # TODO trouver comment update les positions quand on tourne
        self.upper_left_corner += self.velocity.rotate(self.angle) * dt
        self.upper_right_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_left_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_right_corner += self.velocity.rotate(self.angle) * dt
        self.canvas.after(delay, self.move)

    def up(self, event):
        # self.acceleration = -1 * dt
        if self.velocity.y > 0:
            self.acceleration = self.brake_deceleration
        else:
            self.acceleration -= 1 * dt

    def down(self, event):
        # self.acceleration = 1 * dt
        if self.velocity.y < 0:
            self.acceleration = -self.brake_deceleration
        else:
            self.acceleration += 1 * dt

    def turn_left(self, event):
        self.angle -= 4

    def turn_right(self, event):
        self.angle += 4

    def stop(self, event):
        self.acceleration = 0
        self.velocity.x = 0
        self.velocity.y = 0

    def reset(self):
        self.upper_left_corner = Vector2(100, 100)
        self.upper_right_corner = Vector2(115, 100)
        self.bottom_left_corner = Vector2(100, 130)
        self.bottom_right_corner = Vector2(115, 130)
        self.velocity.x = 0
        self.velocity.y = 0
        self.angle = 0
        self.acceleration = 0

    def rotate(self, points, angle, center):
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


class ApplicationBasic:
    """Application principale"""

    def __init__(self):
        self.window = Tk()
        self.canvas = None
        self.forms = []
        self.setup_window()
        self.setup_window_components()
        self.is_drawing_mode = False
        self.is_drawing_line = False
        self.line_start_x = None
        self.line_start_y = None

    def setup_window(self):
        width = 800
        height = 650
        x = (self.window.winfo_screenwidth() / 2) - (width / 2)
        y = (self.window.winfo_screenheight() / 2) - (height / 2)
        if self.window.winfo_screenwidth() == 1920:
            self.window.geometry('%dx%d+%d+%d' % (width, height, x + 500, y))
        else:
            self.window.geometry('%dx%d+%d+%d' % (width, height, x - 500, y))
        self.window.title('Race Circuit')
        self.canvas = Canvas(self.window, bg='#202827', height=height - 40, width=width)
        self.canvas.bind("<Button-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.drawing_line)
        self.canvas.bind("<ButtonRelease-1>", self.draw_line)
        self.car = Car(self.canvas)

        self.window.bind("<KeyPress-Up>", self.car.up)
        self.window.bind("<KeyPress-Down>", self.car.down)
        self.window.bind("<KeyPress-Left>", self.car.turn_left)
        self.window.bind("<KeyPress-Right>", self.car.turn_right)
        # self.window.bind("<KeyRelease-Up>", self.car.stop)
        # self.window.bind("<KeyRelease-Down>", self.car.stop)
        # self.window.bind("<KeyRelease-Right>", self.car.stop_turn)
        # self.window.bind("<KeyRelease-Right>", self.car.stop_turn)
        self.canvas.pack(side=BOTTOM)

    def setup_window_components(self):
        self.draw_line_btn = Button(self.window)
        self.draw_line_img = PhotoImage(file="assets/draw_line.png")
        self.draw_line_btn.config(image=self.draw_line_img, command=self.active_drawing_mode)
        self.draw_line_btn.pack(side=LEFT)

        self.open_btn = Button(self.window)
        self.open_img = PhotoImage(file="assets/open.png")
        self.open_btn.config(image=self.open_img, command=self.choose_and_draw_from_file)
        self.open_btn.pack(side=LEFT)

        self.save_btn = Button(self.window)
        self.save_img = PhotoImage(file="assets/save.png")
        self.save_btn.config(image=self.save_img, command=self.save_positions)
        self.save_btn.pack(side=LEFT)

        self.erase_btn = Button(self.window)
        self.erase_img = PhotoImage(file="assets/erase.png")
        self.erase_btn.config(image=self.erase_img, command=self.erase)
        self.erase_btn.pack(side=LEFT)

        self.reset_btn = Button(self.window)
        self.reset_img = PhotoImage(file="assets/reset.png")
        self.reset_btn.config(image=self.reset_img, command=self.reset)
        self.reset_btn.pack(side=LEFT)

    def reset(self):
        self.car.reset()

    def run(self):
        circuit01_path = "./saves/circuit01.txt"
        if os.path.exists(circuit01_path):
            self.draw_from_file(circuit01_path)

        self.car.show()
        self.car.move()
        self.window.mainloop()

    def active_drawing_mode(self):
        """
        Fonction de callback appelée lorsque l'on appuie sur le bouton de dessin
        """
        self.is_drawing_mode = not self.is_drawing_mode
        if self.is_drawing_mode is True:
            self.draw_line_btn.config(bg='#aaa')
        else:
            self.draw_line_btn.config(bg='#d9d9d9')

    def start_line(self, event):
        """
        Fonction de callback appelée lorsque l'on clique dans le canvas
        a pour effet d'activer une variable de controle qui va dire que l'on est en train de dessiner
        ainsi que d'enregistrer la position x;y de départ de la ligne
        """
        # active une seconde variable qui servira de condition quant à l'écoute de l'event B1-Motion
        if self.is_drawing_mode:
            self.is_drawing_line = True
            self.line_start_x = event.x
            self.line_start_y = event.y

    def drawing_line(self, event):
        """
        Fonction de callback appelée lorsque l'on maintient le click enfoncé pour dessiner la ligne
        Si jamais on est en mode dessin et que l'on a bien cliquer pour commencer à dessiner,
        alors on supprime tous les dessins avec le tag 'temporary', et on crée une ligne avec la position de
        départ et la position courante de la souris
        """
        if self.is_drawing_mode and self.is_drawing_line:
            self.canvas.delete("temporary")
            line = self.canvas.create_line(self.line_start_x, self.line_start_y, event.x, event.y, width=3,
                                           fill="#A9ACAB")
            self.canvas.itemconfig(line, tags=("temporary"))

    def draw_line(self, event):
        """
        Lorsque l'on relache la souris, les lignes temporaires sont supprimées,
        et une ligne "définitive" est crée et ajoutée à une liste
        """
        if self.is_drawing_mode and self.is_drawing_line:
            self.canvas.delete("temporary")
            self.is_drawing_line = False
            line = self.canvas.create_line(self.line_start_x, self.line_start_y, event.x, event.y, width=3,
                                           fill="#A9ACAB")
            self.canvas.itemconfig(line, tags=("circuit"))
            self.forms.append(line)

    def save_positions(self):
        if len(self.forms) == 0:
            print("Il n'y a rien à sauvegarder")
        else:
            positions = ""
            for form in self.forms:
                positions += str(self.canvas.coords(form)).replace("[", "").replace("]", "") + "\n"
            save_text_in_file(positions, saves_dir, "save_" + now.strftime("%Y%d%m-%H%M%S"))

    def choose_and_draw_from_file(self):
        self.erase()
        file_path = choose_file(saves_dir)
        self.draw_from_file(file_path)

    def draw_from_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                coords = line.replace(" ", "").rstrip().split(",")
                line_form = self.canvas.create_line(coords[0], coords[1], coords[2], coords[3], width=3, fill="#A9ACAB")
                self.canvas.itemconfig(line_form, tags=("circuit"))
                self.forms.append(line_form)

    def erase(self):
        self.canvas.delete("circuit")
        self.forms = []


if __name__ == '__main__':
    app = ApplicationBasic()
    app.run()

    # self.window.update()
    # canvas.delete(myrect)
    # self.canvas.find_overlapping()
