# 🚗 RaceCircuitGANN - Guide des Versions

Ce projet propose maintenant **deux versions** pour répondre à différents besoins.

---

## 🎯 Quelle Version Choisir ?

### 🖥️ Version Tkinter (Originale)

**Lancez avec** : `python src/main.py`

✅ **Avantages** :
- Interface traditionnelle avec boutons
- Mode rapide ultra-performant (1.2s/génération)
- Fonctionne partout (même sans OpenGL)
- Boutons "Train AI" / "Test AI" intuitifs

❌ **Inconvénients** :
- Visualisation limitée (1 voiture max)
- Mode lent très lent (12s/génération)
- Pas d'accélération matérielle

**Idéal pour** :
- Entraînement rapide sans visualisation
- Systèmes avec UI traditionnelle
- Utilisateurs préférant les boutons

---

### 🎮 Version Pygame (Nouvelle - Haute Performance)

**Lancez avec** : `python run_pygame.py`

✅ **Avantages** :
- **60 FPS constants** avec visualisation
- **Toutes les 50 voitures** visibles en temps réel 🔥
- Accélération matérielle (SDL2)
- Interface gaming-style fluide
- **Même vitesse** que mode rapide Tkinter (~1.5s/génération)

❌ **Inconvénients** :
- Interface minimaliste (navigation clavier)
- Nécessite support OpenGL

**Idéal pour** :
- **Voir l'apprentissage** en temps réel
- Debugging visuel
- Créer des vidéos
- Performance maximale avec visualisation

---

## 📊 Tableau Comparatif

| Critère | Tkinter (Mode Lent) | Tkinter (Mode Rapide) | **Pygame** |
|---------|---------------------|----------------------|------------|
| FPS | 1-2 | N/A | **60** 🚀 |
| Voitures visibles | 1 | 0 | **50** 🎉 |
| Temps/génération | 12s | 1.2s | **1.5s** ⚡ |
| Total (50 gen) | 10 min | 1 min | **1.5 min** |
| Visualisation | Limitée | Aucune | **Complète** |
| Hardware accelerated | Non | Non | **Oui** |
| Interface | Boutons | Boutons | Clavier |

---

## 🚀 Utilisation Rapide

### Version Tkinter

```bash
# Lance l'interface Tkinter
python src/main.py

# Cliquez sur "Train AI" (mode rapide par défaut)
# Puis "Test AI" pour voir le résultat
```

### Version Pygame

```bash
# Lance l'interface Pygame
python run_pygame.py

# Appuyez sur 'T' pour Train
# Appuyez sur 'S' pour Test
# Appuyez sur 'Q' pour Quit
```

---

## 📁 Fichiers Générés

Les deux versions créent des modèles séparés :

```
models/
├── best_genome.pkl         # Modèle Tkinter
└── best_genome_pygame.pkl  # Modèle Pygame
```

Vous pouvez utiliser les deux en parallèle !

---

## 🎯 Recommandation

### Pour l'Entraînement :
**Utilisez Pygame** 🎮
- Performance identique au mode rapide Tkinter
- **MAIS** avec visualisation complète
- Voir toutes les voitures apprendre en temps réel

### Pour le Test :
Les deux versions fonctionnent bien !

---

## 📚 Documentation Complète

- **`PERFORMANCE_OPTIMIZATION.md`** : Détails sur le mode rapide Tkinter
- **`PYGAME_VERSION.md`** : Guide complet de la version Pygame
- **`GANN_GUIDE.md`** : Guide d'utilisation du système GANN

---

## 🎨 Aperçu Visuel

### Tkinter (Mode Lent)
```
┌──────────────────────────┐
│  [Buttons]              │
│  ┌────────────────────┐  │
│  │                    │  │
│  │  🟢 1 voiture      │  │
│  │     (la meilleure) │  │
│  │                    │  │
│  └────────────────────┘  │
│  Gen: 15 | Best: 234.5  │
└──────────────────────────┘
FPS: 1-2 | Temps: 12s/gen
```

### Pygame
```
┌──────────────────────────┐
│ Gen: 15                 │
│ Alive: 23/50 🟢         │
│ Best: 456.7             │
│                          │
│  ⚪⚪⚪⚪⚪⚪⚪⚪⚪           │
│  ⚪🟢⚪⚪⚪⚪⚪⚪⚪          │
│  ⚪⚪⚪⚪⚪🔵🔵🔵          │
│    50 voitures!          │
│                          │
│ ESC: Skip                │
└──────────────────────────┘
FPS: 60 | Temps: 1.5s/gen
```

---

## ⚡ Performance

**Les deux versions sont maintenant rapides !**

- **Tkinter mode rapide** : 1.2s/génération (sans visualisation)
- **Pygame** : 1.5s/génération (**avec** visualisation de 50 voitures!)

Le léger overhead de Pygame (0.3s) vaut **largement** la visualisation complète !

---

## 🔧 Installation

Les mêmes dépendances pour les deux versions :

```bash
pip install neat-python pygame shapely mathutils
```

---

## 💡 Astuce Pro

**Workflow recommandé** :
1. Utilisez **Pygame** pour les 5 premières générations
   - Vérifiez que tout fonctionne
   - Observez les comportements

2. Si vous voulez juste entraîner sans regarder :
   - Passez à **Tkinter mode rapide**
   - 20% plus rapide

3. Pour présenter/débugger :
   - Toujours **Pygame** !

---

**TL;DR** : Utilisez **Pygame** pour voir l'apprentissage, c'est incroyable ! 🚀🎮
