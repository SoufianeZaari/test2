# src/logic/reservation_validator.py
"""
Reservation validation service
Validates reservation requests according to business rules:
- 2-hour advance notice requirement
- Conflict detection
- Room capacity validation
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from src.logic.conflict_detector import ConflictDetector
from src.logic.time_utils import TimeUtils


class ReservationValidator:
    """Validates reservation requests against business constraints"""
    
    # Minimum advance notice required (in hours)
    MIN_ADVANCE_HOURS = 2
    
    def __init__(self, existing_seances: List[Dict], existing_reservations: List[Dict] = None):
        """
        Initialize the validator with existing data
        Args:
            existing_seances: List of existing session dictionaries
            existing_reservations: List of existing reservation dictionaries (approved only)
        """
        self.existing_seances = existing_seances or []
        self.existing_reservations = existing_reservations or []
        
        # Combine approved reservations with sessions for conflict detection
        approved_reservations = [
            {
                'id': r.get('id'),
                'date': r.get('date'),
                'heure_debut': r.get('heure_debut'),
                'heure_fin': r.get('heure_fin'),
                'salle_id': r.get('salle_id'),
                'enseignant_id': r.get('enseignant_id'),
                'groupe_id': None  # Reservations don't have groups
            }
            for r in (existing_reservations or [])
            if r.get('statut') == 'validee'
        ]
        
        # Create conflict detector with all existing commitments
        all_commitments = self.existing_seances + approved_reservations
        self.conflict_detector = ConflictDetector(all_commitments)
    
    def validate_reservation_request(self, enseignant_id: int, salle_id: int,
                                     date: str, heure_debut: str, heure_fin: str,
                                     groupe_id: Optional[int] = None,
                                     groupe_effectif: Optional[int] = None,
                                     salle_capacite: Optional[int] = None) -> Tuple[bool, List[str]]:
        """
        Validate a reservation request
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # 1. Validate time range format
        if not TimeUtils.is_valid_time_range(heure_debut, heure_fin):
            errors.append("L'heure de début doit être avant l'heure de fin.")
            return False, errors
        
        # 2. Check 2-hour advance notice
        advance_error = self._check_advance_notice(date, heure_debut)
        if advance_error:
            errors.append(advance_error)
        
        # 3. Check room capacity (if group size provided)
        if groupe_effectif is not None and salle_capacite is not None:
            if salle_capacite < groupe_effectif:
                errors.append(
                    f"La capacité de la salle ({salle_capacite}) est insuffisante "
                    f"pour le groupe ({groupe_effectif} étudiants)."
                )
        
        # 4. Check conflicts
        conflicts = self.conflict_detector.detect_all_conflicts(
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            salle_id=salle_id,
            enseignant_id=enseignant_id,
            groupe_id=groupe_id
        )
        errors.extend(conflicts)
        
        return len(errors) == 0, errors
    
    def _check_advance_notice(self, date: str, heure_debut: str) -> Optional[str]:
        """
        Check if reservation is made at least 2 hours in advance
        Returns error message if validation fails, None otherwise
        """
        try:
            # Parse date and time
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            time_obj = TimeUtils.parse_time(heure_debut)
            
            if time_obj is None:
                return "Format d'heure invalide."
            
            # Combine date and time
            reservation_datetime = datetime.combine(date_obj.date(), time_obj)
            
            # Get current datetime
            now = datetime.now()
            
            # Calculate time difference
            time_diff = reservation_datetime - now
            
            # Check if at least 2 hours in advance
            if time_diff < timedelta(hours=self.MIN_ADVANCE_HOURS):
                return (
                    f"Les réservations doivent être faites au moins {self.MIN_ADVANCE_HOURS} heures "
                    f"à l'avance. Temps restant: {self._format_time_diff(time_diff)}"
                )
            
            return None
            
        except ValueError as e:
            return f"Format de date invalide: {date}"
        except Exception as e:
            return f"Erreur lors de la validation: {str(e)}"
    
    def _format_time_diff(self, time_diff: timedelta) -> str:
        """Format time difference for display"""
        if time_diff.total_seconds() < 0:
            return "déjà passé"
        
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"
    
    def validate_reservation_approval(self, reservation: Dict,
                                     salle_capacite: Optional[int] = None,
                                     groupe_effectif: Optional[int] = None) -> Tuple[bool, List[str]]:
        """
        Validate if a reservation can be approved
        This is called when admin tries to approve a reservation
        """
        errors = []
        
        # Check conflicts at approval time (may have changed since request)
        conflicts = self.conflict_detector.detect_all_conflicts(
            date=reservation.get('date'),
            heure_debut=reservation.get('heure_debut'),
            heure_fin=reservation.get('heure_fin'),
            salle_id=reservation.get('salle_id'),
            enseignant_id=reservation.get('enseignant_id'),
            groupe_id=None  # Reservations don't have groups
        )
        errors.extend(conflicts)
        
        # Check capacity if provided
        if groupe_effectif is not None and salle_capacite is not None:
            if salle_capacite < groupe_effectif:
                errors.append(
                    f"La capacité de la salle ({salle_capacite}) est insuffisante "
                    f"pour le groupe ({groupe_effectif} étudiants)."
                )
        
        return len(errors) == 0, errors