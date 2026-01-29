# src/logic/constraint_validator.py
"""
Comprehensive constraint validator
Validates all business constraints for scheduling
"""

from typing import List, Dict, Optional, Tuple
from src.logic.conflict_detector import ConflictDetector
from src.logic.time_utils import TimeUtils


class ConstraintValidator:
    """Validates all business constraints for scheduling"""
    
    def __init__(self, existing_seances: List[Dict], existing_reservations: List[Dict] = None,
                 salles: List[Dict] = None, groupes: List[Dict] = None):
        """
        Initialize the validator with existing data
        Args:
            existing_seances: List of existing session dictionaries
            existing_reservations: List of existing reservation dictionaries
            salles: List of room dictionaries
            groupes: List of group dictionaries with id, nom, effectif
        """
        self.existing_seances = existing_seances or []
        self.existing_reservations = existing_reservations or []
        self.salles = {s['id']: s for s in (salles or [])}
        self.groupes = {g['id']: g for g in (groupes or [])}
        
        # Combine approved reservations with sessions for conflict detection
        approved_reservations = [
            {
                'id': r.get('id'),
                'date': r.get('date'),
                'heure_debut': r.get('heure_debut'),
                'heure_fin': r.get('heure_fin'),
                'salle_id': r.get('salle_id'),
                'enseignant_id': r.get('enseignant_id'),
                'groupe_id': None
            }
            for r in (existing_reservations or [])
            if r.get('statut') == 'validee'
        ]
        
        all_commitments = self.existing_seances + approved_reservations
        self.conflict_detector = ConflictDetector(all_commitments)
    
    def validate_seance(self, date: str, heure_debut: str, heure_fin: str,
                       salle_id: Optional[int] = None,
                       enseignant_id: Optional[int] = None,
                       groupe_id: Optional[int] = None,
                       exclude_seance_id: Optional[int] = None) -> Tuple[bool, List[str]]:
        """
        Validate a session against all business constraints
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Validate time range
        if not TimeUtils.is_valid_time_range(heure_debut, heure_fin):
            errors.append("L'heure de début doit être avant l'heure de fin.")
            return False, errors
        
        # 2. Check for overlapping sessions (no overlapping sessions allowed)
        conflicts = self.conflict_detector.detect_all_conflicts(
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            salle_id=salle_id,
            enseignant_id=enseignant_id,
            groupe_id=groupe_id,
            exclude_seance_id=exclude_seance_id
        )
        errors.extend(conflicts)
        
        # 3. Check room capacity if group is specified
        if groupe_id is not None and salle_id is not None:
            groupe = self.groupes.get(groupe_id)
            salle = self.salles.get(salle_id)
            
            if groupe and salle:
                effectif = groupe.get('effectif', 0)
                capacite = salle.get('capacite', 0)
                
                if capacite < effectif:
                    errors.append(
                        f"La capacité de la salle ({capacite}) est insuffisante "
                        f"pour le groupe ({effectif} étudiants)."
                    )
        
        # 4. Validate required fields
        if salle_id is None:
            errors.append("Une salle doit être assignée.")
        
        if enseignant_id is None:
            errors.append("Un enseignant doit être assigné.")
        
        if groupe_id is None:
            errors.append("Un groupe doit être assigné.")
        
        return len(errors) == 0, errors
    
    def validate_no_room_double_booking(self, date: str, heure_debut: str, heure_fin: str,
                                       salle_id: int,
                                       exclude_seance_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate that a room is not double-booked
        Returns (is_valid, error_message)
        """
        conflict = self.conflict_detector.detect_room_conflict(
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            salle_id=salle_id,
            exclude_seance_id=exclude_seance_id
        )
        
        if conflict:
            return False, conflict
        return True, None
    
    def validate_no_teacher_double_booking(self, date: str, heure_debut: str, heure_fin: str,
                                         enseignant_id: int,
                                         exclude_seance_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate that a teacher is not double-booked
        Returns (is_valid, error_message)
        """
        conflict = self.conflict_detector.detect_teacher_conflict(
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            enseignant_id=enseignant_id,
            exclude_seance_id=exclude_seance_id
        )
        
        if conflict:
            return False, conflict
        return True, None
    
    def validate_no_group_double_booking(self, date: str, heure_debut: str, heure_fin: str,
                                        groupe_id: int,
                                        exclude_seance_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate that a group is not double-booked
        Returns (is_valid, error_message)
        """
        conflict = self.conflict_detector.detect_group_conflict(
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            groupe_id=groupe_id,
            exclude_seance_id=exclude_seance_id
        )
        
        if conflict:
            return False, conflict
        return True, None
    
    def validate_room_capacity(self, salle_id: int, groupe_id: int) -> Tuple[bool, Optional[str]]:
        """
        Validate that room capacity fits group size
        Returns (is_valid, error_message)
        """
        salle = self.salles.get(salle_id)
        groupe = self.groupes.get(groupe_id)
        
        if salle is None:
            return False, "Salle introuvable."
        
        if groupe is None:
            return False, "Groupe introuvable."
        
        capacite = salle.get('capacite', 0)
        effectif = groupe.get('effectif', 0)
        
        if capacite < effectif:
            return False, (
                f"La capacité de la salle ({capacite}) est insuffisante "
                f"pour le groupe ({effectif} étudiants)."
            )
        
        return True, None
    
    def validate_all_constraints(self, date: str, heure_debut: str, heure_fin: str,
                                salle_id: Optional[int] = None,
                                enseignant_id: Optional[int] = None,
                                groupe_id: Optional[int] = None,
                                exclude_seance_id: Optional[int] = None) -> Tuple[bool, List[str]]:
        """
        Validate all constraints at once
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate time range
        if not TimeUtils.is_valid_time_range(heure_debut, heure_fin):
            errors.append("L'heure de début doit être avant l'heure de fin.")
            return False, errors
        
        # Check room double booking
        if salle_id is not None:
            is_valid, error = self.validate_no_room_double_booking(
                date, heure_debut, heure_fin, salle_id, exclude_seance_id
            )
            if not is_valid:
                errors.append(error)
        
        # Check teacher double booking
        if enseignant_id is not None:
            is_valid, error = self.validate_no_teacher_double_booking(
                date, heure_debut, heure_fin, enseignant_id, exclude_seance_id
            )
            if not is_valid:
                errors.append(error)
        
        # Check group double booking
        if groupe_id is not None:
            is_valid, error = self.validate_no_group_double_booking(
                date, heure_debut, heure_fin, groupe_id, exclude_seance_id
            )
            if not is_valid:
                errors.append(error)
        
        # Check room capacity
        if salle_id is not None and groupe_id is not None:
            is_valid, error = self.validate_room_capacity(salle_id, groupe_id)
            if not is_valid:
                errors.append(error)
        
        return len(errors) == 0, errors