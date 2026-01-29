# src/import_manager.py
import csv
import os
from src.database import Database
from config import COLONNES_ETUDIANTS, COLONNES_ENSEIGNANTS, COLONNES_SALLES, COLONNES_GROUPES

# Default filière level for auto-created filières during CSV import
# L3 (Licence 3) is the most common level at FSTT for undergraduate programs
DEFAULT_FILIERE_NIVEAU = "L3"

class ImportManager:
    """Classe pour gérer les imports massifs CSV de la FSTT"""
    
    def __init__(self):
        self.db = Database()
    
    def parse_csv(self, fichier_path):
        """Lit un fichier CSV et retourne une liste de dictionnaires"""
        try:
            with open(fichier_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du fichier : {e}")
            return None

    def valider_colonnes(self, donnees, colonnes_requises):
        """Vérifie si le CSV possède bien toutes les colonnes nécessaires"""
        if not donnees: 
            return False
        colonnes_fichier = donnees[0].keys()
        manquantes = [col for col in colonnes_requises if col not in colonnes_fichier]
        if manquantes:
            print(f"❌ Colonnes manquantes : {', '.join(manquantes)}")
            return False
        return True

    def import_salles(self, fichier_path):
        """Importe les salles et remplace les anciennes"""
        donnees = self.parse_csv(fichier_path)
        
        if not donnees:
            return False
            
        if not self.valider_colonnes(donnees, COLONNES_SALLES):
            print("❌ Erreur : Colonnes manquantes dans le fichier Salles.")
            return False

        # 1. Sauvegarde de sécurité
        self.db.sauvegarder_bdd()
        
        # 2. Nettoyage
        self.db.supprimer_toutes_salles()
        
        # 3. Insertion
        succes = 0
        for ligne in donnees:
            res = self.db.ajouter_salle(
                ligne['nom'], 
                int(ligne['capacite']), 
                ligne['type_salle'], 
                ligne.get('equipements', '')
            )
            if res: 
                succes += 1
            
        # 4. Historique (ID 1 par défaut pour l'admin système)
        self.db.ajouter_historique_import("Salles", succes, os.path.basename(fichier_path), 1)
        print(f"✅ Import réussi : {succes} salles ajoutées.")
        return True

    def import_enseignants(self, fichier_path, mode='remplacer'):
        """
        Importe les enseignants avec durée max par jour
        
        Args:
            fichier_path: Chemin du CSV
            mode: 'remplacer' (supprime puis ajoute) ou 'fusionner' (ajoute seulement)
        """
        donnees = self.parse_csv(fichier_path)
        
        if not donnees:
            return False
            
        if not self.valider_colonnes(donnees, COLONNES_ENSEIGNANTS):
            print("❌ Erreur : Colonnes manquantes dans le fichier Enseignants.")
            return False

        self.db.sauvegarder_bdd()
        
        if mode == 'remplacer':
            self.db.supprimer_tous_utilisateurs_type('enseignant')
            print("🗑️  Anciennes données supprimées")
        else:
            print("➕ Mode fusion : ajout sans suppression")
        
        succes = 0
        for ligne in donnees:
            # Récupérer la durée max ou utiliser 480 min (8h) par défaut
            duree_max = int(ligne.get('duree_max_jour', 480))
            
            res = self.db.ajouter_utilisateur(
                ligne['nom'], 
                ligne['prenom'], 
                ligne['email'],
                "prof123",  # Mot de passe par défaut
                "enseignant", 
                ligne['specialite'],
                None,  # pas de groupe
                duree_max  # Durée max en minutes
            )
            if res: 
                succes += 1
            
        self.db.ajouter_historique_import("Enseignants", succes, os.path.basename(fichier_path), 1)
        print(f"✅ Import réussi : {succes} enseignants ajoutés.")
        return True

    def import_groupes(self, fichier_path):
        """Importe les groupes et remplace les anciens - Crée automatiquement les filières si nécessaire"""
        donnees = self.parse_csv(fichier_path)
        
        if not donnees:
            return False
            
        if not self.valider_colonnes(donnees, COLONNES_GROUPES):
            print("❌ Erreur : Colonnes manquantes dans le fichier Groupes.")
            return False

        self.db.sauvegarder_bdd()
        self.db.supprimer_tous_groupes()
        
        succes = 0
        erreurs = 0
        filieres_creees = 0
        
        for ligne in donnees:
            # 1. Récupérer ou créer la filière
            filiere_nom = ligne['filiere'].strip()
            filiere = self.db.get_filiere_by_nom(filiere_nom)
            
            if not filiere:
                # Auto-créer la filière avec le niveau par défaut
                filiere_id = self.db.ajouter_filiere(filiere_nom, DEFAULT_FILIERE_NIVEAU)
                if filiere_id:
                    print(f"✅ Filière créée automatiquement : '{filiere_nom}' (Niveau: {DEFAULT_FILIERE_NIVEAU})")
                    filieres_creees += 1
                else:
                    print(f"⚠️ Impossible de créer la filière '{filiere_nom}' pour le groupe '{ligne['nom']}'")
                    erreurs += 1
                    continue
            else:
                filiere_id = filiere[0]  # ID de la filière
            
            # 2. Ajouter le groupe
            res = self.db.ajouter_groupe(
                ligne['nom'],
                int(ligne['effectif']),
                filiere_id
            )
            
            if res:
                succes += 1
            else:
                erreurs += 1
        
        self.db.ajouter_historique_import("Groupes", succes, os.path.basename(fichier_path), 1)
        
        if filieres_creees > 0:
            print(f"📚 {filieres_creees} filières créées automatiquement.")
        
        if erreurs > 0:
            print(f"⚠️ Import partiel : {succes} groupes ajoutés, {erreurs} erreurs.")
        else:
            print(f"✅ Import réussi : {succes} groupes ajoutés.")
        
        return True

    def import_etudiants(self, fichier_path):
        """Importe les étudiants et remplace les anciens"""
        donnees = self.parse_csv(fichier_path)
        
        if not donnees:
            return False
            
        if not self.valider_colonnes(donnees, COLONNES_ETUDIANTS):
            print("❌ Erreur : Colonnes manquantes dans le fichier Étudiants.")
            return False

        self.db.sauvegarder_bdd()
        self.db.supprimer_tous_utilisateurs_type('etudiant')
        
        succes = 0
        erreurs = 0
        
        for ligne in donnees:
            # 1. Récupérer le groupe par son nom
            groupe = self.db.get_groupe_by_nom(ligne['groupe'])
            
            if not groupe:
                print(f"⚠️ Groupe '{ligne['groupe']}' introuvable pour {ligne['nom']} {ligne['prenom']}")
                erreurs += 1
                continue
            
            # 2. Ajouter l'étudiant
            res = self.db.ajouter_utilisateur(
                ligne['nom'],
                ligne['prenom'],
                ligne['email'],
                "etudiant123",  # Mot de passe par défaut
                "etudiant",
                None,  # pas de spécialité
                groupe[0]  # ID du groupe
            )
            
            if res:
                succes += 1
            else:
                erreurs += 1
        
        self.db.ajouter_historique_import("Étudiants", succes, os.path.basename(fichier_path), 1)
        
        if erreurs > 0:
            print(f"⚠️ Import partiel : {succes} étudiants ajoutés, {erreurs} erreurs.")
        else:
            print(f"✅ Import réussi : {succes} étudiants ajoutés.")
        
        return True

    def import_tous_fichiers(self, dossier_templates):
        """Importe automatiquement tous les CSV du dossier templates"""
        print("🚀 Lancement de l'import complet...")
        
        fichiers = {
            'salles.csv': self.import_salles,
            'enseignants.csv': self.import_enseignants,
            'groupes.csv': self.import_groupes,
            'etudiants.csv': self.import_etudiants
        }
        
        resultats = {}
        
        for nom_fichier, fonction_import in fichiers.items():
            chemin = os.path.join(dossier_templates, nom_fichier)
            
            if os.path.exists(chemin):
                print(f"\n📄 Import de {nom_fichier}...")
                resultats[nom_fichier] = fonction_import(chemin)
            else:
                print(f"⚠️ Fichier {nom_fichier} introuvable, ignoré.")
                resultats[nom_fichier] = False
        
        print("\n" + "="*50)
        print("📊 RÉSUMÉ DE L'IMPORT")
        print("="*50)
        for fichier, succes in resultats.items():
            statut = "✅ Réussi" if succes else "❌ Échoué"
            print(f"{fichier:20} : {statut}")
        
        return resultats