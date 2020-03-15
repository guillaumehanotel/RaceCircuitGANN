import tkinter as tk
from math import sin, radians, degrees
from pygame.math import Vector2
import math
from src.utils import get_equation_line_by_segment, get_segments_intersection_point


class RadarDirection:
    CENTER = 0
    LEFT = 1
    RIGHT = 2
    LEFT_DIAGONAL = 3
    RIGHT_DIAGONAL = 4


# Les fonctions move et show sont réappelés toutes les 20ms
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
        self.init_car_position(self.length, self.width, 125, 300)

        self.center = self.get_center_coordinates()

        # Pour se mouvoir, la voiture doit avoir une vélocité et une accélération
        self.velocity = Vector2(0.0, 0.0)
        self.acceleration = 0.0

        # Pour gérer la direction, il faut avoir :
        # - la direction (steering) qui correspond à quel point "les roues sont tournées"
        # - l'angle de rotation, qui est calculé en fonction des paramètres de la voiture
        self.steering = 0.0
        self.angle = 0.0

        # La vélocité est limitée pour ne pas dépasser une certaine vitesse
        self.max_velocity = 20
        # L'accélération est aussi limitée pour ne pas avoir une montée en vitesse trop rapide
        self.max_acceleration = 5.0
        # La direction des roues a aussi une limite -> plus c'est élevé, plus on peut pivoter "rapidement"
        self.max_steering = 100

        self.brake_deceleration = 10
        self.free_deceleration = 8

        # La propriété car correspond à son polygone dans le canvas
        self.car = None

    def init_car_position(self, length, width, position_x, position_y):
        """
        Place la voiture à sa position initiale
        """
        initial_coord = Vector2(position_x, position_y), Vector2(position_x + width, position_y), \
                        Vector2(position_x, position_y + length), Vector2(position_x + width, position_y + length)

        self.upper_left_corner, self.upper_right_corner, \
        self.bottom_left_corner, self.bottom_right_corner = initial_coord

        self.rotated_upper_left_corner, self.rotated_upper_right_corner, \
        self.rotated_bottom_left_corner, self.rotated_bottom_right_corner = initial_coord

    def move(self):
        """
        Fonction permettant de mettre à jour la position de la voiture en fonction de sa vélocité et de son accélération
        """
        self.velocity += (0, self.acceleration * dt)
        self.velocity.y = max(-self.max_velocity, min(self.velocity.y, self.max_velocity))

        if self.has_reach_limit():
            self.velocity = self.velocity * -20

        self.upper_left_corner += self.velocity.rotate(self.angle) * dt
        self.upper_right_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_left_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_right_corner += self.velocity.rotate(self.angle) * dt

        self.center = self.get_center_coordinates()
        self.angle = self.compute_car_angle()

        self.canvas.after(delay, self.move)

    def compute_car_angle(self):
        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.y / turning_radius
        else:
            angular_velocity = 0
        angle = self.bound_angle(self.angle + degrees(angular_velocity) * dt)
        self.steering = 0
        return angle

    def bound_angle(self, angle):
        if angle > 360:
            angle = self.angle - 360
        elif angle < 0:
            angle = 360 - (-self.angle)
        return angle

    def has_reach_limit(self):
        if self.is_position_out_of_bound(self.rotated_bottom_right_corner) or \
                self.is_position_out_of_bound(self.rotated_bottom_left_corner) or \
                self.is_position_out_of_bound(self.rotated_upper_right_corner) or \
                self.is_position_out_of_bound(self.rotated_upper_left_corner):
            return True
        return False

    def is_position_out_of_bound(self, coord):
        if coord[0] < 0 or coord[0] > self.canvas.winfo_width() or \
                coord[1] < 0 or coord[1] > self.canvas.winfo_height():
            return True
        return False

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
        self.stop_car()

    def stop_car(self):
        self.velocity.y = 0
        self.acceleration = 0

    def reset(self):
        self.init_car_position(self.length, self.width, 125, 300)
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
        # Met

        # Dessin de la voiture
        self.car = self.canvas.create_polygon(rotated_positions, outline='green', fill='')
        self.draw_track_intersection_with_car_points(rotated_positions)
        self.draw_center()
        self.draw_direction_arrow()
        self.draw_radar_lines()

        self.canvas.after(delay, self.draw)

    def draw_track_intersection_with_car_points(self, car_corner_positions):
        front_car_segment = [car_corner_positions[0][0], car_corner_positions[0][1], car_corner_positions[1][0],
                             car_corner_positions[1][1]]
        right_car_segment = [car_corner_positions[1][0], car_corner_positions[1][1], car_corner_positions[2][0],
                             car_corner_positions[2][1]]
        back_car_segment = [car_corner_positions[2][0], car_corner_positions[2][1], car_corner_positions[3][0],
                            car_corner_positions[3][1]]
        left_car_segment = [car_corner_positions[3][0], car_corner_positions[3][1], car_corner_positions[0][0],
                            car_corner_positions[0][1]]
        self.draw_track_intersection_points(front_car_segment, 'yellow')
        self.draw_track_intersection_points(right_car_segment, 'yellow')
        self.draw_track_intersection_points(back_car_segment, 'yellow')
        self.draw_track_intersection_points(left_car_segment, 'yellow')

    def draw_track_intersection_points(self, line_coord, color='red'):
        track_segments_ids = list(self.canvas.find_withtag("track_segment"))
        for track_segment_id in track_segments_ids:
            track_segment_coord = self.canvas.coords(track_segment_id)
            intersection_point = get_segments_intersection_point(line_coord, track_segment_coord)
            if intersection_point:
                point = self.draw_point([intersection_point[0], intersection_point[1]], color)
                self.canvas.itemconfig(point, tags="track_intersection")

    def draw_radar_lines(self):

        # une fonction qui prend en paramètre la direction et qui retourne l'equation_line
        # une fonction qui prend en paramètre le direction et l'equation_line et qui renvoie les coordonnées de la ligne
        # fonction qui draw la ligne

        self.draw_radar_line_by_direction(RadarDirection.CENTER)
        self.draw_radar_line_by_direction(RadarDirection.LEFT)
        self.draw_radar_line_by_direction(RadarDirection.RIGHT)
        self.draw_radar_line_by_direction(RadarDirection.LEFT_DIAGONAL)
        self.draw_radar_line_by_direction(RadarDirection.RIGHT_DIAGONAL)

        # car_width_coord = self.center.x, self.center.y, \
        #                   (self.rotated_bottom_right_corner.x + self.rotated_upper_right_corner.x) / 2, \
        #                   (self.rotated_bottom_right_corner.y + self.rotated_upper_right_corner.y) / 2
        # car_width_equation_line = get_equation_line_by_segment(*car_width_coord)
        #
        # self.draw_center_radar_line(center)
        # self.draw_left_radar_line(center, car_width_equation_line)
        # self.draw_right_radar_line(center, car_width_equation_line)
        # self.draw_right_diagonal_radar_line(center)
        # self.draw_left_diagonal_radar_line(center)

    def draw_radar_line_by_direction(self, radar_direction):
        equation_line = self.get_equation_line_by_direction(radar_direction)
        line_coord = self.get_line_coord_by_equation_line_and_direction(equation_line, radar_direction)
        self.draw_radar_line(line_coord)

    def get_equation_line_by_direction(self, radar_direction):
        if radar_direction == RadarDirection.CENTER:
            segment_coord = self.center.x, self.center.y, \
                            (self.rotated_upper_left_corner.x + self.rotated_upper_right_corner.x) / 2, \
                            (self.rotated_upper_left_corner.y + self.rotated_upper_right_corner.y) / 2
        elif radar_direction == RadarDirection.LEFT or radar_direction == RadarDirection.RIGHT:
            segment_coord = self.center.x, self.center.y, \
                            (self.rotated_bottom_right_corner.x + self.rotated_upper_right_corner.x) / 2, \
                            (self.rotated_bottom_right_corner.y + self.rotated_upper_right_corner.y) / 2
        elif radar_direction == RadarDirection.LEFT_DIAGONAL:
            rotated_diagonal_point = self.rotate(
                [Vector2(self.center.x - (self.length / 2), self.upper_left_corner.y)], self.angle, self.center)
            segment_coord = self.center.x, self.center.y, rotated_diagonal_point[0][0], rotated_diagonal_point[0][1]
        elif radar_direction == RadarDirection.RIGHT_DIAGONAL:
            rotated_diagonal_point = self.rotate(
                [Vector2(self.center.x + (self.length / 2), self.upper_left_corner.y)], self.angle, self.center)
            segment_coord = self.center.x, self.center.y, rotated_diagonal_point[0][0], rotated_diagonal_point[0][1]
        return get_equation_line_by_segment(*segment_coord)

    def get_line_coord_by_equation_line_and_direction(self, equation_line, radar_direction):
        if radar_direction == RadarDirection.CENTER:
            x = 0
            if 0 <= self.angle < 180:
                x = self.canvas.winfo_width()
        elif radar_direction == RadarDirection.LEFT:
            x = 0
            if 90 <= self.angle < 270:
                x = self.canvas.winfo_width()
        elif radar_direction == RadarDirection.RIGHT:
            x = self.canvas.winfo_width()
            if 90 <= self.angle < 270:
                x = 0
        elif radar_direction == RadarDirection.LEFT_DIAGONAL:
            x = 0
            if 45 <= self.angle < 225:
                x = self.canvas.winfo_width()
        elif radar_direction == RadarDirection.RIGHT_DIAGONAL:
            x = self.canvas.winfo_width()
            if 135 <= self.angle < 315:
                x = 0
        y = x * equation_line[0] + equation_line[1]
        return self.center.x, self.center.y, x, y

    def draw_radar_line(self, line_coord):
        line = self.canvas.create_line(*line_coord)
        self.canvas.itemconfig(line, tags="radar_line")
        self.draw_track_intersection_points(line_coord)

    def erase_old_forms(self):
        self.canvas.delete(self.car)
        self.canvas.delete("center")
        self.canvas.delete("arrow")
        self.canvas.delete("real_car")
        self.canvas.delete("radar_line")
        self.canvas.delete("track_intersection")

    def draw_direction_arrow(self):
        """
        Dessin de la flèche de direction
        """
        arrow_coord = self.center.x, self.center.y, \
                      (self.rotated_upper_left_corner.x + self.rotated_upper_right_corner.x) / 2, \
                      (self.rotated_upper_left_corner.y + self.rotated_upper_right_corner.y) / 2
        arrow = self.canvas.create_line(*arrow_coord, arrow=tk.LAST)
        self.canvas.itemconfig(arrow, tags="arrow")

    def draw_real_car(self):
        """
        Permet de dessiner la 'vraie' position de la voiture qui n'est pas pivotée
        """
        coordinates = self.get_coordinates_as_list()
        real_car = self.canvas.create_polygon(coordinates, outline='red', fill='')
        self.canvas.itemconfig(real_car, tags="real_car")

    def draw_center(self):
        """
        Dessin du centre de la voiture
        """
        center_point = self.canvas.create_oval(self.center.x - 1, self.center.y - 1, self.center.x, self.center.y,
                                               fill='#FFFF00')
        self.canvas.itemconfig(center_point, tags="center")

    def draw_point(self, point, color='red'):
        return self.canvas.create_oval(point[0] - 3, point[1] - 3, point[0], point[1], outline=color, fill=color)
