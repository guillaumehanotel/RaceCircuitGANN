import neat
import pickle
import time
import pygame


class PygameNEATTrainer:
    """
    Trainer NEAT optimisé pour Pygame - Affiche toutes les voitures en temps réel
    """

    def __init__(self, screen, track_segments, config_path):
        self.screen = screen
        self.track_segments = track_segments
        self.config_path = config_path
        self.generation = 0
        self.best_genome = None
        self.best_fitness = 0
        self.is_training = False
        self.cars = []
        self.genomes = []
        self.networks = []

        # Charge la configuration NEAT
        self.config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        # Statistiques d'entraînement
        self.stats = {
            'best_fitness_history': [],
            'avg_fitness_history': [],
            'generation_times': []
        }

        # Font pour affichage stats
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 12)

    def eval_genomes(self, genomes, config):
        """
        Évalue tous les génomes d'une génération
        """
        self.generation += 1
        generation_start_time = time.time()

        # Crée les réseaux de neurones et les voitures pour chaque génome
        self.genomes = []
        self.networks = []
        self.cars = []

        for genome_id, genome in genomes:
            genome.fitness = 0
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.networks.append(net)
            self.genomes.append(genome)

            # Importe ici pour éviter les imports circulaires
            from src.pygame_car import PygameCar
            car = PygameCar(self.track_segments)
            car.is_autonomous = True
            # Initialise les radars
            car.update_rotated_coordinates()
            car.get_radar_segments()
            self.cars.append(car)

        # Lance la simulation pour cette génération
        self.run_generation_simulation()

        # Calcule les statistiques
        fitnesses = [genome.fitness for _, genome in genomes]
        avg_fitness = sum(fitnesses) / len(fitnesses)
        max_fitness = max(fitnesses)

        self.stats['best_fitness_history'].append(max_fitness)
        self.stats['avg_fitness_history'].append(avg_fitness)
        self.stats['generation_times'].append(time.time() - generation_start_time)

        # Sauvegarde le meilleur génome
        if max_fitness > self.best_fitness:
            self.best_fitness = max_fitness
            for _, genome in genomes:
                if genome.fitness == max_fitness:
                    self.best_genome = genome
                    break

        print(f"Generation {self.generation}: Best={max_fitness:.2f}, Avg={avg_fitness:.2f}, "
              f"Time={self.stats['generation_times'][-1]:.2f}s, Alive={sum(1 for c in self.cars if c.is_alive)}")

    def run_generation_simulation(self):
        """
        Lance la simulation avec affichage de TOUTES les voitures en Pygame
        """
        max_frames = 1000
        frame_count = 0
        clock = pygame.time.Clock()

        # Réinitialise toutes les voitures
        for car in self.cars:
            car.reset()
            car.update_rotated_coordinates()
            car.get_radar_segments()

        # Simule jusqu'à ce que toutes les voitures soient mortes ou timeout
        while any(car.is_alive for car in self.cars) and frame_count < max_frames:
            # Gestion des événements Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

            # Met à jour toutes les voitures
            for i, car in enumerate(self.cars):
                if car.is_alive:
                    # Obtient les entrées du réseau de neurones
                    inputs = car.get_radar_distances()

                    # Obtient les sorties du réseau de neurones
                    outputs = self.networks[i].activate(inputs)

                    # Applique les sorties
                    steering = outputs[0]
                    acceleration = outputs[1]

                    car.drive_autonomous(steering, acceleration)
                    car.move()

            # Affichage
            self.render(frame_count)

            frame_count += 1

            # Limite à 60 FPS (bien plus rapide que Tkinter qui était à 1-2 FPS)
            clock.tick(60)

        # Calcule le fitness de chaque voiture
        for i, car in enumerate(self.cars):
            fitness = self.calculate_fitness(car, frame_count)
            self.genomes[i].fitness = fitness

    def render(self, frame_count):
        """
        Affiche toutes les voitures et les stats (Pygame est TRES rapide)
        """
        # Fond noir
        self.screen.fill((32, 40, 39))

        # Dessine la piste
        for segment in self.track_segments:
            pygame.draw.line(self.screen, (169, 172, 171),
                           (segment[0], segment[1]),
                           (segment[2], segment[3]), 3)

        # Compte les voitures vivantes
        alive_count = sum(1 for car in self.cars if car.is_alive)

        # Trouve la meilleure voiture
        best_car = None
        best_distance = 0
        for car in self.cars:
            if car.distance_traveled > best_distance:
                best_distance = car.distance_traveled
                best_car = car

        # Dessine TOUTES les voitures
        for car in self.cars:
            if car.is_alive:
                # Couleur en fonction du fitness
                if car == best_car:
                    color = (0, 255, 0)  # Verte pour la meilleure
                    radar_color = (0, 255, 255)  # Cyan
                    line_width = 2
                else:
                    # Gris transparent pour les autres
                    color = (100, 100, 100)
                    radar_color = (70, 70, 70)
                    line_width = 1

                # Dessine la voiture (polygone)
                rotated_pos = [
                    (car.rotated_upper_left_corner.x, car.rotated_upper_left_corner.y),
                    (car.rotated_upper_right_corner.x, car.rotated_upper_right_corner.y),
                    (car.rotated_bottom_right_corner.x, car.rotated_bottom_right_corner.y),
                    (car.rotated_bottom_left_corner.x, car.rotated_bottom_left_corner.y)
                ]
                pygame.draw.polygon(self.screen, color, rotated_pos, line_width)

                # Dessine les radars (seulement pour la meilleure voiture)
                if car == best_car:
                    for segment in car.radar_segments:
                        pygame.draw.line(self.screen, radar_color,
                                       (segment[0], segment[1]),
                                       (segment[2], segment[3]), 1)

        # Affiche les stats
        self.draw_stats(alive_count, best_distance, frame_count)

        # Met à jour l'écran (double buffering hardware accelerated)
        pygame.display.flip()

    def draw_stats(self, alive_count, best_distance, frame_count):
        """
        Affiche les statistiques en overlay
        """
        y_offset = 10

        # Génération actuelle
        text = self.font.render(f"Generation: {self.generation}", True, (255, 255, 255))
        self.screen.blit(text, (10, y_offset))
        y_offset += 25

        # Voitures vivantes
        color = (0, 255, 0) if alive_count > 25 else (255, 165, 0) if alive_count > 10 else (255, 0, 0)
        text = self.font.render(f"Alive: {alive_count}/50", True, color)
        self.screen.blit(text, (10, y_offset))
        y_offset += 25

        # Meilleure distance
        text = self.font.render(f"Best Distance: {best_distance:.1f}", True, (0, 255, 255))
        self.screen.blit(text, (10, y_offset))
        y_offset += 25

        # Frame actuelle
        text = self.small_font.render(f"Frame: {frame_count}/1000", True, (150, 150, 150))
        self.screen.blit(text, (10, y_offset))
        y_offset += 20

        # Historique des fitness (si disponible)
        if self.stats['best_fitness_history']:
            text = self.small_font.render(f"Best Fitness: {self.stats['best_fitness_history'][-1]:.1f}",
                                         True, (150, 150, 150))
            self.screen.blit(text, (10, y_offset))
            y_offset += 20

            text = self.small_font.render(f"Avg Fitness: {self.stats['avg_fitness_history'][-1]:.1f}",
                                         True, (150, 150, 150))
            self.screen.blit(text, (10, y_offset))
            y_offset += 20

        # Instructions
        text = self.small_font.render("ESC: Skip generation", True, (100, 100, 100))
        self.screen.blit(text, (10, 590))

    def calculate_fitness(self, car, max_frames):
        """
        Calcule le fitness d'une voiture
        """
        distance_score = car.distance_traveled
        time_bonus = car.time_alive * 0.1

        if car.time_alive > 0:
            avg_velocity = car.distance_traveled / car.time_alive
            speed_bonus = avg_velocity * 10
        else:
            speed_bonus = 0

        if car.time_alive < 50:
            early_death_penalty = -100
        else:
            early_death_penalty = 0

        fitness = distance_score + time_bonus + speed_bonus + early_death_penalty

        return max(fitness, 0)

    def train(self, generations=50):
        """
        Lance l'entraînement avec NEAT
        """
        self.is_training = True

        # Crée la population
        population = neat.Population(self.config)

        # Ajoute des reporters pour suivre l'entraînement
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)

        # Lance l'entraînement
        winner = population.run(self.eval_genomes, generations)

        self.is_training = False

        print(f'\nBest genome:\n{winner}')

        # Sauvegarde le meilleur génome
        self.save_genome(winner, 'models/best_genome_pygame.pkl')

        return winner

    def save_genome(self, genome, filename):
        """
        Sauvegarde un génome dans un fichier
        """
        with open(filename, 'wb') as f:
            pickle.dump(genome, f)
        print(f"Genome saved to {filename}")

    def load_genome(self, filename):
        """
        Charge un génome depuis un fichier
        """
        with open(filename, 'rb') as f:
            genome = pickle.load(f)
        print(f"Genome loaded from {filename}")
        return genome

    def test_genome(self, genome):
        """
        Teste un génome avec visualisation complète
        """
        from src.pygame_car import PygameCar

        net = neat.nn.FeedForwardNetwork.create(genome, self.config)
        car = PygameCar(self.track_segments)
        car.is_autonomous = True
        car.reset()
        car.update_rotated_coordinates()
        car.get_radar_segments()

        max_frames = 2000
        frame_count = 0
        clock = pygame.time.Clock()

        while car.is_alive and frame_count < max_frames:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

            inputs = car.get_radar_distances()
            outputs = net.activate(inputs)
            car.drive_autonomous(outputs[0], outputs[1])
            car.move()

            # Affichage
            self.screen.fill((32, 40, 39))

            # Piste
            for segment in self.track_segments:
                pygame.draw.line(self.screen, (169, 172, 171),
                               (segment[0], segment[1]),
                               (segment[2], segment[3]), 3)

            # Voiture
            rotated_pos = [
                (car.rotated_upper_left_corner.x, car.rotated_upper_left_corner.y),
                (car.rotated_upper_right_corner.x, car.rotated_upper_right_corner.y),
                (car.rotated_bottom_right_corner.x, car.rotated_bottom_right_corner.y),
                (car.rotated_bottom_left_corner.x, car.rotated_bottom_left_corner.y)
            ]
            pygame.draw.polygon(self.screen, (0, 100, 255), rotated_pos, 2)

            # Radars
            for segment in car.radar_segments:
                pygame.draw.line(self.screen, (255, 255, 0),
                               (segment[0], segment[1]),
                               (segment[2], segment[3]), 1)

            # Stats
            text = self.font.render(f"TEST MODE - Frame: {frame_count}/{max_frames}", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))
            text = self.font.render(f"Distance: {car.distance_traveled:.1f}", True, (0, 255, 255))
            self.screen.blit(text, (10, 35))

            pygame.display.flip()
            frame_count += 1
            clock.tick(60)

        fitness = self.calculate_fitness(car, frame_count)
        print(f"Test finished. Fitness: {fitness:.2f}, Distance: {car.distance_traveled:.2f}")

        return fitness
