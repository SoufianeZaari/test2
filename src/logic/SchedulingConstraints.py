# src/logic/scheduling_constraints.py
"""
Logique de validation et contraintes de planification.
Gère les règles métiers : Heures de travail, Capacité, Durée min/max.
"""

from typing import List, Dict, Optional, Tuple
import config  # On utilise la config pour les heures de travail
from src.logic.time_utils import TimeUtils
from src.logic.conflict_detector import ConflictDetector

class SchedulingConstraints:
    """Gère les contraintes de l'emploi du temps"""
    
    def __init__(self):
        """
        Initialise les contraintes en se basant sur config.py
        """
        # On récupère l'heure de début du premier créneau et fin du dernier
        # config.CRENEAUX_HORAIRES est une liste de tuples [("08:30", "10:15"), ...]
        if config.CRENEAUX_HORAIRES:
            self.work_start = config.CRENEAUX_HORAIRES[0][0]  # Ex: "08:30"
            self.work_end = config.CRENEAUX_HORAIRES[-1][1]   # Ex: "18:15"
        else:
            # Valeurs par défaut si config vide
            self.work_start = "08:00"
            self.work_end = "19:00"

        # Durée minimale et maximale d'une séance (en minutes)
        self.min_duration = 30   # 30 min
        self.max_duration = 240  # 4 heures
    
    def validate_session(self, date: str, heure_debut: str, heure_fin: str,
                        salle_id: Optional[int] = None,
                        enseignant_id: Optional[int] = None,
                        groupe_id: Optional[int] = None,
                        salle_capacite: Optional[int] = None,
                        groupe_effectif: Optional[int] = None,
                        existing_seances: Optional[List[Dict]] = None,
                        exclude_seance_id: Optional[int] = None) -> Tuple[bool, List[str]]:
        """
        Validation complète d'une séance (Règles + Conflits)
        Retourne: (True/False, Liste des erreurs)
        """
        errors = []
        
        # 1. Validation de l'horaire (Règles de base)
        is_time_valid, time_error = self.validate_time_slot(heure_debut, heure_fin)
        if not is_time_valid:
            errors.append(time_error)
        
        # 2. Validation de la capacité (Si les infos sont fournies)
        if salle_capacite is not None and groupe_effectif is not None:
            is_cap_valid, cap_error = self.validate_room_capacity(salle_capacite, groupe_effectif)
            if not is_cap_valid:
                errors.append(cap_error)
        
        # 3. Détection de Conflits (Si on a la liste des séances existantes)
        # C'est ici qu'on appelle le ConflictDetector qu'on a créé avant
        if existing_seances is not None:
            detector = ConflictDetector(existing_seances)
            conflicts = detector.detect_all_conflicts(
                date, heure_debut, heure_fin,
                salle_id, enseignant_id, groupe_id,
                exclude_seance_id
            )
            errors.extend(conflicts)
        
        return len(errors) == 0, errors

    def validate_time_slot(self, heure_debut: str, heure_fin: str) -> Tuple[bool, Optional[str]]:
        """Vérifie si l'horaire est valide (Format, Ordre, Heures de travail, Durée)"""
        
        # A. Format et Ordre
        if not TimeUtils.is_valid_time_range(heure_debut, heure_fin):
            return False, "L'heure de début doit être avant l'heure de fin."
        
        # B. Heures de travail (Pas avant 8h30, pas après 18h15)
        if not self.is_within_working_hours(heure_debut, heure_fin):
            return False, f"L'horaire doit être compris entre {self.work_start} et {self.work_end}."
        
        # C. Durée (Pas trop court, pas trop long)
        duration = TimeUtils.calculate_duration(heure_debut, heure_fin)
        if duration < self.min_duration:
            return False, f"La séance est trop courte (Min: {self.min_duration} min)."
        
        if duration > self.max_duration:
            return False, f"La séance est trop longue (Max: {self.max_duration/60} heures)."
        
        return True, None

    def validate_room_capacity(self, salle_capacite: int, groupe_effectif: int) -> Tuple[bool, Optional[str]]:
        """Vérifie si la salle est assez grande pour le groupe"""
        if salle_capacite < groupe_effectif:
            return False, f"Capacité insuffisante : La salle ({salle_capacite} places) est trop petite pour le groupe ({groupe_effectif} étudiants)."
        return True, None

    def is_within_working_hours(self, heure_debut: str, heure_fin: str) -> bool:
        """Vérifie si le créneau est dans les heures d'ouverture"""
        # On utilise TimeUtils pour comparer les minutes
        start_min = TimeUtils.time_to_minutes(heure_debut)
        end_min = TimeUtils.time_to_minutes(heure_fin)
        work_start_min = TimeUtils.time_to_minutes(self.work_start)
        work_end_min = TimeUtils.time_to_minutes(self.work_end)
        
        if None in [start_min, end_min, work_start_min, work_end_min]:
            return False
        
        return start_min >= work_start_min and end_min <= work_end_min

    def get_duration_minutes(self, heure_debut: str, heure_fin: str) -> int:
        """Helper pour avoir la durée"""
        return TimeUtils.calculate_duration(heure_debut, heure_fin)