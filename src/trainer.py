import neat
import pickle
import time


class NEATTrainer:
    """
    Classe gérant l'entraînement des voitures avec NEAT
    """

    def __init__(self, canvas, config_path):
        self.canvas = canvas
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
            from src.car import Car
            car = Car(self.canvas)
            car.is_autonomous = True
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
              f"Time={self.stats['generation_times'][-1]:.2f}s")

    def run_generation_simulation(self):
        """
        Lance la simulation pour une génération jusqu'à ce que toutes les voitures soient mortes
        ou timeout atteint
        """
        max_frames = 1000  # Timeout après 1000 frames (20 secondes)
        frame_count = 0

        # Réinitialise toutes les voitures
        for car in self.cars:
            car.reset()

        # Simule jusqu'à ce que toutes les voitures soient mortes ou timeout
        while any(car.is_alive for car in self.cars) and frame_count < max_frames:
            for i, car in enumerate(self.cars):
                if car.is_alive:
                    # Obtient les entrées du réseau de neurones (distances radar)
                    inputs = car.get_radar_distances()

                    # Obtient les sorties du réseau de neurones
                    outputs = self.networks[i].activate(inputs)

                    # Applique les sorties (steering, acceleration)
                    steering = outputs[0]  # Entre -1 et 1
                    acceleration = outputs[1]  # Entre -1 et 1

                    car.drive_autonomous(steering, acceleration)

                    # Met à jour la position de la voiture manuellement
                    car.move()

            # Met à jour l'interface (obligatoire pour Tkinter)
            self.canvas.update()
            frame_count += 1

            # Petit délai pour éviter de surcharger le CPU
            time.sleep(0.001)

        # Calcule le fitness de chaque voiture
        for i, car in enumerate(self.cars):
            fitness = self.calculate_fitness(car, frame_count)
            self.genomes[i].fitness = fitness

    def calculate_fitness(self, car, max_frames):
        """
        Calcule le fitness d'une voiture
        Récompense:
        - Distance parcourue
        - Temps de survie
        - Vitesse moyenne
        """
        # Distance parcourue (poids principal)
        distance_score = car.distance_traveled

        # Bonus pour le temps de survie (encourage à rester en vie longtemps)
        time_bonus = car.time_alive * 0.1

        # Bonus pour la vitesse (encourage à aller vite)
        if car.time_alive > 0:
            avg_velocity = car.distance_traveled / car.time_alive
            speed_bonus = avg_velocity * 10
        else:
            speed_bonus = 0

        # Pénalité si mort trop rapidement
        if car.time_alive < 50:
            early_death_penalty = -100
        else:
            early_death_penalty = 0

        fitness = distance_score + time_bonus + speed_bonus + early_death_penalty

        return max(fitness, 0)  # Fitness minimum de 0

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

        # Affiche le meilleur réseau
        print(f'\nBest genome:\n{winner}')

        # Sauvegarde le meilleur génome
        self.save_genome(winner, 'best_genome.pkl')

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

    def test_genome(self, genome, visualize=True):
        """
        Teste un génome (mode démo)
        """
        from src.car import Car

        # Crée le réseau de neurones
        net = neat.nn.FeedForwardNetwork.create(genome, self.config)

        # Crée une voiture
        car = Car(self.canvas)
        car.is_autonomous = True
        car.reset()

        # Lance la simulation
        max_frames = 2000
        frame_count = 0

        while car.is_alive and frame_count < max_frames:
            # Obtient les entrées
            inputs = car.get_radar_distances()

            # Obtient les sorties
            outputs = net.activate(inputs)

            # Applique les sorties
            car.drive_autonomous(outputs[0], outputs[1])

            # Met à jour la position de la voiture
            car.move()

            # Met à jour l'interface
            if visualize:
                self.canvas.update()
                time.sleep(0.02)  # 50 FPS

            frame_count += 1

        fitness = self.calculate_fitness(car, frame_count)
        print(f"Test finished. Fitness: {fitness:.2f}, Distance: {car.distance_traveled:.2f}, "
              f"Time alive: {car.time_alive}")

        return fitness
