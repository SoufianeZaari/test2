# src/logic/service_facade.py
from typing import List, Dict, Optional, Tuple
from src.database import Database

# Import des services et validateurs
from src.logic.constraint_validator import ConstraintValidator
from src.logic.reservation_validator import ReservationValidator
from src.logic.room_availability_service import RoomAvailabilityService
from src.logic.unavailability_service import UnavailabilityService
from src.logic.schedule_generator import ScheduleGenerator

class ServiceFacade:
    """
    Point d'entrée unique pour la logique métier (Design Pattern Facade).
    L'interface graphique ne doit idéalement interagir qu'avec cette classe
    pour éviter le couplage fort.
    """
    
    def __init__(self, db: Database):
        self.db = db
        # Initialisation des sous-services
        self.unavailability_service = UnavailabilityService(db)
        self.room_service = RoomAvailabilityService(db)
        self.generator = ScheduleGenerator(db)
    
    # === GESTION DES SÉANCES (Ajout manuel) ===
    def create_seance(self, data: Dict) -> Tuple[bool, List[str]]:
        """Créer une nouvelle séance avec validation complète des contraintes."""
        # 1. Récupération des données nécessaires
        all_seances = self.db.get_toutes_seances()
        salles = self.db.get_toutes_salles()
        groupes = self.db.get_tous_groupes()
        
        # 2. Validation (Conflits, Capacité, Horaires...)
        validator = ConstraintValidator(all_seances, salles=salles, groupes=groupes)
        is_valid, errors = validator.validate_seance(
            date=data['date'],
            heure_debut=data['heure_debut'],
            heure_fin=data['heure_fin'],
            salle_id=data['salle_id'],
            enseignant_id=data['enseignant_id'],
            groupe_id=data['groupe_id']
        )
        
        if not is_valid:
            return False, errors
            
        # 3. Sauvegarde si validation OK
        try:
            self.db.ajouter_seance(**data)
            return True, ["Séance créée avec succès"]
        except Exception as e:
            return False, [str(e)]

    # === GESTION DES RÉSERVATIONS (Demandes Profs) ===
    def request_reservation(self, data: Dict) -> Tuple[bool, List[str]]:
        """Soumettre une demande de réservation de salle."""
        all_seances = self.db.get_toutes_seances()
        existing_res = self.db.get_toutes_reservations()
        
        validator = ReservationValidator(all_seances, existing_res)
        is_valid, errors = validator.validate_reservation_request(
            enseignant_id=data['enseignant_id'],
            salle_id=data['salle_id'],
            date=data['date'],
            heure_debut=data['heure_debut'],
            heure_fin=data['heure_fin']
        )
        
        if is_valid:
            self.db.ajouter_reservation(**data)
            return True, ["Demande envoyée à l'administration"]
        return False, errors

    # === GESTION DES ABSENCES & RECHERCHE SALLES ===
    def add_prof_unavailability(self, prof_id: int, date: str, start: str, end: str):
        """Délègue l'ajout d'indisponibilité au service dédié."""
        return self.unavailability_service.add_unavailability(prof_id, date, start, end)

    def find_free_rooms(self, date: str, start: str, end: str, capacity: int = 0):
        """Délègue la recherche de salles au service dédié."""
        return self.room_service.find_available_rooms(date, start, end, capacity)

    # === GÉNÉRATION AUTOMATIQUE ===
    def generate_timetable(self, courses: List[Dict], start_date: str):
        """Lance l'algorithme de génération et sauvegarde si succès."""
        result = self.generator.generate_schedule(courses, start_date)
        if result['success']:
            self.generator.save_generated_schedule()
        return result