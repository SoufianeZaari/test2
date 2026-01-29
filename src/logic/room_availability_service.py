# src/logic/room_availability_service.py
from typing import List, Dict, Optional
from src.logic.conflict_detector import ConflictDetector
from src.logic.time_utils import TimeUtils

class RoomAvailabilityService:
    """
    Service de recherche des salles disponibles.
    """
    
    def __init__(self, db):
        self.db = db

    def find_available_rooms(self, date: str, heure_debut: str, heure_fin: str, 
                           min_capacite: int = 0, type_salle: Optional[str] = None) -> List[Dict]:
        """
        Trouve toutes les salles libres pour un créneau donné.
        Permet de filtrer par capacité minimale et type de salle.
        """
        # 1. Récupérer toutes les salles depuis la base
        all_rooms = self.db.get_toutes_salles()
        
        # Filtrer d'abord par capacité et type (Optimisation des performances)
        candidate_rooms = []
        for room in all_rooms:
            if room['capacite'] >= min_capacite:
                if type_salle is None or room['type_salle'] == type_salle:
                    candidate_rooms.append(room)
        
        if not candidate_rooms:
            return []

        # 2. Récupérer toutes les séances de ce jour (pour la détection de conflit)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM seances WHERE date = ?", (date,))
        todays_seances = [dict(row) for row in cursor.fetchall()]
        conn.close()

        detector = ConflictDetector(todays_seances)
        
        available_rooms = []
        
        # 3. Vérifier la disponibilité de chaque salle candidate
        for room in candidate_rooms:
            # detect_room_conflict retourne une chaîne si conflit, None si libre
            conflict = detector.detect_room_conflict(
                date, heure_debut, heure_fin, room['id']
            )
            
            if conflict is None:
                available_rooms.append(room)
                
        return available_rooms