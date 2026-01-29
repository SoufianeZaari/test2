# logic/time_utils.py
from datetime import datetime, time
from typing import Optional

class TimeSlot:
    def __init__(self, date: str, heure_debut: str, heure_fin: str):
        self.date = date
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
    
    def __str__(self):
        return f"{self.date} {self.heure_debut}-{self.heure_fin}"
    
    # [MODIFICATION] Zdna parametre min_pause (par défaut 0)
    def overlaps_with(self, other: 'TimeSlot', min_pause: int = 0) -> bool:
        """
        Check if time slots overlap considering a minimum pause.
        min_pause: Minutes de pause requises entre les séances (ex: 10)
        """
        if self.date != other.date:
            return False
        
        return TimeUtils.times_overlap(
            self.heure_debut, self.heure_fin,
            other.heure_debut, other.heure_fin,
            min_pause # <-- Hna kan-passiw l-pause
        )
    
    # ... (B9i l-code khellih kif ma howa: contains, get_duration_minutes...)
    def get_duration_minutes(self) -> int:
        return TimeUtils.calculate_duration(self.heure_debut, self.heure_fin)

class TimeUtils:
    # ... (parse_time w time_to_minutes khellihom kif ma huma)
    @staticmethod
    def parse_time(time_str: str) -> Optional[time]:
        try:
            parts = time_str.split(':')
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
                return time(hour, minute)
        except (ValueError, AttributeError):
            pass
        return None
    
    @staticmethod
    def time_to_minutes(time_str: str) -> Optional[int]:
        t = TimeUtils.parse_time(time_str)
        if t:
            return t.hour * 60 + t.minute
        return None

    # [MODIFICATION IMPORTANTE ICI] 👇
    @staticmethod
    def times_overlap(start1: str, end1: str, start2: str, end2: str, min_pause: int = 0) -> bool:
        """
        Vérifie si les plages se chevauchent en prenant compte de la pause.
        Logic: Si Fin_A + Pause > Debut_B  ET  Fin_B + Pause > Debut_A ==> CONFLIT
        """
        start1_min = TimeUtils.time_to_minutes(start1)
        end1_min = TimeUtils.time_to_minutes(end1)
        start2_min = TimeUtils.time_to_minutes(start2)
        end2_min = TimeUtils.time_to_minutes(end2)
        
        if None in [start1_min, end1_min, start2_min, end2_min]:
            return False
        
        # On ajoute la pause à la fin de chaque créneau pour "élargir" la zone occupée
        return start1_min < (end2_min + min_pause) and start2_min < (end1_min + min_pause)

    # ... (kmml l-b9ya d l-code: time_contains, is_valid_time_range... kif ma kanou)
    @staticmethod
    def time_contains(container_start: str, container_end: str, contained_start: str, contained_end: str) -> bool:
        container_start_min = TimeUtils.time_to_minutes(container_start)
        container_end_min = TimeUtils.time_to_minutes(container_end)
        contained_start_min = TimeUtils.time_to_minutes(contained_start)
        contained_end_min = TimeUtils.time_to_minutes(contained_end)
        if None in [container_start_min, container_end_min, contained_start_min, contained_end_min]:
            return False
        return (container_start_min <= contained_start_min and container_end_min >= contained_end_min)

    @staticmethod
    def is_valid_time_range(start: str, end: str) -> bool:
        start_min = TimeUtils.time_to_minutes(start)
        end_min = TimeUtils.time_to_minutes(end)
        if None in [start_min, end_min]:
            return False
        return start_min < end_min

    @staticmethod
    def format_time(time_str: str) -> str:
        t = TimeUtils.parse_time(time_str)
        if t:
            return f"{t.hour:02d}:{t.minute:02d}"
        return time_str

    @staticmethod
    def calculate_duration(start: str, end: str) -> int:
        start_min = TimeUtils.time_to_minutes(start)
        end_min = TimeUtils.time_to_minutes(end)
        if start_min is not None and end_min is not None:
            return max(0, end_min - start_min)
        return 0