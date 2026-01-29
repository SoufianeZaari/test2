# src/logic/csv_import_service.py
"""
CSV Import Service - Backend logic for importing CSV files
Handles import of students, teachers, groups, and rooms CSV files
After import, automatically generates weekly timetable
"""

import csv
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from src.logic.schedule_generator import ScheduleGenerator
from src.logic.conflict_detector import ConflictDetector


class CSVImportService:
    """Service for importing CSV files and auto-generating timetable"""
    
    # Expected CSV column names
    COLUMNS_ETUDIANTS = ['nom', 'prenom', 'email', 'groupe']
    COLUMNS_ENSEIGNANTS = ['nom', 'prenom', 'email', 'specialite']
    COLUMNS_GROUPES = ['nom', 'effectif', 'filiere']
    COLUMNS_SALLES = ['nom', 'capacite', 'type_salle', 'equipements']
    
    def __init__(self, db):
        """
        Initialize the CSV import service
        Args:
            db: Database instance
        """
        self.db = db
        self.errors = []
        self.warnings = []
    
    def import_all_csv_files(self, liste_etudiants_path: str,
                            liste_enseignants_path: str,
                            groupes_path: str,
                            salles_path: str,
                            auto_generate_timetable: bool = True,
                            semaine_debut: str = None) -> Dict:
        """
        Imports all 4 CSV files and optionally generates timetable
        Args:
            liste_etudiants_path: Path to liste_etudiants.csv
            liste_enseignants_path: Path to liste_enseignants.csv
            groupes_path: Path to groupes.csv
            salles_path: Path to salles.csv
            auto_generate_timetable: Whether to auto-generate timetable after import
            semaine_debut: Start week date for timetable generation
        Returns:
            Dict with 'success', 'imported', 'generated', 'errors', 'warnings'
        """
        self.errors = []
        self.warnings = []
        imported_counts = {
            'etudiants': 0,
            'enseignants': 0,
            'groupes': 0,
            'salles': 0
        }
        
        # Import in order: salles, groupes, enseignants, etudiants
        # (dependencies first)
        
        # 1. Import salles
        if os.path.exists(salles_path):
            count = self._import_salles(salles_path)
            if count is not None:
                imported_counts['salles'] = count
        else:
            self.errors.append(f"Fichier introuvable: {salles_path}")
        
        # 2. Import groupes (needs filieres to exist)
        if os.path.exists(groupes_path):
            count = self._import_groupes(groupes_path)
            if count is not None:
                imported_counts['groupes'] = count
        else:
            self.errors.append(f"Fichier introuvable: {groupes_path}")
        
        # 3. Import enseignants
        if os.path.exists(liste_enseignants_path):
            count = self._import_enseignants(liste_enseignants_path)
            if count is not None:
                imported_counts['enseignants'] = count
        else:
            self.errors.append(f"Fichier introuvable: {liste_enseignants_path}")
        
        # 4. Import etudiants (needs groupes to exist)
        if os.path.exists(liste_etudiants_path):
            count = self._import_etudiants(liste_etudiants_path)
            if count is not None:
                imported_counts['etudiants'] = count
        else:
            self.errors.append(f"Fichier introuvable: {liste_etudiants_path}")
        
        # Auto-generate timetable if requested
        generated_count = 0
        if auto_generate_timetable and len(self.errors) == 0:
            generated_count = self._auto_generate_timetable(semaine_debut)
        
        success = len(self.errors) == 0
        
        return {
            'success': success,
            'imported': imported_counts,
            'generated': generated_count,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def _parse_csv(self, filepath: str) -> Optional[List[Dict]]:
        """Parse CSV file and return list of dictionaries"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            self.errors.append(f"Erreur lecture {filepath}: {e}")
            return None
    
    def _validate_columns(self, data: List[Dict], required_columns: List[str],
                         file_type: str) -> bool:
        """Validate CSV has required columns"""
        if not data:
            self.errors.append(f"{file_type}: Fichier vide")
            return False
        
        file_columns = list(data[0].keys())
        missing = [col for col in required_columns if col not in file_columns]
        
        if missing:
            self.errors.append(
                f"{file_type}: Colonnes manquantes: {', '.join(missing)}"
            )
            return False
        
        return True
    
    def _import_salles(self, filepath: str) -> Optional[int]:
        """Import rooms from CSV"""
        data = self._parse_csv(filepath)
        if not data:
            return None
        
        if not self._validate_columns(data, self.COLUMNS_SALLES, "Salles"):
            return None
        
        # Backup database
        self.db.sauvegarder_bdd()
        
        # Delete existing rooms
        self.db.supprimer_toutes_salles()
        
        imported = 0
        for row in data:
            try:
                nom = row['nom'].strip()
                capacite = int(row['capacite'])
                type_salle = row['type_salle'].strip()
                equipements = row.get('equipements', '').strip()
                
                salle_id = self.db.ajouter_salle(nom, capacite, type_salle, equipements)
                if salle_id:
                    imported += 1
            except Exception as e:
                self.warnings.append(f"Salle ligne {imported + 1}: {e}")
        
        return imported
    
    def _import_groupes(self, filepath: str) -> Optional[int]:
        """Import groups from CSV"""
        data = self._parse_csv(filepath)
        if not data:
            return None
        
        if not self._validate_columns(data, self.COLUMNS_GROUPES, "Groupes"):
            return None
        
        # Backup database
        self.db.sauvegarder_bdd()
        
        # Delete existing groups
        self.db.supprimer_tous_groupes()
        
        imported = 0
        for row in data:
            try:
                nom = row['nom'].strip()
                effectif = int(row['effectif'])
                filiere_nom = row['filiere'].strip()
                
                # Get or create filiere
                filiere = self.db.get_filiere_by_nom(filiere_nom)
                if not filiere:
                    # Create filiere (extract niveau from name or use default)
                    # Assuming format like "Informatique L3" or just name
                    niveau = "L3"  # Default, could be extracted from name
                    filiere_id = self.db.ajouter_filiere(filiere_nom, niveau)
                else:
                    filiere_id = filiere['id']
                
                groupe_id = self.db.ajouter_groupe(nom, effectif, filiere_id)
                if groupe_id:
                    imported += 1
            except Exception as e:
                self.warnings.append(f"Groupe ligne {imported + 1}: {e}")
        
        return imported
    
    def _import_enseignants(self, filepath: str) -> Optional[int]:
        """Import teachers from CSV"""
        data = self._parse_csv(filepath)
        if not data:
            return None
        
        if not self._validate_columns(data, self.COLUMNS_ENSEIGNANTS, "Enseignants"):
            return None
        
        # Backup database
        self.db.sauvegarder_bdd()
        
        # Delete existing teachers
        self.db.supprimer_tous_utilisateurs_type('enseignant')
        
        imported = 0
        for row in data:
            try:
                nom = row['nom'].strip()
                prenom = row['prenom'].strip()
                email = row['email'].strip()
                specialite = row['specialite'].strip()
                
                # Default password
                password = "enseignant123"
                
                user_id = self.db.ajouter_utilisateur(
                    nom, prenom, email, password, "enseignant", specialite, None
                )
                if user_id:
                    imported += 1
            except Exception as e:
                self.warnings.append(f"Enseignant ligne {imported + 1}: {e}")
        
        return imported
    
    def _import_etudiants(self, filepath: str) -> Optional[int]:
        """Import students from CSV"""
        data = self._parse_csv(filepath)
        if not data:
            return None
        
        if not self._validate_columns(data, self.COLUMNS_ETUDIANTS, "Étudiants"):
            return None
        
        # Backup database
        self.db.sauvegarder_bdd()
        
        # Delete existing students
        self.db.supprimer_tous_utilisateurs_type('etudiant')
        
        imported = 0
        for row in data:
            try:
                nom = row['nom'].strip()
                prenom = row['prenom'].strip()
                email = row['email'].strip()
                groupe_nom = row['groupe'].strip()
                
                # Get group
                groupe = self.db.get_groupe_by_nom(groupe_nom)
                if not groupe:
                    self.warnings.append(
                        f"Étudiant {nom} {prenom}: Groupe '{groupe_nom}' introuvable"
                    )
                    continue
                
                # Default password
                password = "etudiant123"
                
                user_id = self.db.ajouter_utilisateur(
                    nom, prenom, email, password, "etudiant", None, groupe['id']
                )
                if user_id:
                    imported += 1
            except Exception as e:
                self.warnings.append(f"Étudiant ligne {imported + 1}: {e}")
        
        return imported
    
    def _auto_generate_timetable(self, semaine_debut: str = None) -> int:
        """
        Auto-generates weekly timetable after CSV import
        This is a placeholder - actual generation would need course data
        Args:
            semaine_debut: Start week date
        Returns:
            Number of sessions generated
        """
        # This would need course/subject data to generate timetable
        # For now, return 0 as placeholder
        # The actual implementation would:
        # 1. Get all groups
        # 2. Get all teachers
        # 3. Generate sessions for each group-teacher combination
        # 4. Respect 8h/week teacher limit
        
        if not semaine_debut:
            # Start from next Monday
            today = datetime.now()
            days_ahead = (7 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            next_monday = today + timedelta(days=days_ahead)
            semaine_debut = next_monday.strftime("%Y-%m-%d")
        
        # Get existing seances for conflict detection
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM seances")
        existing_seances = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Initialize schedule generator
        generator = ScheduleGenerator(self.db, existing_seances, [])
        
        # Track teacher hours per week
        teacher_weekly_hours = {}
        
        # Get all groups and teachers
        groupes = self.db.get_tous_groupes()
        enseignants = self.db.get_tous_utilisateurs(type_user='enseignant')
        
        generated_count = 0
        
        # Note: This is a simplified example
        # Real implementation would need course/subject data from another source
        # For now, this serves as the structure
        
        return generated_count

