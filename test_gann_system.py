#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que le système GANN est correctement configuré
"""

import sys
import os

# Ajoute le répertoire racine au path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

def test_imports():
    """Teste que tous les imports fonctionnent"""
    print("🔍 Test des imports...")

    try:
        import neat
        print("  ✅ neat-python importé")
    except ImportError as e:
        print(f"  ❌ Erreur import neat: {e}")
        return False

    try:
        from src.car import Car
        print("  ✅ Car importé")
    except ImportError as e:
        print(f"  ❌ Erreur import Car: {e}")
        return False

    try:
        from src.trainer import NEATTrainer
        print("  ✅ NEATTrainer importé")
    except ImportError as e:
        print(f"  ❌ Erreur import NEATTrainer: {e}")
        return False

    try:
        from src.app import App
        print("  ✅ App importé")
    except ImportError as e:
        print(f"  ❌ Erreur import App: {e}")
        return False

    return True


def test_config_file():
    """Teste que le fichier de configuration NEAT existe"""
    print("\n🔍 Test du fichier de configuration...")

    config_path = ROOT_DIR + '/config-neat.txt'

    if not os.path.exists(config_path):
        print(f"  ❌ Fichier config-neat.txt non trouvé: {config_path}")
        return False

    print(f"  ✅ config-neat.txt trouvé")

    # Teste le chargement de la config
    try:
        import neat
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )
        print(f"  ✅ Configuration NEAT chargée")
        print(f"    - Population: {config.pop_size}")
        print(f"    - Inputs: {config.genome_config.num_inputs}")
        print(f"    - Outputs: {config.genome_config.num_outputs}")
        return True
    except Exception as e:
        print(f"  ❌ Erreur chargement config: {e}")
        return False


def test_circuit_file():
    """Teste que le fichier de circuit existe"""
    print("\n🔍 Test du circuit par défaut...")

    circuit_path = ROOT_DIR + '/saves/circuit01.txt'

    if not os.path.exists(circuit_path):
        print(f"  ❌ Circuit circuit01.txt non trouvé: {circuit_path}")
        return False

    print(f"  ✅ circuit01.txt trouvé")

    # Compte le nombre de segments
    with open(circuit_path, 'r') as f:
        lines = f.readlines()
        segments_count = len([l for l in lines if l.strip()])

    print(f"    - Nombre de segments: {segments_count}")
    return True


def test_car_methods():
    """Teste que les nouvelles méthodes de Car existent"""
    print("\n🔍 Test des méthodes de Car...")

    from src.car import Car

    # Crée une instance factice (sans canvas)
    class FakeCanvas:
        def winfo_width(self):
            return 800
        def winfo_height(self):
            return 650
        def after(self, delay, func):
            pass
        def find_withtag(self, tag):
            return []

    try:
        car = Car(FakeCanvas())

        # Vérifie les attributs
        assert hasattr(car, 'is_alive'), "Attribut is_alive manquant"
        assert hasattr(car, 'fitness'), "Attribut fitness manquant"
        assert hasattr(car, 'distance_traveled'), "Attribut distance_traveled manquant"
        assert hasattr(car, 'is_autonomous'), "Attribut is_autonomous manquant"
        print("  ✅ Attributs GANN présents")

        # Vérifie les méthodes
        assert hasattr(car, 'get_radar_distances'), "Méthode get_radar_distances manquante"
        assert hasattr(car, 'drive_autonomous'), "Méthode drive_autonomous manquante"
        assert hasattr(car, 'check_collision_with_track'), "Méthode check_collision_with_track manquante"
        print("  ✅ Méthodes GANN présentes")

        # Teste get_radar_distances
        distances = car.get_radar_distances()
        assert len(distances) == 5, f"get_radar_distances devrait retourner 5 valeurs, a retourné {len(distances)}"
        print(f"  ✅ get_radar_distances() retourne 5 valeurs")

        return True
    except AssertionError as e:
        print(f"  ❌ {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        return False


def test_trainer_methods():
    """Teste que les méthodes du Trainer existent"""
    print("\n🔍 Test des méthodes de NEATTrainer...")

    from src.trainer import NEATTrainer

    try:
        # Vérifie que la classe existe
        assert hasattr(NEATTrainer, 'eval_genomes'), "Méthode eval_genomes manquante"
        assert hasattr(NEATTrainer, 'run_generation_simulation'), "Méthode run_generation_simulation manquante"
        assert hasattr(NEATTrainer, 'calculate_fitness'), "Méthode calculate_fitness manquante"
        assert hasattr(NEATTrainer, 'train'), "Méthode train manquante"
        assert hasattr(NEATTrainer, 'save_genome'), "Méthode save_genome manquante"
        assert hasattr(NEATTrainer, 'load_genome'), "Méthode load_genome manquante"
        assert hasattr(NEATTrainer, 'test_genome'), "Méthode test_genome manquante"

        print("  ✅ Toutes les méthodes sont présentes")
        return True
    except AssertionError as e:
        print(f"  ❌ {e}")
        return False


def main():
    """Lance tous les tests"""
    print("=" * 60)
    print("🧪 Test du Système GANN - RaceCircuitGANN")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Configuration NEAT", test_config_file()))
    results.append(("Circuit par défaut", test_circuit_file()))
    results.append(("Méthodes Car", test_car_methods()))
    results.append(("Méthodes NEATTrainer", test_trainer_methods()))

    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("=" * 60)
        print("\n✅ Le système GANN est correctement configuré.")
        print("\n📖 Pour démarrer l'entraînement :")
        print("   1. Lancez: python src/main.py")
        print("   2. Cliquez sur 'Train AI'")
        print("\n📚 Consultez GANN_GUIDE.md pour plus d'informations")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("=" * 60)
        print("\n⚠️  Corrigez les erreurs avant de lancer l'entraînement.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
