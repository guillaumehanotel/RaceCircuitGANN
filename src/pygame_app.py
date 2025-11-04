#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application Pygame pour l'entraînement GANN - Beaucoup plus performante que Tkinter
Peut afficher 50+ voitures en temps réel à 60 FPS
"""

import pygame
import os
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, ROOT_DIR)


class PygameGANNApp:
    def __init__(self):
        pygame.init()

        # Fenêtre principale
        self.width = 800
        self.height = 650
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('RaceCircuitGANN - Pygame Edition (High Performance)')

        self.clock = pygame.time.Clock()
        self.running = True

        # Font
        self.font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 14)

        # Piste
        self.track_segments = []
        self.load_default_track()

        # Trainer
        self.trainer = None
        self.is_training = False

        # État de l'UI
        self.state = "MENU"  # MENU, TRAINING, TESTING

    def load_default_track(self):
        """
        Charge le circuit par défaut
        """
        circuit_path = ROOT_DIR + '/saves/circuit01.txt'
        if os.path.exists(circuit_path):
            with open(circuit_path, 'r') as f:
                for line in f:
                    coords = line.replace(" ", "").rstrip().split(",")
                    if len(coords) == 4:
                        segment = (float(coords[0]), float(coords[1]),
                                 float(coords[2]), float(coords[3]))
                        self.track_segments.append(segment)
            print(f"Loaded track with {len(self.track_segments)} segments")
        else:
            print(f"Warning: Default track not found at {circuit_path}")

    def run(self):
        """
        Boucle principale
        """
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()

    def handle_events(self):
        """
        Gestion des événements
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "TRAINING":
                        self.stop_training()
                    self.state = "MENU"

                # Raccourcis clavier
                if self.state == "MENU":
                    if event.key == pygame.K_t:
                        self.start_training()
                    elif event.key == pygame.K_s:
                        self.start_testing()
                    elif event.key == pygame.K_q:
                        self.running = False

    def update(self):
        """
        Mise à jour logique
        """
        pass

    def render(self):
        """
        Rendu graphique
        """
        if self.state == "MENU":
            self.render_menu()
        elif self.state == "TRAINING":
            # Le trainer gère son propre rendu
            pass
        elif self.state == "TESTING":
            # Le trainer gère son propre rendu
            pass

        pygame.display.flip()

    def render_menu(self):
        """
        Affiche le menu principal
        """
        self.screen.fill((32, 40, 39))

        # Dessine la piste
        for segment in self.track_segments:
            pygame.draw.line(self.screen, (169, 172, 171),
                           (segment[0], segment[1]),
                           (segment[2], segment[3]), 3)

        # Titre
        title = self.font.render("RaceCircuitGANN - Pygame Edition", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("High Performance Training - 60 FPS", True, (100, 255, 100))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 75))
        self.screen.blit(subtitle, subtitle_rect)

        # Options du menu
        y_offset = 150
        menu_items = [
            ("T - Start Training", "Train 50 generations with all cars visible", (0, 255, 0)),
            ("S - Test Best Model", "Visualize the best trained model", (0, 150, 255)),
            ("Q - Quit", "Exit the application", (255, 100, 100))
        ]

        for key_text, desc_text, color in menu_items:
            # Texte de la touche
            key_surface = self.font.render(key_text, True, color)
            key_rect = key_surface.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(key_surface, key_rect)

            # Description
            desc_surface = self.small_font.render(desc_text, True, (150, 150, 150))
            desc_rect = desc_surface.get_rect(center=(self.width // 2, y_offset + 20))
            self.screen.blit(desc_surface, desc_rect)

            y_offset += 60

        # Informations
        y_offset = 500
        info_lines = [
            f"Track: {len(self.track_segments)} segments loaded",
            "During training: ESC to skip generation",
            "All 50 cars visible in real-time!",
            "Green car = best performer"
        ]

        for info_text in info_lines:
            info_surface = self.small_font.render(info_text, True, (100, 100, 100))
            info_rect = info_surface.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(info_surface, info_rect)
            y_offset += 20

    def start_training(self):
        """
        Démarre l'entraînement
        """
        if len(self.track_segments) == 0:
            print("Error: No track loaded!")
            return

        print("Starting training with Pygame renderer...")
        print("All 50 cars will be visible in real-time at 60 FPS!")

        self.state = "TRAINING"

        from src.pygame_trainer import PygameNEATTrainer

        config_path = ROOT_DIR + '/config-neat.txt'
        self.trainer = PygameNEATTrainer(self.screen, self.track_segments, config_path)

        # Lance l'entraînement (bloquant)
        winner = self.trainer.train(generations=50)

        print(f"\nTraining completed! Best fitness: {self.trainer.best_fitness:.2f}")

        # Retour au menu
        self.state = "MENU"

    def start_testing(self):
        """
        Teste le meilleur modèle
        """
        model_path = ROOT_DIR + '/models/best_genome_pygame.pkl'

        if not os.path.exists(model_path):
            print("No trained model found! Train first (press T)")
            return

        print("Loading and testing best model...")

        self.state = "TESTING"

        from src.pygame_trainer import PygameNEATTrainer

        config_path = ROOT_DIR + '/config-neat.txt'
        self.trainer = PygameNEATTrainer(self.screen, self.track_segments, config_path)

        genome = self.trainer.load_genome(model_path)
        self.trainer.test_genome(genome)

        # Retour au menu
        self.state = "MENU"

    def stop_training(self):
        """
        Arrête l'entraînement
        """
        print("Training interrupted by user")
        self.is_training = False


def main():
    """
    Point d'entrée
    """
    app = PygameGANNApp()
    app.run()


if __name__ == "__main__":
    main()
