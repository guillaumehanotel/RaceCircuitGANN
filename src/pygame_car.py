from math import sin, radians, degrees
from pygame.math import Vector2
import math
from src.utils import get_equation_line_by_segment, get_segments_intersection_point


class RadarDirection:
    CENTER = 'CENTER'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    LEFT_DIAGONAL = 'LEFT_DIAGONAL'
    RIGHT_DIAGONAL = 'RIGHT_DIAGONAL'


# Paramètres de simulation
dt = 0.2


class PygameCar:
    """
    Classe Car optimisée pour Pygame - pas de dépendance à Tkinter
    """

    def __init__(self, track_segments, start_x=125, start_y=300):
        self.track_segments = track_segments  # Liste de segments [(x1,y1,x2,y2), ...]

        # Dimensions de la voiture
        self.length = 24
        self.width = 12

        # Position initiale
        self.start_x = start_x
        self.start_y = start_y
        self.init_car_position(self.length, self.width, start_x, start_y)

        self.center = self.get_center_coordinates()

        # Vélocité et accélération
        self.velocity = Vector2(0.0, 0.0)
        self.acceleration = 0.0

        # Direction et angle
        self.steering = 0.0
        self.angle = 0.0

        # Limites
        self.max_velocity = 20
        self.max_acceleration = 5.0
        self.max_steering = 100

        self.brake_deceleration = 10
        self.free_deceleration = 8

        self.radar_segments = []

        # Propriétés pour le mode autonome et le GANN
        self.is_alive = True
        self.fitness = 0.0
        self.distance_traveled = 0.0
        self.time_alive = 0
        self.is_autonomous = True  # Par défaut autonome pour Pygame

        # Limites de la fenêtre (Pygame)
        self.window_width = 800
        self.window_height = 610

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
        Met à jour la position de la voiture
        """
        if not self.is_alive:
            return

        # Sauvegarde la position précédente
        prev_center = self.get_center_coordinates()

        self.velocity += (0, self.acceleration * dt)
        self.velocity.y = max(-self.max_velocity, min(self.velocity.y, self.max_velocity))

        self.upper_left_corner += self.velocity.rotate(self.angle) * dt
        self.upper_right_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_left_corner += self.velocity.rotate(self.angle) * dt
        self.bottom_right_corner += self.velocity.rotate(self.angle) * dt

        self.center = self.get_center_coordinates()
        self.angle = self.compute_car_angle()

        # Met à jour les coordonnées rotées
        self.update_rotated_coordinates()

        # Calcule les segments radar
        self.get_radar_segments()

        # Détection de collision avec les bords
        if self.has_reach_window_limit():
            self.is_alive = False
            return

        # Calcule la distance parcourue
        if self.is_alive:
            distance_moved = math.sqrt((self.center.x - prev_center.x)**2 + (self.center.y - prev_center.y)**2)
            self.distance_traveled += distance_moved
            self.time_alive += 1

            # Détection de collision avec la piste
            if self.check_collision_with_track():
                self.is_alive = False

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

    def has_reach_window_limit(self):
        if self.is_position_out_of_bound(self.rotated_bottom_right_corner) or \
                self.is_position_out_of_bound(self.rotated_bottom_left_corner) or \
                self.is_position_out_of_bound(self.rotated_upper_right_corner) or \
                self.is_position_out_of_bound(self.rotated_upper_left_corner):
            return True
        return False

    def is_position_out_of_bound(self, coord):
        if coord[0] < 0 or coord[0] > self.window_width or \
                coord[1] < 0 or coord[1] > self.window_height:
            return True
        return False

    def reset(self):
        self.init_car_position(self.length, self.width, self.start_x, self.start_y)
        self.velocity.x = 0
        self.velocity.y = 0
        self.steering = 0
        self.angle = 0
        self.acceleration = 0
        self.is_alive = True
        self.fitness = 0.0
        self.distance_traveled = 0.0
        self.time_alive = 0

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

    def update_rotated_coordinates(self, rotated_positions=None):
        """
        Met à jour les coordonnées rotées
        """
        if rotated_positions is None:
            rotated_positions = self.rotate([
                self.upper_left_corner,
                self.upper_right_corner,
                self.bottom_right_corner,
                self.bottom_left_corner,
            ], self.angle, (self.center.x, self.center.y))

        self.rotated_upper_left_corner = Vector2(rotated_positions[0][0], rotated_positions[0][1])
        self.rotated_upper_right_corner = Vector2(rotated_positions[1][0], rotated_positions[1][1])
        self.rotated_bottom_right_corner = Vector2(rotated_positions[2][0], rotated_positions[2][1])
        self.rotated_bottom_left_corner = Vector2(rotated_positions[3][0], rotated_positions[3][1])

    # =========================== Autonomous Driving ===========================

    def get_radar_distances(self):
        """
        Retourne les distances des 5 radars normalisées
        """
        distances = []
        max_distance = 500.0

        if len(self.radar_segments) == 5:
            for segment in self.radar_segments:
                distance = math.sqrt((segment[2] - segment[0])**2 + (segment[3] - segment[1])**2)
                normalized_distance = min(distance / max_distance, 1.0)
                distances.append(normalized_distance)
        else:
            distances = [1.0, 1.0, 1.0, 1.0, 1.0]

        return distances

    def drive_autonomous(self, steering_output, acceleration_output):
        """
        Contrôle autonome
        """
        if not self.is_alive:
            return

        self.steering = steering_output * self.max_steering
        self.acceleration = acceleration_output * self.max_acceleration

    def check_collision_with_track(self):
        """
        Vérifie collision avec la piste
        """
        car_segments = [
            [self.rotated_upper_left_corner.x, self.rotated_upper_left_corner.y,
             self.rotated_upper_right_corner.x, self.rotated_upper_right_corner.y],
            [self.rotated_upper_right_corner.x, self.rotated_upper_right_corner.y,
             self.rotated_bottom_right_corner.x, self.rotated_bottom_right_corner.y],
            [self.rotated_bottom_right_corner.x, self.rotated_bottom_right_corner.y,
             self.rotated_bottom_left_corner.x, self.rotated_bottom_left_corner.y],
            [self.rotated_bottom_left_corner.x, self.rotated_bottom_left_corner.y,
             self.rotated_upper_left_corner.x, self.rotated_upper_left_corner.y]
        ]

        for car_segment in car_segments:
            for track_segment in self.track_segments:
                intersection_point = get_segments_intersection_point(car_segment, track_segment)
                if intersection_point:
                    return True

        return False

    # =========================== Radar Lines ===========================

    def get_radar_segments(self):
        radar_lines = self.get_radar_lines()
        self.radar_segments = []
        for radar_line in radar_lines:
            intersection_point = self.get_track_intersection_point_by_radar_line(radar_line)
            if intersection_point:
                segment_coord = (self.center.x, self.center.y, intersection_point[0], intersection_point[1])
                self.radar_segments.append(segment_coord)

    def get_track_intersection_point_by_radar_line(self, line_coord):
        closest_intersection_point = None
        for track_segment in self.track_segments:
            intersection_point = get_segments_intersection_point(line_coord, track_segment)
            if intersection_point:
                if closest_intersection_point is None:
                    closest_intersection_point = intersection_point
                else:
                    # Calcule la distance au centre
                    dist_current = math.sqrt((intersection_point[0] - self.center.x)**2 +
                                           (intersection_point[1] - self.center.y)**2)
                    dist_closest = math.sqrt((closest_intersection_point[0] - self.center.x)**2 +
                                           (closest_intersection_point[1] - self.center.y)**2)
                    if dist_current < dist_closest:
                        closest_intersection_point = intersection_point
        return closest_intersection_point

    def get_radar_lines(self):
        radar_directions = [a for a in dir(RadarDirection) if not a.startswith('__')]
        return list(map(lambda direction: self.get_radar_line_coord_by_direction(direction), radar_directions))

    def get_radar_line_coord_by_direction(self, radar_direction):
        equation_line = self.get_equation_line_by_direction(radar_direction)
        return self.get_line_coord_by_equation_line_and_direction(equation_line, radar_direction)

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
                x = self.window_width
        elif radar_direction == RadarDirection.LEFT:
            x = 0
            if 90 <= self.angle < 270:
                x = self.window_width
        elif radar_direction == RadarDirection.RIGHT:
            x = self.window_width
            if 90 <= self.angle < 270:
                x = 0
        elif radar_direction == RadarDirection.LEFT_DIAGONAL:
            x = 0
            if 45 <= self.angle < 225:
                x = self.window_width
        elif radar_direction == RadarDirection.RIGHT_DIAGONAL:
            x = self.window_width
            if 135 <= self.angle < 315:
                x = 0
        y = x * equation_line[0] + equation_line[1]
        return self.center.x, self.center.y, x, y

    def get_center_coordinates(self):
        return Vector2(
            (self.upper_left_corner.x + self.bottom_right_corner.x) / 2,
            (self.upper_left_corner.y + self.bottom_right_corner.y) / 2
        )
