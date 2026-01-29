# src/logic/unavailability_service.py
from typing import List, Dict, Optional, Tuple
from src.logic.time_utils import TimeUtils
from src.logic.conflict_detector import ConflictDetector

class UnavailabilityService:
    """
    Service pour gérer les indisponibilités des enseignants.
    Permet d'ajouter, récupérer et supprimer les créneaux d'absence.
    """
    
    def __init__(self, db):
        self.db = db

    def add_unavailability(self, enseignant_id: int, date: str, 
                          heure_debut: str, heure_fin: str, motif: str = "") -> Tuple[bool, str]:
        """
        Déclarer une indisponibilité pour un enseignant.
        Vérifie d'abord s'il n'a pas DÉJÀ cours pendant cette période avant de valider.
        """
        # 1. Validation de la plage horaire (Début < Fin)
        if not TimeUtils.is_valid_time_range(heure_debut, heure_fin):
            return False, "Erreur : L'heure de début doit être avant l'heure de fin."

        # 2. Vérifier si l'enseignant a déjà des cours ce jour-là
        # Récupération des séances existantes pour ce prof à cette date
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM seances 
            WHERE enseignant_id = ? AND date = ?
        """, (enseignant_id, date))
        existing_seances = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Utilisation du ConflictDetector pour vérifier les chevauchements
        detector = ConflictDetector(existing_seances)
        conflict = detector.detect_teacher_conflict(date, heure_debut, heure_fin, enseignant_id)
        
        if conflict:
            return False, f"Impossible : L'enseignant a déjà un cours prévu sur ce créneau : {conflict}"

        # 3. Insertion de l'indisponibilité dans la base de données
        try:
            self.db.ajouter_disponibilite(enseignant_id, date, heure_debut, heure_fin, motif)
            return True, "Indisponibilité ajoutée avec succès."
        except Exception as e:
            return False, f"Erreur Base de Données : {str(e)}"

    def get_teacher_unavailabilities(self, enseignant_id: int) -> List[Dict]:
        """Récupérer toutes les indisponibilités d'un enseignant spécifique."""
        return self.db.get_dispo_prof(enseignant_id)

    def delete_unavailability(self, dispo_id: int) -> bool:
        """Supprimer une indisponibilité par son ID."""
        return self.db.supprimer_disponibilite(dispo_id)