# src/logic/room_availability_service.py
from typing import List, Dict, Optional
from src.logic.conflict_detector import ConflictDetector
from src.logic.time_utils import TimeUtils

class RoomAvailabilityService:
    """
    Service de recherche des salles disponibles.
    """
    
    def __init__(self, db, existing_seances: List[Dict] = None, existing_reservations: List[Dict] = None):
        """
        Initialize the room availability service
        
        Args:
            db: Database instance
            existing_seances: Optional list of existing sessions (for caching)
            existing_reservations: Optional list of existing reservations (for caching)
        """
        self.db = db
        self.existing_seances = existing_seances
        self.existing_reservations = existing_reservations

    def _convert_room_tuple_to_dict(self, room) -> Optional[Dict]:
        """
        Converts a room tuple or row to a dictionary.
        
        Args:
            room: Tuple, dict, or sqlite Row object
            
        Returns:
            Dictionary with room data or None if conversion fails
        """
        if isinstance(room, tuple):
            return {
                'id': room[0],
                'nom': room[1],
                'capacite': room[2],
                'type_salle': room[3],
                'equipements': room[4] or ""
            }
        elif isinstance(room, dict):
            return room
        else:
            try:
                return {
                    'id': room['id'],
                    'nom': room['nom'],
                    'capacite': room['capacite'],
                    'type_salle': room['type_salle'],
                    'equipements': room['equipements'] or ""
                }
            except (TypeError, KeyError):
                return None

    def _convert_seance_tuple_to_dict(self, seance) -> Optional[Dict]:
        """
        Converts a seance tuple or row to a dictionary.
        
        Args:
            seance: Tuple, dict, or sqlite Row object
            
        Returns:
            Dictionary with seance data or None if conversion fails
        """
        if isinstance(seance, tuple):
            return {
                'id': seance[0], 'titre': seance[1], 'type_seance': seance[2],
                'date': seance[3], 'heure_debut': seance[4], 'heure_fin': seance[5],
                'salle_id': seance[6], 'enseignant_id': seance[7], 'groupe_id': seance[8]
            }
        elif isinstance(seance, dict):
            return seance
        else:
            try:
                return dict(seance)
            except (TypeError, ValueError):
                return None

    def find_available_rooms(self, date: str, heure_debut: str, heure_fin: str, 
                           min_capacite: int = 0, type_salle: Optional[str] = None) -> List[Dict]:
        """
        Trouve toutes les salles libres pour un créneau donné.
        Permet de filtrer par capacité minimale et type de salle.
        
        Args:
            date: Date au format YYYY-MM-DD
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
            min_capacite: Capacité minimale requise
            type_salle: Type de salle ("Salle", "Amphithéâtre", "Laboratoire")
        
        Returns:
            List of available room dictionaries
        """
        # 1. Récupérer toutes les salles depuis la base
        all_rooms_tuples = self.db.get_toutes_salles()
        
        # Convertir les tuples en dictionnaires
        all_rooms = []
        for room in all_rooms_tuples:
            room_dict = self._convert_room_tuple_to_dict(room)
            if room_dict:
                all_rooms.append(room_dict)
        
        # Filtrer d'abord par capacité et type (Optimisation des performances)
        candidate_rooms = []
        for room in all_rooms:
            if room['capacite'] >= min_capacite:
                if type_salle is None or room['type_salle'] == type_salle:
                    candidate_rooms.append(room)
        
        if not candidate_rooms:
            return []

        # 2. Récupérer toutes les séances de ce jour (pour la détection de conflit)
        if self.existing_seances is not None:
            # Filtrer les séances existantes par date
            todays_seances = [s for s in self.existing_seances if s.get('date') == date]
        else:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM seances WHERE date = ?", (date,))
            seances_tuples = cursor.fetchall()
            conn.close()
            
            # Convertir en dictionnaires
            todays_seances = []
            for s in seances_tuples:
                seance_dict = self._convert_seance_tuple_to_dict(s)
                if seance_dict:
                    todays_seances.append(seance_dict)

        # Ajouter les réservations validées
        if self.existing_reservations:
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
                for r in self.existing_reservations
                if r.get('statut') == 'validee' and r.get('date') == date
            ]
            todays_seances.extend(approved_reservations)

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