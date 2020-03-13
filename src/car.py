import tkinter as tk
from math import sin, radians, degrees
from pygame.math import Vector2
import math

# Les fonctions move et show sont réappelés toutes les 20ms
from src.utils import get_equation_line

delay = 20
# Sert pour les calculs de changement de position
dt = 0.2


class Car:

    def __init__(self, canvas):
        self.canvas = canvas

        # Dimensions de la voiture
        self.length = 24
        self.width = 12

        # On initialise la position de la voiture en fonction de sa taille
        self.upper_left_corner, self.upper_right_corner, \
        self.bottom_left_corner, self.bottom_right_corner = self.init_car(self.length, self.width, 125, 300)

        # On doit également connaitre la position pivotée
        self.rotated_upper_left_corner = None
        self.rotated_upper_right_corner = None
        self.rotated_bottom_left_corner = None
        self.rotated_bottom_right_corner = None

        # Pour se mouvoir, la voiture doit avoir une vélocité et une accélération
        self.velocity = Vector2(0.0, 0.0)
        self.acceleration = 0.0

        # Pour gérer la direction, il faut avoir :
        # - la direction (steering) qui correspond à quel point "les roues sont tournées"
        # - l'angle de rotation, qui est calculé en fonction des paramètres de la voiture
        self.steering = 0.0
        self.angle = 0.0

        # La vélocité est limitée pour ne pas dépasser une certaine vitesse
        self.max_velocity = 12
        # L'accélération est aussi limitée pour ne pas avoir une montée en vitesse trop rapide
        self.max_acceleration = 5.0
        # La direction des roues a aussi une limite -> plus c'est élevé, plus on peut pivoter "rapidement"
        self.max_steering = 100

        self.brake_deceleration = 10
        self.free_deceleration = 8

        # La propriété car correspond à son polygone dans le canvas
        self.car = None

    def init_car(self, length, width, position_x, position_y):
        """
        Retourne les 4 positions de départ des coins de la voiture
        """
        return Vector2(position_x, position_y), Vector2(position_x + width, position_y), \
               Vector2(position_x, position_y + length), Vector2(position_x + width, position_y + length)

    def draw(self):
        """
        Fonction permettant d'afficher la position actuelle de la voiture de manière continue
        """
        # Efface les précédentes formes
        self.erase_old_forms()

        center = self.get_center_coordinates()

        # Récupère la nouvelle position pivotée
        rotated_positions = self.rotate([
            self.upper_left_corner,
            self.upper_right_corner,
            self.bottom_right_corner,
            self.bottom_left_corner,
        ], self.angle, (center.x, center.y))

        # Met à jour la position pivotée
        self.update_rotated_coordinates(rotated_positions)

        # Dessin de la voiture
        self.car = self.canvas.create_polygon(rotated_positions, outline='green', fill='')
        # self.draw_real_car()
        self.draw_center(center)
        self.draw_direction_arrow(center, rotated_positions)
        self.draw_radar_lines(center, rotated_positions)

        self.canvas.after(delay, self.draw)

    def draw_radar_lines(self, center, rotated_positions):
        car_length_coord = center.x, center.y, \
                           (rotated_positions[1][0] + rotated_positions[0][0]) / 2, \
                           (rotated_positions[1][1] + rotated_positions[0][1]) / 2
        car_length_equation_line = get_equation_line(*car_length_coord)

        car_width_coord = center.x, center.y, \
                          (rotated_positions[2][0] + rotated_positions[1][0]) / 2, \
                          (rotated_positions[2][1] + rotated_positions[1][1]) / 2
        car_width_equation_line = get_equation_line(*car_width_coord)

        self.draw_center_radar_line(center, car_length_equation_line)
        self.draw_left_radar_line(center, car_width_equation_line)
        self.draw_right_radar_line(center, car_width_equation_line)


    def draw_center_radar_line(self, center, car_equation_line):
        x = 0
        if 0 <= self.angle < 180:
            x = self.canvas.winfo_width()
        y = x * car_equation_line[0] + car_equation_line[1]

        line = self.canvas.create_line(center.x, center.y, x, y)
        self.canvas.itemconfig(line, tags="radar_line")

    def draw_left_radar_line(self, center, car_equation_line):
        x = 0
        if 90 <= self.angle < 270:
            x = self.canvas.winfo_width()
        y = x * car_equation_line[0] + car_equation_line[1]
        line = self.canvas.create_line(center.x, center.y, x, y)
        self.canvas.itemconfig(line, tags="radar_line")

    def draw_right_radar_line(self, center, car_equation_line):
        x = self.canvas.winfo_width()
        if 90 <= self.angle < 270:
            x = 0
        y = x * car_equation_line[0] + car_equation_line[1]
        line = self.canvas.create_line(center.x, center.y, x, y)
        self.canvas.itemconfig(line, tags="radar_line")

    def erase_old_forms(self):
        self.canvas.delete(self.car)
        self.canvas.delete("center")
        self.canvas.delete("arrow")
        self.canvas.delete("real_car")
        self.canvas.delete("radar_line")

    def draw_direction_arrow(self, center, rotated_positions):
        """
        Dessin de la flèche de direction
        """
        arrow_coord = center.x, center.y, (rotated_positions[1][0] + rotated_positions[0][0]) / 2, (
                rotated_positions[1][1] + rotated_positions[0][1]) / 2
        arrow = self.canvas.create_line(*arrow_coord, arrow=tk.LAST)
        self.canvas.itemconfig(arrow, tags="arrow")

    def draw_real_car(self):
        """
        Permet de dessiner la 'vraie' position de la voiture qui n'est pas pivotée
        """
        coordinates = self.get_coordinates_as_list()
        real_car = self.canvas.create_polygon(coordinates, outline='red', fill='')
        self.canvas.itemconfig(real_car, tags="real_car")

    def draw_center(self, center):
        """
        Dessin du centre de la voiture
        """
        center_point = self.canvas.create_oval(center.x - 1, center.y - 1, center.x, center.y, fill='#FFFF00')
        self.canvas.itemconfig(center_point, tags="center")

    def move(self):
        """
        Fonction permettant de mettre à jour la position de la voiture en fonction de sa vélocité et de son accélération
        """
        self.velocity += (0, self.acceleration * dt)
        self.velocity.y = max(-self.max_velocity, min(self.velocity.y, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.y / turning_radius
        else:
            angular_velocity = 0

        self.upper_left_corner += self.velocity.rotate(self.angle) * dt
        self.upper_right_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_left_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_right_corner += self.velocity.rotate(self.angle) * dt

        self.angle += degrees(angular_velocity) * dt
        if self.angle > 360:
            self.angle = self.angle - 360
        elif self.angle < 0:
            self.angle = 360 - (-self.angle)
        self.steering = 0

        self.canvas.after(delay, self.move)

    def up(self, event):
        self.acceleration -= 1 * dt
        self.acceleration = max(-self.max_acceleration, min(self.acceleration, self.max_acceleration))

    def down(self, event):
        self.acceleration += 1 * dt
        self.acceleration = max(-self.max_acceleration, min(self.acceleration, self.max_acceleration))

    def turn_left(self, event):
        self.steering += 100
        self.steering = max(-self.max_steering, min(self.steering, self.max_steering))

    def turn_right(self, event):
        self.steering -= 100
        self.steering = max(-self.max_steering, min(self.steering, self.max_steering))

    def stop(self, event):
        self.velocity.y = 0
        self.acceleration = 0

    def stop(self, event):
        self.acceleration = 0
        self.velocity.x = 0
        self.velocity.y = 0

    def reset(self):
        self.init_car(self.length, self.width, 200, 200)
        self.velocity.x = 0
        self.velocity.y = 0
        self.steering = 0
        self.angle = 0
        self.acceleration = 0

    def rotate(self, points, angle, center):
        """
        Retourne les positions pivotées de la voiture en fonction de l'angle
        """
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

    def get_coordinates_as_list(self):
        return [
            [self.upper_left_corner.x, self.upper_left_corner.y],
            [self.upper_right_corner.x, self.upper_right_corner.y],
            [self.bottom_right_corner.x, self.bottom_right_corner.y],
            [self.bottom_left_corner.x, self.bottom_left_corner.y]
        ]

    def get_center_coordinates(self):
        return Vector2(
            (self.upper_left_corner.x + self.bottom_right_corner.x) / 2,
            (self.upper_left_corner.y + self.bottom_right_corner.y) / 2
        )

    def update_rotated_coordinates(self, new_positions):
        """
        Met à jour les propriétés de position pivotée de la voiture avec la nouvelle position
        """
        self.rotated_upper_left_corner = Vector2(new_positions[0][0], new_positions[0][1])
        self.rotated_upper_right_corner = Vector2(new_positions[1][0], new_positions[1][1])
        self.rotated_bottom_right_corner = Vector2(new_positions[2][0], new_positions[2][1])
        self.rotated_bottom_left_corner = Vector2(new_positions[3][0], new_positions[3][1])
