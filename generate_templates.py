import csv
import os
# On importe les variables de configuration pour être sûr d'avoir les mêmes colonnes partout
from config import TEMPLATES_CSV_FOLDER, COLONNES_ETUDIANTS, COLONNES_ENSEIGNANTS, COLONNES_SALLES, COLONNES_GROUPES

def generate_csv_templates():
    """
    Crée automatiquement le dossier templates et les fichiers CSV vides 
    avec les entêtes corrects pour la FSTT.
    """
    # 1. Création du dossier s'il n'existe pas
    if not os.path.exists(TEMPLATES_CSV_FOLDER):
        os.makedirs(TEMPLATES_CSV_FOLDER)
        print(f"📁 Dossier créé : {TEMPLATES_CSV_FOLDER}")

    # 2. Définition des fichiers à générer
    # Le format est : { "nom_du_fichier.csv": [liste_des_colonnes] }
    templates = {
        "etudiants.csv": COLONNES_ETUDIANTS,
        "enseignants.csv": COLONNES_ENSEIGNANTS,
        "salles.csv": COLONNES_SALLES,
        "groupes.csv": COLONNES_GROUPES
    }

    print("🚀 Génération des modèles CSV en cours...")

    # 3. Boucle de création des fichiers
    for filename, headers in templates.items():
        filepath = os.path.join(TEMPLATES_CSV_FOLDER, filename)
        
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # On écrit uniquement la ligne d'entête
                writer.writerow(headers)
            print(f"  ✅ Modèle généré : {filename}")
        except Exception as e:
            print(f"  ❌ Erreur lors de la création de {filename} : {e}")

    print("\n✨ Terminé ! Les fichiers sont prêts à être remplis dans 'templates_csv/'.")

if __name__ == "__main__":
    generate_csv_templates()