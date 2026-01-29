# src/logic/schedule_generator.py
"""
Automatic schedule generation logic
Generates timetables while respecting all constraints
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from src.logic.conflict_detector import ConflictDetector
from src.logic.constraint_validator import ConstraintValidator
from src.logic.room_availability_service import RoomAvailabilityService
from src.logic.time_utils import TimeUtils


class ScheduleGenerator:
    """Generates automatic schedules respecting all constraints"""
    
    # Maximum hours per week for teachers in auto-generated timetable
    MAX_TEACHER_HOURS_PER_WEEK = 8
    
    # Default time slots for scheduling
    DEFAULT_TIME_SLOTS = [
        ("08:00", "09:30"),
        ("09:40", "11:10"),  # 10 min pause
        ("11:20", "12:50"),  # 10 min pause
        ("14:00", "15:30"),
        ("15:40", "17:10"),  # 10 min pause
        ("17:20", "18:50")   # 10 min pause
    ]
    
    def __init__(self, db, existing_seances: List[Dict] = None,
                 existing_reservations: List[Dict] = None):
        """
        Initialize the schedule generator
        Args:
            db: Database instance
            existing_seances: List of existing sessions
            existing_reservations: List of existing reservations
        """
        self.db = db
        self.constraint_validator = ConstraintValidator(db)
        
        # Combine seances and approved reservations
        all_sessions = (existing_seances or [])
        if existing_reservations:
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
                for r in existing_reservations
                if r.get('statut') == 'validee'
            ]
            all_sessions.extend(approved_reservations)
        
        self.conflict_detector = ConflictDetector(all_sessions)
        self.room_service = RoomAvailabilityService(db, existing_seances, existing_reservations)
    
    def generate_schedule_for_group(self, groupe_id: int, matiere: str,
                                   type_seance: str, duree_heures: float,
                                   enseignant_id: int, nb_seances_semaine: int,
                                   semaine_debut: str = None,
                                   teacher_weekly_hours: Dict[int, float] = None) -> List[Dict]:
        """
        Generates schedule for a group's course
        Args:
            groupe_id: Group ID
            matiere: Subject name
            type_seance: Type of session ("Cours", "TD", "TP", "Examen")
            duree_heures: Duration in hours
            enseignant_id: Teacher ID
            nb_seances_semaine: Number of sessions per week
            semaine_debut: Start week date "YYYY-MM-DD" (default: current week)
            teacher_weekly_hours: Dict tracking teacher hours per week {teacher_id: hours}
        Returns:
            List of generated session dictionaries (not yet saved to DB)
        """
        if not semaine_debut:
            # Start from next Monday
            today = datetime.now()
            days_ahead = (7 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            next_monday = today + timedelta(days=days_ahead)
            semaine_debut = next_monday.strftime("%Y-%m-%d")
        
        # Initialize teacher hours tracking if not provided
        if teacher_weekly_hours is None:
            teacher_weekly_hours = {}
        
        # Check teacher workload constraint (8h/week for auto-generated)
        current_teacher_hours = teacher_weekly_hours.get(enseignant_id, 0.0)
        total_hours_needed = duree_heures * nb_seances_semaine
        
        if current_teacher_hours + total_hours_needed > self.MAX_TEACHER_HOURS_PER_WEEK:
            # Teacher would exceed 8h/week limit
            return []  # Return empty list - teacher workload limit reached
        
        # Get group info for capacity check
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT effectif FROM groupes WHERE id = ?", (groupe_id,))
        groupe = cursor.fetchone()
        if not groupe:
            conn.close()
            return []
        # Handle both tuple and dict access
        effectif = groupe[0] if isinstance(groupe, tuple) else groupe.get('effectif', 0)
        conn.close()
        
        # Get available rooms with sufficient capacity
        available_rooms = self._get_suitable_rooms(effectif)
        
        if not available_rooms:
            return []  # No suitable rooms available
        
        # Calculate session duration
        duree_minutes = int(duree_heures * 60)
        
        # Generate sessions
        generated_sessions = []
        dates = self._get_week_dates(semaine_debut, nb_seances_semaine)
        
        for date in dates:
            # Check if adding this session would exceed teacher limit
            if current_teacher_hours + duree_heures > self.MAX_TEACHER_HOURS_PER_WEEK:
                break  # Stop generating if limit would be exceeded
            
            # Try to find a suitable time slot and room
            session = self._find_suitable_slot(
                date, groupe_id, enseignant_id, duree_minutes,
                matiere, type_seance, available_rooms
            )
            
            if session:
                generated_sessions.append(session)
                # Update teacher hours tracking
                current_teacher_hours += duree_heures
                teacher_weekly_hours[enseignant_id] = current_teacher_hours
        
        return generated_sessions
    
    def _get_suitable_rooms(self, min_capacity: int) -> List[Dict]:
        """Gets rooms with sufficient capacity"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM salles WHERE capacite >= ? ORDER BY capacite",
                (min_capacity,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            # Convert tuples to dicts
            rooms = []
            for row in rows:
                if isinstance(row, tuple):
                    rooms.append({
                        'id': row[0],
                        'nom': row[1],
                        'capacite': row[2],
                        'type_salle': row[3],
                        'equipements': row[4] or ""
                    })
                elif isinstance(row, dict):
                    rooms.append(row)
                else:
                    try:
                        rooms.append(dict(row))
                    except (TypeError, ValueError):
                        continue
            return rooms
        except Exception as e:
            print(f"Erreur lors de la récupération des salles: {e}")
            return []
    
    def _get_week_dates(self, semaine_debut: str, nb_seances: int) -> List[str]:
        """Gets dates for the week starting from semaine_debut"""
        try:
            start_date = datetime.strptime(semaine_debut, "%Y-%m-%d")
            dates = []
            
            # Generate dates (Monday to Friday, max 5 days)
            for i in range(min(nb_seances, 5)):
                date = start_date + timedelta(days=i)
                dates.append(date.strftime("%Y-%m-%d"))
            
            return dates
        except ValueError:
            return []
    
    def _find_suitable_slot(self, date: str, groupe_id: int, enseignant_id: int,
                            duree_minutes: int, matiere: str, type_seance: str,
                            available_rooms: List[Dict]) -> Optional[Dict]:
        """
        Finds a suitable time slot and room for a session
        """
        # Try each default time slot
        for heure_debut, heure_fin_base in self.DEFAULT_TIME_SLOTS:
            # Calculate actual end time based on duration
            start_min = TimeUtils.time_to_minutes(heure_debut)
            if start_min is None:
                continue
            
            end_min = start_min + duree_minutes
            hours = end_min // 60
            minutes = end_min % 60
            heure_fin = f"{hours:02d}:{minutes:02d}"
            
            # Check if this time slot is valid
            if not TimeUtils.is_valid_time_range(heure_debut, heure_fin):
                continue
            
            # Try each available room
            for room in available_rooms:
                salle_id = room['id']
                
                # Check for conflicts
                conflicts = self.conflict_detector.detect_all_conflicts(
                    date, heure_debut, heure_fin,
                    salle_id=salle_id,
                    enseignant_id=enseignant_id,
                    groupe_id=groupe_id
                )
                
                if not conflicts:
                    # Found a suitable slot!
                    return {
                        'titre': matiere,
                        'type_seance': type_seance,
                        'date': date,
                        'heure_debut': heure_debut,
                        'heure_fin': heure_fin,
                        'salle_id': salle_id,
                        'enseignant_id': enseignant_id,
                        'groupe_id': groupe_id
                    }
        
        return None
    
    def validate_generated_schedule(self, sessions: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validates a generated schedule
        Args:
            sessions: List of session dictionaries
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        for session in sessions:
            # Validate constraints
            is_valid, constraint_errors = self.constraint_validator.validate_all_constraints(
                session['date'],
                session['heure_debut'],
                session['heure_fin'],
                salle_id=session.get('salle_id'),
                groupe_id=session.get('groupe_id'),
                is_reservation=False  # Not a reservation, so no advance notice required
            )
            
            if not is_valid:
                errors.extend(constraint_errors)
            
            # Check conflicts
            conflict_errors = self.conflict_detector.detect_all_conflicts(
                session['date'],
                session['heure_debut'],
                session['heure_fin'],
                salle_id=session.get('salle_id'),
                enseignant_id=session.get('enseignant_id'),
                groupe_id=session.get('groupe_id')
            )
            
            errors.extend(conflict_errors)
        
        return len(errors) == 0, errors
    
    def get_teacher_weekly_hours(self, enseignant_id: int, semaine_debut: str,
                                 existing_seances: List[Dict] = None) -> float:
        """
        Calculates total hours for a teacher in a given week (auto-generated sessions only)
        Args:
            enseignant_id: Teacher ID
            semaine_debut: Start of week date "YYYY-MM-DD"
            existing_seances: List of existing sessions (optional, for calculation)
        Returns:
            Total hours for the teacher in that week
        """
        if not existing_seances:
            # Get from database
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                # Calculate week end date
                start_date = datetime.strptime(semaine_debut, "%Y-%m-%d")
                week_end = start_date + timedelta(days=6)
                semaine_fin = week_end.strftime("%Y-%m-%d")
                
                cursor.execute('''
                    SELECT * FROM seances
                    WHERE enseignant_id = ? 
                    AND date >= ? AND date <= ?
                ''', (enseignant_id, semaine_debut, semaine_fin))
                
                existing_seances = [dict(row) for row in cursor.fetchall()]
                conn.close()
            except Exception as e:
                print(f"Erreur lors du calcul des heures: {e}")
                return 0.0
        
        # Calculate total hours
        total_hours = 0.0
        for seance in existing_seances:
            if seance.get('enseignant_id') == enseignant_id:
                # Calculate duration in hours
                duree_minutes = TimeUtils.calculate_duration(
                    seance.get('heure_debut', ''),
                    seance.get('heure_fin', '')
                )
                total_hours += duree_minutes / 60.0
        
        return total_hours

