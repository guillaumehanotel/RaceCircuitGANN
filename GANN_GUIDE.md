# Guide d'Utilisation du Système GANN (Genetic Algorithm + Neural Network)

## 🎯 Ce qui a été implémenté

### ✅ Système Complet GANN Fonctionnel

Le projet possède maintenant un système complet d'entraînement de voitures autonomes utilisant :
- **NEAT** (NeuroEvolution of Augmenting Topologies)
- **Réseau de neurones** évolutif
- **Algorithme génétique** pour l'optimisation
- **Fonction de fitness** récompensant la distance, la vitesse et la survie

---

## 📦 Installation

### 1. Dépendances
```bash
pip install neat-python pygame shapely mathutils
```

### 2. Vérifier la structure
```
RaceCircuitGANN/
├── src/
│   ├── car.py           # Classe Car avec mode autonome
│   ├── trainer.py       # Système d'entraînement NEAT
│   ├── app.py           # Interface graphique
│   └── utils.py         # Utilitaires
├── config-neat.txt      # Configuration NEAT
├── saves/               # Circuits sauvegardés
│   └── circuit01.txt    # Circuit par défaut
└── models/              # Modèles entraînés (créé automatiquement)
```

---

## 🚀 Utilisation

### Lancement de l'Application

```bash
python src/main.py
```

### Interface Utilisateur

L'interface contient plusieurs boutons :

#### Boutons de Circuit
- **Draw Line** : Mode dessin pour créer un circuit
- **Open** : Charger un circuit existant
- **Save** : Sauvegarder le circuit actuel
- **Erase** : Effacer tous les segments du circuit
- **Reset** : Réinitialiser la position de la voiture

#### Boutons GANN (Nouveaux)
- **Train AI** 🟢 : Lance l'entraînement (50 générations par défaut)
- **Test AI** 🔵 : Teste le meilleur modèle entraîné

#### Affichage des Statistiques
En haut à droite : `Generation: X | Best: Y.YY | Avg: Z.ZZ`

---

## 📖 Comment Entraîner une IA

### Étape 1 : Charger un Circuit

L'application charge automatiquement `saves/circuit01.txt` au démarrage.

Si vous voulez un autre circuit :
1. Cliquez sur **Open**
2. Sélectionnez un fichier dans `saves/`

### Étape 2 : Lancer l'Entraînement

1. Cliquez sur **Train AI**
2. Le contrôle manuel est désactivé
3. L'entraînement démarre avec 50 voitures par génération

#### Pendant l'Entraînement

Console (terminal) :
```
Generation 1: Best=150.23, Avg=45.67, Time=5.12s
Generation 2: Best=220.45, Avg=89.34, Time=4.89s
...
Generation 50: Best=890.12, Avg=456.78, Time=6.23s

Training completed! Best fitness: 890.12
Genome saved to /path/to/models/best_genome.pkl
```

#### Durée Estimée
- 1 génération ≈ 5-10 secondes
- 50 générations ≈ 5-10 minutes

### Étape 3 : Tester le Modèle Entraîné

1. Une fois l'entraînement terminé, cliquez sur **Test AI**
2. Le meilleur génome est chargé depuis `models/best_genome.pkl`
3. Une voiture autonome démarre et vous pouvez observer son comportement

Console :
```
Testing best model...
Test finished. Fitness: 890.12, Distance: 2500.45, Time alive: 980
```

---

## ⚙️ Architecture du Système

### Réseau de Neurones (NEAT)

**Entrées** (5 neurones) :
- Distance radar avant (CENTER)
- Distance radar gauche (LEFT)
- Distance radar gauche diagonale (LEFT_DIAGONAL)
- Distance radar droite (RIGHT)
- Distance radar droite diagonale (RIGHT_DIAGONAL)

**Sorties** (2 neurones) :
- Steering (direction) : valeur entre -1 et +1
- Acceleration : valeur entre -1 et +1

**Architecture** :
- NEAT crée automatiquement les couches cachées
- Activation : `tanh`
- Évolution : ajout/suppression de neurones et connexions

### Fonction de Fitness

```python
fitness = distance_parcourue + (temps_survie * 0.1) + (vitesse_moyenne * 10)
```

**Récompenses** :
- ✅ Distance parcourue (poids principal)
- ✅ Temps de survie (bonus)
- ✅ Vitesse moyenne (bonus pour aller vite)

**Pénalités** :
- ❌ Mort rapide (< 50 frames) : -100 points

### Algorithme Génétique (NEAT)

**Paramètres** (dans `config-neat.txt`) :
- Population : 50 génomes par génération
- Élitisme : 2 (les 2 meilleurs passent automatiquement)
- Seuil de survie : 20% (top 20% reproduisent)
- Mutation des poids : 80%
- Ajout de connexion : 50%
- Ajout de neurone : 20%

**Processus** :
1. Génération aléatoire de 50 réseaux
2. Simulation de chaque voiture jusqu'à mort/timeout
3. Calcul du fitness
4. Sélection des meilleurs (top 20%)
5. Crossover et mutation
6. Création de la génération suivante

---

## 🎮 Mode Manuel vs Autonome

### Mode Manuel (par défaut)
- Contrôles clavier :
  - ⬆️ Haut : Accélération
  - ⬇️ Bas : Décélération
  - ⬅️ Gauche : Tourner à gauche
  - ➡️ Droite : Tourner à droite
  - Espace : Arrêt d'urgence

### Mode Autonome (entraînement/test)
- Contrôle par réseau de neurones
- Détection de collision automatique
- Calcul de fitness en temps réel
- Arrêt si collision ou timeout

---

## 📊 Conseils pour l'Entraînement

### Circuits Recommandés

**Circuit Simple** :
- Peu de virages
- Lignes droites longues
- Bon pour débuter (convergence rapide)

**Circuit Complexe** :
- Virages serrés
- Nécessite plus de générations (100+)
- Meilleure généralisation

### Paramètres à Ajuster (config-neat.txt)

**Pour accélérer l'entraînement** :
```
pop_size = 30  # Moins de voitures par génération
```

**Pour améliorer la qualité** :
```
pop_size = 100  # Plus de diversité
max_stagnation = 30  # Plus de patience
```

**Pour circuits complexes** :
```python
# Dans trainer.py, ligne 90
max_frames = 2000  # Plus de temps
```

---

## 🐛 Résolution de Problèmes

### L'entraînement ne démarre pas
- Vérifiez qu'un circuit est chargé
- Regardez la console pour les erreurs

### Les voitures meurent immédiatement
- Le circuit est peut-être trop proche de la position de départ (125, 300)
- Modifiez la position initiale dans `car.py:62`

### Le fitness n'augmente pas
- Augmentez le nombre de générations
- Vérifiez que le circuit n'est pas trop complexe
- Ajustez les paramètres de mutation

### Canvas.update() freeze
- Réduisez `pop_size` dans `config-neat.txt`
- Augmentez `time.sleep()` dans `trainer.py:121`

---

## 📈 Résultats Attendus

### Génération 1-10
- Voitures très maladroites
- Meurent rapidement
- Fitness : 50-200

### Génération 10-30
- Début d'apprentissage
- Suivent le circuit partiellement
- Fitness : 200-500

### Génération 30-50
- Bon comportement
- Complètent des parties du circuit
- Fitness : 500-1000

### Génération 50+
- Comportement expert
- Peuvent compléter le circuit
- Fitness : 1000+

---

## 🔧 Fichiers Générés

### models/best_genome.pkl
- Contient le meilleur réseau de neurones
- Format : pickle Python
- Peut être chargé avec `trainer.load_genome()`

### saves/circuit01.txt
- Circuit par défaut
- Format : `x1, y1, x2, y2` (un segment par ligne)

---

## 🎓 Comprendre NEAT

NEAT (NeuroEvolution of Augmenting Topologies) est différent d'un GA classique :

1. **Évolution de la structure** : Les neurones et connexions sont ajoutés/supprimés
2. **Spéciation** : Les génomes similaires sont regroupés
3. **Innovation** : Chaque mutation est identifiée pour le crossover

**Avantages** :
- Pas besoin de définir l'architecture manuellement
- Commence simple et se complexifie
- Évite les minimums locaux

---

## 📝 Modifications du Code Original

### Fichiers Modifiés

#### src/car.py
- ✅ Ajout de `is_alive`, `fitness`, `distance_traveled`, `time_alive`
- ✅ Méthode `get_radar_distances()` pour le NN
- ✅ Méthode `drive_autonomous()` pour le contrôle IA
- ✅ Méthode `check_collision_with_track()`
- ✅ Logique de collision mise à jour

#### src/app.py
- ✅ Ajout des boutons "Train AI" et "Test AI"
- ✅ Label de statistiques
- ✅ Intégration du NEATTrainer
- ✅ Threading pour l'entraînement

### Fichiers Créés

#### src/trainer.py
- Classe `NEATTrainer`
- Fonction d'évaluation du fitness
- Boucle d'entraînement
- Sauvegarde/chargement de modèles

#### config-neat.txt
- Configuration complète de NEAT
- Paramètres du réseau de neurones
- Paramètres de l'algorithme génétique

---

## 🚀 Prochaines Améliorations Possibles

1. **Visualisation des Meilleurs** : Afficher les N meilleures voitures en temps réel
2. **Graphiques de Fitness** : Courbes d'évolution avec matplotlib
3. **Checkpoints** : Sauvegarder toutes les X générations
4. **Multi-circuits** : Entraîner sur plusieurs circuits
5. **Ralenti/Accéléré** : Curseur de vitesse de simulation
6. **Mode Replay** : Rejouer les meilleures tentatives
7. **Obstacles** : Ajouter des obstacles mobiles
8. **Détection de Tour** : Récompenser les tours complets

---

## 📞 Support

Pour plus d'informations sur NEAT :
- Documentation : https://neat-python.readthedocs.io/
- Paper original : http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf

Bon entraînement ! 🏎️💨
