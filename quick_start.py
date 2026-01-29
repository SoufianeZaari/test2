#!/usr/bin/env python3
# quick_start.py
"""
═══════════════════════════════════════════════════════════════
SCRIPT DE DÉMARRAGE RAPIDE - FST Tanger
Initialise la base de données et lance l'application
═══════════════════════════════════════════════════════════════
"""

import os
import sys

def main():
    print("\n" + "═" * 60)
    print("  🚀 DÉMARRAGE RAPIDE - Gestion Emploi du Temps FSTT")
    print("═" * 60)
    
    # Étape 1: Vérifier si la base de données existe
    db_path = "data/emploi_du_temps.db"
    
    if os.path.exists(db_path):
        print(f"\n✅ Base de données trouvée: {db_path}")
        print("   Pour réinitialiser: supprimer ce fichier et relancer")
    else:
        print("\n📦 Initialisation de la base de données...")
        
        # Import et initialisation
        from src.database import Database
        from src.import_manager import ImportManager
        
        db = Database()
        manager = ImportManager()
        
        # Import CSV
        print("\n📥 Import des données CSV...")
        manager.import_salles('templates_csv/salles.csv')
        manager.import_groupes('templates_csv/groupes.csv')
        manager.import_enseignants('templates_csv/enseignants.csv')
        manager.import_etudiants('templates_csv/etudiants.csv')
        
        # Créer admin
        db.ajouter_utilisateur('Admin', 'System', 'admin@fstt.ac.ma', 'admin123', 'admin', None, None)
        
        # Statistiques
        print("\n✅ Base de données initialisée!")
        print(f"   • Salles: {len(db.get_toutes_salles())}")
        print(f"   • Groupes: {len(db.get_tous_groupes())}")
        print(f"   • Enseignants: {len(db.get_tous_utilisateurs('enseignant'))}")
        print(f"   • Étudiants: {len(db.get_tous_utilisateurs('etudiant'))}")
    
    # Étape 2: Afficher les identifiants
    print("\n" + "─" * 60)
    print("🔐 IDENTIFIANTS DE CONNEXION:")
    print("─" * 60)
    print("   Admin:    admin@fstt.ac.ma / admin123")
    print("   Prof:     mohammed.alami1@uae.ac.ma / prof123")
    print("   Étudiant: mohammed.bennani1@etu.uae.ac.ma / etudiant123")
    print("─" * 60)
    
    # Étape 3: Lancer l'application
    print("\n🚀 Lancement de l'application...")
    print("   (Fermez cette fenêtre pour arrêter l'application)\n")
    
    # Import et lancement
    from PyQt6.QtWidgets import QApplication
    from main import FSSTApplication
    
    app = FSSTApplication()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
