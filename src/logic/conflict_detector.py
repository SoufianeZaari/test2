# src/logic/conflict_detector.py
"""
Conflict detection logic for scheduling
Detects conflicts between teachers, rooms, groups, and time slots
"""

from typing import List, Dict, Optional, Tuple
# Import absolu pour éviter les erreurs de chemin
from src.logic.time_utils import TimeSlot, TimeUtils


class ConflictDetector:
    """Detects scheduling conflicts for teachers, rooms, groups, and time slots"""
    
    # [MODIFICATION] La durée de la pause obligatoire entre deux séances (en minutes)
    PAUSE_MINUTES = 10

    def __init__(self, existing_seances: List[Dict]):
        """
        Initialize the conflict detector with existing sessions
        Args:
            existing_seances: List of existing session dictionaries
        """
        self.existing_seances = existing_seances or []
    
    def detect_all_conflicts(self, date: str, heure_debut: str, heure_fin: str,
                            salle_id: Optional[int] = None,
                            enseignant_id: Optional[int] = None,
                            groupe_id: Optional[int] = None,
                            exclude_seance_id: Optional[int] = None) -> List[str]:
        """
        Detect all conflicts for a given time slot and resources
        Returns: List of conflict messages (empty if no conflicts)
        """
        conflicts = []
        
        # Validate time range
        if not TimeUtils.is_valid_time_range(heure_debut, heure_fin):
            conflicts.append("Erreur: L'heure de début doit être avant l'heure de fin.")
            return conflicts
        
        # Check room conflict
        if salle_id is not None:
            room_conflict = self.detect_room_conflict(
                date, heure_debut, heure_fin, salle_id, exclude_seance_id
            )
            if room_conflict:
                conflicts.append(room_conflict)
        
        # Check teacher conflict
        if enseignant_id is not None:
            teacher_conflict = self.detect_teacher_conflict(
                date, heure_debut, heure_fin, enseignant_id, exclude_seance_id
            )
            if teacher_conflict:
                conflicts.append(teacher_conflict)
        
        # Check group conflict
        if groupe_id is not None:
            group_conflict = self.detect_group_conflict(
                date, heure_debut, heure_fin, groupe_id, exclude_seance_id
            )
            if group_conflict:
                conflicts.append(group_conflict)
        
        return conflicts
    
    def detect_room_conflict(self, date: str, heure_debut: str, heure_fin: str,
                           salle_id: int, exclude_seance_id: Optional[int] = None) -> Optional[str]:
        """Detect if a room is already occupied (considering pause time)"""
        new_slot = TimeSlot(date, heure_debut, heure_fin)
        
        for seance in self.existing_seances:
            if exclude_seance_id is not None and seance.get('id') == exclude_seance_id:
                continue
            
            if seance.get('salle_id') == salle_id:
                existing_slot = TimeSlot(
                    seance.get('date', ''),
                    seance.get('heure_debut', ''),
                    seance.get('heure_fin', '')
                )
                
                # [MODIF] On passe min_pause ici
                if new_slot.overlaps_with(existing_slot, min_pause=self.PAUSE_MINUTES):
                    return (f"Salle occupée: La salle {salle_id} est prise ou en pause ({self.PAUSE_MINUTES}min) "
                            f"autour de {existing_slot}")
        return None
    
    def detect_teacher_conflict(self, date: str, heure_debut: str, heure_fin: str,
                               enseignant_id: int, exclude_seance_id: Optional[int] = None) -> Optional[str]:
        """Detect if a teacher is already occupied (considering pause time)"""
        new_slot = TimeSlot(date, heure_debut, heure_fin)
        
        for seance in self.existing_seances:
            if exclude_seance_id is not None and seance.get('id') == exclude_seance_id:
                continue
            
            if seance.get('enseignant_id') == enseignant_id:
                existing_slot = TimeSlot(
                    seance.get('date', ''),
                    seance.get('heure_debut', ''),
                    seance.get('heure_fin', '')
                )
                
                # [MODIF] On passe min_pause ici
                if new_slot.overlaps_with(existing_slot, min_pause=self.PAUSE_MINUTES):
                    return (f"Professeur occupé: L'enseignant {enseignant_id} a un cours ou une pause "
                            f"autour de {existing_slot}")
        return None
    
    def detect_group_conflict(self, date: str, heure_debut: str, heure_fin: str,
                            groupe_id: int, exclude_seance_id: Optional[int] = None) -> Optional[str]:
        """Detect if a group is already occupied (considering pause time)"""
        new_slot = TimeSlot(date, heure_debut, heure_fin)
        
        for seance in self.existing_seances:
            if exclude_seance_id is not None and seance.get('id') == exclude_seance_id:
                continue
            
            if seance.get('groupe_id') == groupe_id:
                existing_slot = TimeSlot(
                    seance.get('date', ''),
                    seance.get('heure_debut', ''),
                    seance.get('heure_fin', '')
                )
                
                # [MODIF] On passe min_pause ici
                if new_slot.overlaps_with(existing_slot, min_pause=self.PAUSE_MINUTES):
                    return (f"Groupe occupé: Le groupe {groupe_id} a un cours ou une pause "
                            f"autour de {existing_slot}")
        return None
    
    def detect_time_slot_conflict(self, date: str, heure_debut: str, heure_fin: str,
                                 exclude_seance_id: Optional[int] = None) -> List[Dict]:
        """Detect all sessions that conflict with a given time slot (considering pause)"""
        new_slot = TimeSlot(date, heure_debut, heure_fin)
        conflicts = []
        
        for seance in self.existing_seances:
            if exclude_seance_id is not None and seance.get('id') == exclude_seance_id:
                continue
            
            existing_slot = TimeSlot(
                seance.get('date', ''),
                seance.get('heure_debut', ''),
                seance.get('heure_fin', '')
            )
            
            # [MODIF] Même ici, on respecte la pause
            if new_slot.overlaps_with(existing_slot, min_pause=self.PAUSE_MINUTES):
                conflicts.append(seance)
        
        return conflicts

    # Les méthodes get_availability restent les mêmes (elles servent juste à l'affichage)
    def get_room_availability(self, salle_id: int, date: str) -> List[Tuple[str, str]]:
        room_sessions = [s for s in self.existing_seances if s.get('salle_id') == salle_id and s.get('date') == date]
        room_sessions.sort(key=lambda s: s.get('heure_debut', ''))
        return [(s.get('heure_debut', ''), s.get('heure_fin', '')) for s in room_sessions]
    
    def get_teacher_availability(self, enseignant_id: int, date: str) -> List[Tuple[str, str]]:
        teacher_sessions = [s for s in self.existing_seances if s.get('enseignant_id') == enseignant_id and s.get('date') == date]
        teacher_sessions.sort(key=lambda s: s.get('heure_debut', ''))
        return [(s.get('heure_debut', ''), s.get('heure_fin', '')) for s in teacher_sessions]
    
    def get_group_availability(self, groupe_id: int, date: str) -> List[Tuple[str, str]]:
        group_sessions = [s for s in self.existing_seances if s.get('groupe_id') == groupe_id and s.get('date') == date]
        group_sessions.sort(key=lambda s: s.get('heure_debut', ''))
        return [(s.get('heure_debut', ''), s.get('heure_fin', '')) for s in group_sessions]