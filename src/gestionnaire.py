# src/gestionnaire.py
"""
Gestionnaire Principal - Logique Métier
Gère les algorithmes d'affectation, détection de conflits,
rattrapages avec verrouillage de salle, et absences avec libération automatique.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from src.services_notification import NotificationService
from src.logic.conflict_detector import ConflictDetector
from src.logic.room_availability_service import RoomAvailabilityService


class GestionnaireRattrapage:
    """
    Gère les séances de rattrapage avec :
    - Vérification de disponibilité de salle
    - Verrouillage automatique de la salle (statut OCCUPÉE)
    - Notification automatique aux étudiants concernés
    """
    
    def __init__(self, db):
        """
        Initialise le gestionnaire de rattrapage
        
        Args:
            db: Instance de Database
        """
        self.db = db
        self.notification_service = NotificationService(db)
    
    def reserver_rattrapage(self, enseignant_id: int, groupe_id: int, 
                           salle_id: int, date: str, heure_debut: str, 
                           heure_fin: str, matiere: str,
                           seance_originale_id: int = None) -> Dict:
        """
        Réserve une salle pour un rattrapage avec verrouillage automatique
        et notification aux étudiants.
        
        PROCESSUS:
        1. Vérifier si la salle est libre (pas de séance, pas de réservation validée, pas de rattrapage)
        2. Si libre -> Créer le rattrapage (verrouille la salle)
        3. Notifier tous les étudiants du groupe
        
        Args:
            enseignant_id: ID de l'enseignant
            groupe_id: ID du groupe concerné
            salle_id: ID de la salle à réserver
            date: Date du rattrapage (YYYY-MM-DD)
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
            matiere: Nom de la matière
            seance_originale_id: ID de la séance originale (optionnel)
        
        Returns:
            Dict avec 'success', 'rattrapage_id', 'message', 'notifications_envoyees'
        """
        result = {
            'success': False,
            'rattrapage_id': None,
            'message': '',
            'notifications_envoyees': 0
        }
        
        # 1. VÉRIFICATION DE LA DISPONIBILITÉ DE LA SALLE
        salle_disponible, raison = self._verifier_disponibilite_salle(
            salle_id, date, heure_debut, heure_fin
        )
        
        if not salle_disponible:
            result['message'] = f"❌ Salle non disponible: {raison}"
            return result
        
        # 2. VÉRIFICATION DU CONFLIT ENSEIGNANT
        conflit_enseignant = self._verifier_conflit_enseignant(
            enseignant_id, date, heure_debut, heure_fin
        )
        
        if conflit_enseignant:
            result['message'] = f"❌ Conflit enseignant: {conflit_enseignant}"
            return result
        
        # 3. CRÉER LE RATTRAPAGE (VERROUILLE LA SALLE)
        rattrapage_id = self.db.ajouter_rattrapage(
            enseignant_id=enseignant_id,
            groupe_id=groupe_id,
            salle_id=salle_id,
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            motif=matiere,
            seance_originale_id=seance_originale_id
        )
        
        if not rattrapage_id:
            result['message'] = "❌ Erreur lors de la création du rattrapage"
            return result
        
        # 4. NOTIFIER LES ÉTUDIANTS
        enseignant = self.db.get_utilisateur_by_id(enseignant_id)
        salle = self.db.get_salle_by_id(salle_id)
        
        enseignant_nom = f"{enseignant[2]} {enseignant[1]}" if enseignant else "Enseignant"
        salle_nom = salle[1] if salle else "Salle"
        
        nb_notifs, msg = self.notification_service.notifier_rattrapage(
            groupe_id=groupe_id,
            enseignant_nom=enseignant_nom,
            matiere=matiere,
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            salle_nom=salle_nom
        )
        
        result['success'] = True
        result['rattrapage_id'] = rattrapage_id
        result['message'] = f"✅ Rattrapage créé! Salle {salle_nom} réservée et verrouillée."
        result['notifications_envoyees'] = nb_notifs
        
        print(f"🔒 Salle {salle_nom} VERROUILLÉE pour le {date} de {heure_debut} à {heure_fin}")
        print(f"📧 {nb_notifs} étudiants notifiés")
        
        return result
    
    def _verifier_disponibilite_salle(self, salle_id: int, date: str, 
                                      heure_debut: str, heure_fin: str) -> Tuple[bool, str]:
        """
        Vérifie complètement si une salle est disponible :
        - Pas de séance existante
        - Pas de réservation validée
        - Pas de rattrapage confirmé
        
        Returns:
            Tuple (disponible, raison si non disponible)
        """
        # Vérifier les séances existantes
        seances = self.db.get_seances_by_salle(salle_id, date)
        for seance in seances:
            hd = seance[4]  # heure_debut
            hf = seance[5]  # heure_fin
            if self._creneaux_chevauchent(heure_debut, heure_fin, hd, hf):
                return False, f"Séance existante de {hd} à {hf}"
        
        # Vérifier les rattrapages existants
        if self.db.verifier_salle_occupee_rattrapage(salle_id, date, heure_debut, heure_fin):
            return False, "Rattrapage déjà programmé sur ce créneau"
        
        # Vérifier les réservations validées
        reservations = self.db.get_reservations_by_statut('validee')
        for res in reservations:
            if res[2] == salle_id and res[3] == date:
                hd = res[4]
                hf = res[5]
                if self._creneaux_chevauchent(heure_debut, heure_fin, hd, hf):
                    return False, f"Réservation validée de {hd} à {hf}"
        
        return True, ""
    
    def _verifier_conflit_enseignant(self, enseignant_id: int, date: str,
                                     heure_debut: str, heure_fin: str) -> Optional[str]:
        """Vérifie si l'enseignant a un conflit d'horaire"""
        seances = self.db.get_seances_by_enseignant(enseignant_id)
        
        for seance in seances:
            if seance[3] == date:  # même date
                hd = seance[4]
                hf = seance[5]
                if self._creneaux_chevauchent(heure_debut, heure_fin, hd, hf):
                    return f"Cours prévu de {hd} à {hf}"
        
        return None
    
    def _creneaux_chevauchent(self, h1_debut: str, h1_fin: str, 
                              h2_debut: str, h2_fin: str) -> bool:
        """Vérifie si deux créneaux se chevauchent"""
        # Convertir en minutes pour comparaison
        def to_minutes(heure: str) -> int:
            parts = heure.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        
        d1, f1 = to_minutes(h1_debut), to_minutes(h1_fin)
        d2, f2 = to_minutes(h2_debut), to_minutes(h2_fin)
        
        return not (f1 <= d2 or f2 <= d1)
    
    def annuler_rattrapage(self, rattrapage_id: int) -> Dict:
        """
        Annule un rattrapage et libère la salle
        
        Args:
            rattrapage_id: ID du rattrapage à annuler
        
        Returns:
            Dict avec 'success', 'message'
        """
        success = self.db.annuler_rattrapage(rattrapage_id)
        
        if success:
            print(f"🔓 Rattrapage {rattrapage_id} annulé - Salle libérée")
            return {'success': True, 'message': "Rattrapage annulé, salle libérée"}
        else:
            return {'success': False, 'message': "Erreur lors de l'annulation"}


class GestionnaireAbsence:
    """
    Gère les absences d'enseignants avec :
    - Libération automatique des salles occupées
    - Notification aux étudiants (cours annulé)
    - Notification aux administrateurs
    """
    
    def __init__(self, db):
        """
        Initialise le gestionnaire d'absence
        
        Args:
            db: Instance de Database
        """
        self.db = db
        self.notification_service = NotificationService(db)
    
    def declarer_absence(self, enseignant_id: int, date_debut: str, 
                        date_fin: str, motif: str = None) -> Dict:
        """
        Déclare une absence d'enseignant avec libération automatique des salles.
        
        PROCESSUS CRITIQUE:
        1. Identifier toutes les séances de l'enseignant sur la période
        2. Notifier les étudiants de chaque groupe concerné
        3. Notifier les administrateurs
        4. LIBÉRER toutes les salles (supprimer les séances = rendre les salles réservables)
        
        Args:
            enseignant_id: ID de l'enseignant
            date_debut: Date de début d'absence (YYYY-MM-DD)
            date_fin: Date de fin d'absence (YYYY-MM-DD)
            motif: Motif de l'absence (optionnel)
        
        Returns:
            Dict avec statistiques détaillées
        """
        result = {
            'success': False,
            'message': '',
            'seances_supprimees': 0,
            'salles_liberees': [],
            'groupes_notifies': 0,
            'etudiants_notifies': 0,
            'admins_notifies': 0
        }
        
        # Récupérer l'enseignant
        enseignant = self.db.get_utilisateur_by_id(enseignant_id)
        if not enseignant:
            result['message'] = "❌ Enseignant non trouvé"
            return result
        
        enseignant_nom = f"{enseignant[2]} {enseignant[1]}"
        
        print(f"\n{'='*60}")
        print(f"🚨 DÉCLARATION D'ABSENCE - {enseignant_nom}")
        print(f"📅 Période: {date_debut} → {date_fin}")
        print(f"{'='*60}")
        
        # 1. RÉCUPÉRER LES SÉANCES À SUPPRIMER
        seances_a_supprimer = self.db.get_seances_enseignant_periode(
            enseignant_id, date_debut, date_fin
        )
        
        if not seances_a_supprimer:
            # Ajouter quand même l'indisponibilité
            self.db.ajouter_disponibilite(enseignant_id, date_debut, date_fin, motif)
            result['success'] = True
            result['message'] = "✅ Absence enregistrée (aucune séance à annuler)"
            return result
        
        print(f"\n📋 {len(seances_a_supprimer)} séance(s) à annuler:")
        
        # Collecter les infos avant suppression
        salles_ids = set()
        groupes_ids = set()
        seances_details = []
        
        for seance in seances_a_supprimer:
            seance_id = seance[0]
            titre = seance[1]
            date = seance[3]
            heure_debut = seance[4]
            salle_id = seance[6]
            groupe_id = seance[8]
            
            salles_ids.add(salle_id)
            if groupe_id:
                groupes_ids.add(groupe_id)
            
            seances_details.append({
                'id': seance_id,
                'titre': titre,
                'date': date,
                'heure_debut': heure_debut,
                'salle_id': salle_id,
                'groupe_id': groupe_id
            })
            
            salle = self.db.get_salle_by_id(salle_id)
            salle_nom = salle[1] if salle else f"Salle {salle_id}"
            print(f"   - {titre} | {date} {heure_debut} | {salle_nom}")
        
        # 2. NOTIFIER LES ÉTUDIANTS ET ADMINS
        print(f"\n📧 Envoi des notifications...")
        
        notif_result = self.notification_service.notifier_absence_enseignant(
            enseignant_id=enseignant_id,
            enseignant_nom=enseignant_nom,
            date_debut=date_debut,
            date_fin=date_fin,
            seances_annulees=seances_a_supprimer
        )
        
        result['etudiants_notifies'] = notif_result['etudiants_notifies']
        result['admins_notifies'] = notif_result['admins_notifies']
        result['groupes_notifies'] = notif_result['groupes_concernes']
        
        print(f"   ✅ {result['etudiants_notifies']} étudiants notifiés")
        print(f"   ✅ {result['admins_notifies']} administrateurs notifiés")
        
        # 3. LIBÉRER LES SALLES (SUPPRIMER LES SÉANCES)
        print(f"\n🔓 LIBÉRATION DES SALLES...")
        
        seances_supprimees, nb_supprime = self.db.liberer_seances_enseignant(
            enseignant_id, date_debut, date_fin
        )
        
        result['seances_supprimees'] = nb_supprime
        
        # Afficher les salles libérées
        for salle_id in salles_ids:
            salle = self.db.get_salle_by_id(salle_id)
            salle_nom = salle[1] if salle else f"Salle {salle_id}"
            result['salles_liberees'].append(salle_nom)
            print(f"   🔓 {salle_nom} - LIBÉRÉE et disponible pour réservation")
        
        # 4. ENREGISTRER L'INDISPONIBILITÉ
        self.db.ajouter_disponibilite(enseignant_id, date_debut, date_fin, motif)
        
        result['success'] = True
        result['message'] = (
            f"✅ Absence déclarée avec succès!\n"
            f"   • {nb_supprime} séances annulées\n"
            f"   • {len(result['salles_liberees'])} salles libérées\n"
            f"   • {result['etudiants_notifies']} étudiants notifiés"
        )
        
        print(f"\n{'='*60}")
        print(f"✅ ABSENCE TRAITÉE AVEC SUCCÈS")
        print(f"   • Séances supprimées: {nb_supprime}")
        print(f"   • Salles libérées: {', '.join(result['salles_liberees'])}")
        print(f"{'='*60}\n")
        
        return result


class GestionnaireEmploiDuTempsComplet:
    """
    Gestionnaire principal qui intègre toutes les fonctionnalités:
    - Génération d'emploi du temps
    - Gestion des rattrapages
    - Gestion des absences
    - Détection de conflits
    - Affectation optimale des salles
    """
    
    def __init__(self, db):
        """
        Initialise le gestionnaire complet
        
        Args:
            db: Instance de Database
        """
        self.db = db
        self.rattrapage_manager = GestionnaireRattrapage(db)
        self.absence_manager = GestionnaireAbsence(db)
        self.notification_service = NotificationService(db)
    
    # ═══════════════════════════════════════════════════════════
    # DÉLÉGATION VERS LES GESTIONNAIRES SPÉCIALISÉS
    # ═══════════════════════════════════════════════════════════
    
    def reserver_rattrapage(self, **kwargs) -> Dict:
        """Réserve un rattrapage (délègue à GestionnaireRattrapage)"""
        return self.rattrapage_manager.reserver_rattrapage(**kwargs)
    
    def declarer_absence(self, **kwargs) -> Dict:
        """Déclare une absence (délègue à GestionnaireAbsence)"""
        return self.absence_manager.declarer_absence(**kwargs)
    
    # ═══════════════════════════════════════════════════════════
    # RECHERCHE DE SALLES LIBRES
    # ═══════════════════════════════════════════════════════════
    
    def trouver_salles_libres(self, date: str, heure_debut: str, 
                              heure_fin: str, capacite_min: int = 0) -> List[Dict]:
        """
        Trouve toutes les salles disponibles sur un créneau
        (exclut les séances, réservations validées ET rattrapages)
        
        Args:
            date: Date (YYYY-MM-DD)
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
            capacite_min: Capacité minimum requise
        
        Returns:
            Liste de salles disponibles
        """
        toutes_salles = self.db.get_toutes_salles()
        salles_libres = []
        
        for salle in toutes_salles:
            salle_id = salle[0]
            nom = salle[1]
            capacite = salle[2]
            type_salle = salle[3]
            equipements = salle[4]
            
            # Vérifier capacité
            if capacite < capacite_min:
                continue
            
            # Vérifier disponibilité complète
            disponible, _ = self.rattrapage_manager._verifier_disponibilite_salle(
                salle_id, date, heure_debut, heure_fin
            )
            
            if disponible:
                salles_libres.append({
                    'id': salle_id,
                    'nom': nom,
                    'capacite': capacite,
                    'type_salle': type_salle,
                    'equipements': equipements
                })
        
        return salles_libres
    
    # ═══════════════════════════════════════════════════════════
    # DÉTECTION DE CONFLITS
    # ═══════════════════════════════════════════════════════════
    
    def detecter_tous_conflits(self, date: str, heure_debut: str, heure_fin: str,
                               salle_id: int = None, enseignant_id: int = None,
                               groupe_id: int = None) -> List[str]:
        """
        Détecte tous les conflits pour un créneau donné
        
        Args:
            date: Date (YYYY-MM-DD)
            heure_debut: Heure de début
            heure_fin: Heure de fin
            salle_id: ID de la salle (optionnel)
            enseignant_id: ID de l'enseignant (optionnel)
            groupe_id: ID du groupe (optionnel)
        
        Returns:
            Liste des messages de conflit
        """
        # Récupérer toutes les séances
        seances = self.db.get_toutes_seances()
        seances_dict = [
            {
                'id': s[0], 'titre': s[1], 'type_seance': s[2],
                'date': s[3], 'heure_debut': s[4], 'heure_fin': s[5],
                'salle_id': s[6], 'enseignant_id': s[7], 'groupe_id': s[8]
            } for s in seances
        ] if seances else []
        
        detector = ConflictDetector(seances_dict)
        return detector.detect_all_conflicts(
            date, heure_debut, heure_fin,
            salle_id=salle_id,
            enseignant_id=enseignant_id,
            groupe_id=groupe_id
        )
    
    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════
    
    def get_statistiques(self) -> Dict:
        """Retourne les statistiques du système"""
        return {
            'nb_seances': len(self.db.get_toutes_seances() or []),
            'nb_salles': len(self.db.get_toutes_salles() or []),
            'nb_groupes': len(self.db.get_tous_groupes() or []),
            'nb_enseignants': len(self.db.get_tous_utilisateurs('enseignant') or []),
            'nb_etudiants': len(self.db.get_tous_utilisateurs('etudiant') or []),
            'nb_reservations_en_attente': len(self.db.get_reservations_by_statut('en_attente') or [])
        }
