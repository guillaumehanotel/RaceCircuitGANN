from tkinter import *
from src.utils import *
from datetime import datetime
from src.car import Car
from shapely.geometry import LineString, Point
import os
import threading

ROOT_DIR = os.path.abspath(os.curdir)
saves_dir = ROOT_DIR + '/saves'
models_dir = ROOT_DIR + '/models'
now = datetime.now()

# Crée le dossier models s'il n'existe pas
if not os.path.exists(models_dir):
    os.makedirs(models_dir)


class App:
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

        # NEAT Trainer
        self.trainer = None
        self.training_thread = None

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
        # Car Control
        self.window.bind("<KeyPress-Up>", self.car.up)
        self.window.bind("<KeyPress-Down>", self.car.down)
        self.window.bind("<KeyPress-Left>", self.car.turn_left)
        self.window.bind("<KeyPress-Right>", self.car.turn_right)
        self.window.bind("<space>", self.car.stop)
        self.canvas.pack(side=BOTTOM)

    def setup_window_components(self):
        self.draw_line_btn = Button(self.window)
        self.draw_line_img = PhotoImage(file=ROOT_DIR + "/assets/draw_line.png")
        self.draw_line_btn.config(image=self.draw_line_img, command=self.active_drawing_mode)
        self.draw_line_btn.pack(side=LEFT)

        self.open_btn = Button(self.window)
        self.open_img = PhotoImage(file=ROOT_DIR + "/assets/open.png")
        self.open_btn.config(image=self.open_img, command=self.choose_and_draw_from_file)
        self.open_btn.pack(side=LEFT)

        self.save_btn = Button(self.window)
        self.save_img = PhotoImage(file=ROOT_DIR + "/assets/save.png")
        self.save_btn.config(image=self.save_img, command=self.save_positions)
        self.save_btn.pack(side=LEFT)

        self.erase_btn = Button(self.window)
        self.erase_img = PhotoImage(file=ROOT_DIR + "/assets/erase.png")
        self.erase_btn.config(image=self.erase_img, command=self.erase)
        self.erase_btn.pack(side=LEFT)

        self.reset_btn = Button(self.window)
        self.reset_img = PhotoImage(file=ROOT_DIR + "/assets/reset.png")
        self.reset_btn.config(image=self.reset_img, command=self.reset)
        self.reset_btn.pack(side=LEFT)

        # Boutons pour le mode GANN
        self.train_btn = Button(self.window, text="Train AI", command=self.start_training, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.train_btn.pack(side=LEFT, padx=5)

        self.test_btn = Button(self.window, text="Test AI", command=self.test_best_model, bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        self.test_btn.pack(side=LEFT, padx=5)

        # Label pour afficher les stats
        self.stats_label = Label(self.window, text="Generation: 0 | Best: 0.0 | Avg: 0.0", bg='#d9d9d9', font=('Arial', 9))
        self.stats_label.pack(side=RIGHT, padx=10)

    def reset(self):
        self.car.reset()

    def run(self, creative_mode=False):
        if creative_mode is False:
            circuit01_path = ROOT_DIR + "/saves/circuit01.txt"
            if os.path.exists(circuit01_path):
                self.draw_from_file(circuit01_path)

            self.car.draw()
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
            self.canvas.itemconfig(line, tags="temporary")

    def draw_line(self, event):
        """
        Lorsque l'on relache la souris, les lignes temporaires sont supprimées,
        et une ligne "définitive" est crée et ajoutée à une liste
        """
        if self.is_drawing_mode and self.is_drawing_line:
            self.canvas.delete("temporary")
            self.is_drawing_line = False
            line_coord = self.line_start_x, self.line_start_y, event.x, event.y
            line = self.canvas.create_line(*line_coord, width=3, fill="#A9ACAB")
            self.canvas.itemconfig(line, tags="track_segment")
            self.forms.append(line)

    def draw_point(self, point):
        self.canvas.create_oval(point[0] - 3, point[1] - 3, point[0], point[1], outline='red', fill='red')

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
                self.canvas.itemconfig(line_form, tags="track_segment")
                self.forms.append(line_form)

    def erase(self):
        self.canvas.delete("track_segment")
        self.forms = []

    # =========================== GANN Training Methods ===========================

    def start_training(self):
        """
        Démarre l'entraînement GANN dans un thread séparé
        """
        if self.training_thread and self.training_thread.is_alive():
            print("Training is already running!")
            return

        # Vérifie qu'un circuit est chargé
        if len(self.forms) == 0:
            print("Please load a circuit first!")
            return

        # Désactive le contrôle manuel
        self.window.unbind("<KeyPress-Up>")
        self.window.unbind("<KeyPress-Down>")
        self.window.unbind("<KeyPress-Left>")
        self.window.unbind("<KeyPress-Right>")
        self.window.unbind("<space>")

        # Initialise le trainer
        from src.trainer import NEATTrainer
        config_path = ROOT_DIR + '/config-neat.txt'
        self.trainer = NEATTrainer(self.canvas, config_path)

        # Démarre l'entraînement dans un thread
        self.training_thread = threading.Thread(target=self._train_worker)
        self.training_thread.daemon = True
        self.training_thread.start()

        print("Training started! This will take a while...")

    def _train_worker(self):
        """
        Worker thread pour l'entraînement
        """
        try:
            winner = self.trainer.train(generations=50)
            print(f"\nTraining completed! Best fitness: {self.trainer.best_fitness:.2f}")

            # Sauvegarde le meilleur modèle
            self.trainer.save_genome(winner, models_dir + '/best_genome.pkl')

        except Exception as e:
            print(f"Error during training: {e}")
            import traceback
            traceback.print_exc()

    def test_best_model(self):
        """
        Teste le meilleur modèle entraîné
        """
        best_model_path = models_dir + '/best_genome.pkl'

        if not os.path.exists(best_model_path):
            print("No trained model found! Please train first.")
            return

        # Initialise le trainer si nécessaire
        if self.trainer is None:
            from src.trainer import NEATTrainer
            config_path = ROOT_DIR + '/config-neat.txt'
            self.trainer = NEATTrainer(self.canvas, config_path)

        # Charge et teste le modèle
        genome = self.trainer.load_genome(best_model_path)
        print("Testing best model...")
        fitness = self.trainer.test_genome(genome, visualize=True)
        print(f"Test completed! Fitness: {fitness:.2f}")

    def update_stats_display(self):
        """
        Met à jour l'affichage des statistiques d'entraînement
        """
        if self.trainer:
            gen = self.trainer.generation
            best = self.trainer.stats['best_fitness_history'][-1] if self.trainer.stats['best_fitness_history'] else 0
            avg = self.trainer.stats['avg_fitness_history'][-1] if self.trainer.stats['avg_fitness_history'] else 0
            self.stats_label.config(text=f"Generation: {gen} | Best: {best:.2f} | Avg: {avg:.2f}")
            self.window.after(1000, self.update_stats_display)  # Update every second
