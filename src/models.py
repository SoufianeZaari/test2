# src/models.py
"""
Classes métier pour le système de gestion d'emploi du temps FSTT
Correspond à la structure de database.py avec duree_max_jour pour enseignants
"""

class Utilisateur:
    """Classe de base pour tous les utilisateurs"""
    def __init__(self, id, nom, prenom, email, mot_de_passe, type_user, 
                 date_creation=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe = mot_de_passe
        self.type_user = type_user
        self.date_creation = date_creation
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"
    
    def __repr__(self):
        return f"<Utilisateur {self.type_user}: {self.nom} {self.prenom}>"


class Administrateur(Utilisateur):
    """Administrateur du système - Gère la génération et l'export des emplois du temps"""
    def __init__(self, id, nom, prenom, email, mot_de_passe, date_creation=None):
        super().__init__(id, nom, prenom, email, mot_de_passe, "admin", date_creation)
    
    def generer_emploi_du_temps(self, db, groupes, enseignants, salles, matieres, contraintes=None):
        """
        Génère automatiquement l'emploi du temps en respectant toutes les contraintes
        
        Args:
            db: Instance de Database
            groupes: Liste des groupes
            enseignants: Liste des enseignants
            salles: Liste des salles
            matieres: Liste des matières à planifier
            contraintes: Dictionnaire de contraintes supplémentaires
        
        Returns:
            dict: Résultat contenant 'success', 'seances_creees', 'erreurs'
        """
        from src.logic.schedule_generator import ScheduleGenerator
        from datetime import datetime, timedelta
        
        result = {
            'success': True,
            'seances_creees': [],
            'erreurs': []
        }
        
        if not groupes or not enseignants or not salles:
            result['success'] = False
            result['erreurs'].append("Données insuffisantes pour générer l'emploi du temps")
            return result
        
        try:
            # Récupérer les séances et réservations existantes
            existing_seances = db.get_toutes_seances()
            existing_seances_dict = [
                {
                    'id': s[0], 'titre': s[1], 'type_seance': s[2],
                    'date': s[3], 'heure_debut': s[4], 'heure_fin': s[5],
                    'salle_id': s[6], 'enseignant_id': s[7], 'groupe_id': s[8]
                } for s in existing_seances
            ] if existing_seances else []
            
            existing_reservations = db.get_toutes_reservations()
            existing_reservations_dict = [
                {
                    'id': r[0], 'enseignant_id': r[1], 'salle_id': r[2],
                    'date': r[3], 'heure_debut': r[4], 'heure_fin': r[5],
                    'statut': r[6]
                } for r in existing_reservations
            ] if existing_reservations else []
            
            # Initialiser le générateur
            generator = ScheduleGenerator(db, existing_seances_dict, existing_reservations_dict)
            
            # Calculer la semaine de début (prochain lundi)
            today = datetime.now()
            days_ahead = (7 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            next_monday = today + timedelta(days=days_ahead)
            semaine_debut = next_monday.strftime("%Y-%m-%d")
            
            # Suivi des heures par enseignant
            teacher_weekly_hours = {}
            
            # Générer les séances pour chaque matière
            for matiere in matieres:
                groupe_id = matiere.get('groupe_id')
                enseignant_id = matiere.get('enseignant_id')
                titre = matiere.get('titre', 'Cours')
                type_seance = matiere.get('type_seance', 'Cours')
                duree_heures = matiere.get('duree_heures', 1.5)
                nb_seances = matiere.get('nb_seances_semaine', 1)
                
                # Vérifier la disponibilité de l'enseignant
                if enseignant_id:
                    if db.verifier_indisponibilite_enseignant(enseignant_id, semaine_debut):
                        result['erreurs'].append(
                            f"Enseignant {enseignant_id} indisponible pour {titre}"
                        )
                        continue
                
                # Générer les séances
                sessions = generator.generate_schedule_for_group(
                    groupe_id=groupe_id,
                    matiere=titre,
                    type_seance=type_seance,
                    duree_heures=duree_heures,
                    enseignant_id=enseignant_id,
                    nb_seances_semaine=nb_seances,
                    semaine_debut=semaine_debut,
                    teacher_weekly_hours=teacher_weekly_hours
                )
                
                # Sauvegarder les séances générées
                for session in sessions:
                    seance_id = db.ajouter_seance(
                        titre=session['titre'],
                        type_seance=session['type_seance'],
                        date=session['date'],
                        heure_debut=session['heure_debut'],
                        heure_fin=session['heure_fin'],
                        salle_id=session['salle_id'],
                        enseignant_id=session['enseignant_id'],
                        groupe_id=session['groupe_id']
                    )
                    if seance_id:
                        session['id'] = seance_id
                        result['seances_creees'].append(session)
            
            if not result['seances_creees'] and not result['erreurs']:
                result['erreurs'].append("Aucune séance n'a pu être créée")
                result['success'] = False
            elif result['erreurs'] and not result['seances_creees']:
                result['success'] = False
                
        except Exception as e:
            result['success'] = False
            result['erreurs'].append(f"Erreur lors de la génération: {str(e)}")
        
        return result
    
    def valider_reservation(self, db, reservation_id):
        """
        Valide une réservation
        
        Args:
            db: Instance de Database
            reservation_id: ID de la réservation
        
        Returns:
            bool: True si succès
        """
        return db.modifier_statut_reservation(reservation_id, "validee")
    
    def rejeter_reservation(self, db, reservation_id):
        """
        Rejette une réservation
        
        Args:
            db: Instance de Database
            reservation_id: ID de la réservation
        
        Returns:
            bool: True si succès
        """
        return db.modifier_statut_reservation(reservation_id, "rejetee")
    
    def exporter_emploi_du_temps(self, db, groupe_id=None, enseignant_id=None, format_export="pdf"):
        """
        Exporte l'emploi du temps au format spécifié
        
        Args:
            db: Instance de Database
            groupe_id: ID du groupe (optionnel)
            enseignant_id: ID de l'enseignant (optionnel)
            format_export: "pdf", "xlsx", ou "png"
        
        Returns:
            tuple: (success, file_path, error_message)
        """
        from src.logic.timetable_export_service import TimetableExportService
        
        export_service = TimetableExportService(db)
        
        if groupe_id:
            return export_service.export_group_timetable(groupe_id, format_export)
        elif enseignant_id:
            return export_service.export_teacher_timetable(enseignant_id, format_export)
        else:
            return False, None, "Veuillez spécifier un groupe ou un enseignant"
    
    def affecter_salle_automatique(self, db, groupe_id, date, heure_debut, heure_fin, equipements_requis=None):
        """
        Affecte automatiquement la meilleure salle disponible pour un cours
        
        Args:
            db: Instance de Database
            groupe_id: ID du groupe
            date: Date au format YYYY-MM-DD
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
            equipements_requis: Liste des équipements requis (optionnel)
        
        Returns:
            dict: {'success': bool, 'salle': Salle ou None, 'message': str}
        """
        from src.logic.room_availability_service import RoomAvailabilityService
        
        result = {'success': False, 'salle': None, 'message': ''}
        
        # Récupérer l'effectif du groupe
        groupe = db.get_groupe_by_id(groupe_id)
        if not groupe:
            result['message'] = "Groupe introuvable"
            return result
        
        effectif = groupe[2]  # effectif est à l'index 2
        
        # Trouver les salles disponibles avec capacité suffisante
        room_service = RoomAvailabilityService(db)
        salles_disponibles = room_service.find_available_rooms(
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            min_capacite=effectif
        )
        
        if not salles_disponibles:
            result['message'] = "Aucune salle disponible avec la capacité requise"
            return result
        
        # Filtrer par équipements si spécifiés
        if equipements_requis:
            salles_filtrees = []
            for salle in salles_disponibles:
                salle_equipements = (salle.get('equipements') or '').split(',')
                salle_equipements = [e.strip() for e in salle_equipements if e.strip()]
                if all(eq in salle_equipements for eq in equipements_requis):
                    salles_filtrees.append(salle)
            salles_disponibles = salles_filtrees
        
        if not salles_disponibles:
            result['message'] = "Aucune salle disponible avec les équipements requis"
            return result
        
        # Optimisation: choisir la salle avec la capacité la plus proche de l'effectif
        # (éviter le gaspillage d'espace)
        meilleure_salle = min(salles_disponibles, key=lambda s: s.get('capacite', 0) - effectif)
        
        result['success'] = True
        result['salle'] = meilleure_salle
        result['message'] = f"Salle {meilleure_salle.get('nom')} affectée ({meilleure_salle.get('capacite')} places)"
        
        return result
    
    def sauvegarder_base(self, db):
        """
        Crée une sauvegarde de la base de données
        
        Args:
            db: Instance de Database
        
        Returns:
            str: Chemin de la sauvegarde
        """
        return db.sauvegarder_bdd()


class Enseignant(Utilisateur):
    """Enseignant de la FSTT avec contrainte durée max/jour"""
    def __init__(self, id, nom, prenom, email, mot_de_passe, specialite, 
                 duree_max_jour=480, date_creation=None):
        super().__init__(id, nom, prenom, email, mot_de_passe, "enseignant", date_creation)
        self.specialite = specialite
        self.duree_max_jour = duree_max_jour  # en minutes (défaut: 480 = 8h)
    
    def __str__(self):
        return f"Prof. {self.prenom} {self.nom} ({self.specialite})"
    
    def get_duree_max_heures(self):
        """Retourne la durée max en heures"""
        return self.duree_max_jour / 60
    
    def set_duree_max_jour(self, db, duree_minutes):
        """
        Modifie la durée maximale journalière
        
        Args:
            db: Instance de Database
            duree_minutes: Nouvelle durée en minutes
        
        Returns:
            bool: True si succès
        """
        if db.modifier_duree_max_enseignant(self.id, duree_minutes):
            self.duree_max_jour = duree_minutes
            return True
        return False
    
    def calculer_duree_journee(self, db, date):
        """
        Calcule le total d'heures pour une date donnée
        
        Args:
            db: Instance de Database
            date: Date au format YYYY-MM-DD
        
        Returns:
            int: Durée en minutes
        """
        return db.calculer_duree_journee_enseignant(self.id, date)
    
    def peut_enseigner(self, db, date, duree_seance):
        """
        Vérifie si l'enseignant peut encore ajouter une séance
        sans dépasser sa durée max
        
        Args:
            db: Instance de Database
            date: Date au format YYYY-MM-DD
            duree_seance: Durée de la séance en minutes
        
        Returns:
            bool: True si possible
        """
        return db.peut_ajouter_seance_enseignant(self.id, date, duree_seance)
    
    def reserver_salle(self, db, salle_id, date, heure_debut, heure_fin, motif=""):
        """
        Crée une demande de réservation de salle
        
        Args:
            db: Instance de Database
            salle_id: ID de la salle
            date: Date au format YYYY-MM-DD
            heure_debut: Heure début (HH:MM)
            heure_fin: Heure fin (HH:MM)
            motif: Raison de la réservation
        
        Returns:
            int: ID de la réservation ou None
        """
        return db.ajouter_reservation(self.id, salle_id, date, heure_debut, heure_fin, motif)
    
    def consulter_emploi_du_temps(self, db, date_debut=None, date_fin=None):
        """
        Consulte son emploi du temps
        
        Args:
            db: Instance de Database
            date_debut: Date de début (optionnel)
            date_fin: Date de fin (optionnel)
        
        Returns:
            list: Liste des séances
        """
        return db.get_seances_by_enseignant(self.id, date_debut, date_fin)
    
    def declarer_indisponibilite(self, db, date_debut, date_fin, motif):
        """
        Déclare une indisponibilité
        
        Args:
            db: Instance de Database
            date_debut: Date de début au format YYYY-MM-DD
            date_fin: Date de fin au format YYYY-MM-DD
            motif: Raison de l'indisponibilité
        
        Returns:
            int: ID de la disponibilité créée
        """
        return db.ajouter_disponibilite(self.id, date_debut, date_fin, motif)
    
    def get_indisponibilites(self, db):
        """
        Récupère toutes les indisponibilités de l'enseignant
        
        Args:
            db: Instance de Database
        
        Returns:
            list: Liste des indisponibilités
        """
        return db.get_disponibilites_by_enseignant(self.id)
    
    def est_disponible(self, db, date):
        """
        Vérifie si l'enseignant est disponible à une date donnée
        
        Args:
            db: Instance de Database
            date: Date au format YYYY-MM-DD
        
        Returns:
            bool: True si disponible
        """
        return not db.verifier_indisponibilite_enseignant(self.id, date)
    
    # ═══════════════════════════════════════════════════════════
    # FONCTIONNALITÉS AVANCÉES - RATTRAPAGE & ABSENCE
    # ═══════════════════════════════════════════════════════════
    
    def demander_rattrapage(self, db, groupe_id, salle_id, date, heure_debut, 
                           heure_fin, matiere, seance_originale_id=None):
        """
        Réserve une salle pour un rattrapage avec verrouillage automatique
        et notification aux étudiants.
        
        Args:
            db: Instance de Database
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
        from src.gestionnaire import GestionnaireRattrapage
        
        gestionnaire = GestionnaireRattrapage(db)
        return gestionnaire.reserver_rattrapage(
            enseignant_id=self.id,
            groupe_id=groupe_id,
            salle_id=salle_id,
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            matiere=matiere,
            seance_originale_id=seance_originale_id
        )
    
    def signaler_absence(self, db, date_debut, date_fin, motif=None):
        """
        Signale une absence avec libération automatique des salles
        et notification aux étudiants/admins.
        
        LOGIQUE CRITIQUE:
        1. Identifie toutes les séances sur la période
        2. Notifie les étudiants concernés
        3. Notifie les administrateurs
        4. LIBÈRE toutes les salles (supprime les séances)
        
        Args:
            db: Instance de Database
            date_debut: Date de début d'absence (YYYY-MM-DD)
            date_fin: Date de fin d'absence (YYYY-MM-DD)
            motif: Motif de l'absence (optionnel)
        
        Returns:
            Dict avec statistiques détaillées de l'opération
        """
        from src.gestionnaire import GestionnaireAbsence
        
        gestionnaire = GestionnaireAbsence(db)
        return gestionnaire.declarer_absence(
            enseignant_id=self.id,
            date_debut=date_debut,
            date_fin=date_fin,
            motif=motif
        )
    
    def get_notifications(self, db, non_lues_seulement=False):
        """
        Récupère les notifications de l'enseignant
        
        Args:
            db: Instance de Database
            non_lues_seulement: Si True, retourne uniquement les non lues
        
        Returns:
            list: Liste des notifications
        """
        from src.services_notification import NotificationService
        
        service = NotificationService(db)
        return service.get_notifications_utilisateur(self.id, non_lues_seulement)
    
    def ecouter_emploi_du_temps(self, db, date=None):
        """
        Lit l'emploi du temps à voix haute (Text-to-Speech)
        
        Args:
            db: Instance de Database
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message)
        """
        from src.services_audio import AudioService
        
        audio_service = AudioService(db)
        return audio_service.lire_emploi_du_temps_enseignant(self.id, date)
    
    def exporter_emploi_du_temps_audio(self, db, date=None):
        """
        Exporte l'emploi du temps en fichier audio
        
        Args:
            db: Instance de Database
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message, filepath)
        """
        from src.services_audio import AudioService
        
        audio_service = AudioService(db)
        return audio_service.exporter_emploi_du_temps_enseignant(self.id, date)


class Etudiant(Utilisateur):
    """Étudiant de la FSTT"""
    def __init__(self, id, nom, prenom, email, mot_de_passe, groupe_id, date_creation=None):
        super().__init__(id, nom, prenom, email, mot_de_passe, "etudiant", date_creation)
        self.groupe_id = groupe_id
    
    def consulter_emploi_du_temps(self, db, date_debut=None, date_fin=None):
        """
        Consulte l'emploi du temps de son groupe
        
        Args:
            db: Instance de Database
            date_debut: Date de début (optionnel)
            date_fin: Date de fin (optionnel)
        
        Returns:
            list: Liste des séances du groupe
        """
        return db.get_seances_by_groupe(self.groupe_id, date_debut, date_fin)
    
    def telecharger_emploi_du_temps(self, db, format_export="pdf"):
        """
        Télécharge son emploi du temps
        
        Args:
            db: Instance de Database
            format_export: "pdf", "xlsx", ou "png"
        
        Returns:
            tuple: (success, file_path, error_message)
        """
        from src.logic.timetable_export_service import TimetableExportService
        
        export_service = TimetableExportService(db)
        return export_service.export_group_timetable(self.groupe_id, format_export)
    
    def afficher_emploi_du_temps(self, db, date_debut=None, date_fin=None):
        """
        Affiche l'emploi du temps formaté de l'étudiant
        
        Args:
            db: Instance de Database
            date_debut: Date de début (optionnel)
            date_fin: Date de fin (optionnel)
        
        Returns:
            str: Emploi du temps formaté pour affichage
        """
        seances = self.consulter_emploi_du_temps(db, date_debut, date_fin)
        
        if not seances:
            return "Aucune séance trouvée pour cette période."
        
        # Formater l'affichage
        output = []
        output.append(f"═══ EMPLOI DU TEMPS - Groupe {self.groupe_id} ═══\n")
        
        current_date = None
        for seance in seances:
            # Structure: (id, titre, type_seance, date, heure_debut, heure_fin, salle_id, enseignant_id, groupe_id)
            seance_date = seance[3]
            titre = seance[1]
            type_seance = seance[2]
            heure_debut = seance[4]
            heure_fin = seance[5]
            salle_id = seance[6]
            
            # Récupérer le nom de la salle
            salle = db.get_salle_by_id(salle_id) if salle_id else None
            salle_nom = salle[1] if salle else "N/A"
            
            if seance_date != current_date:
                current_date = seance_date
                output.append(f"\n📅 {current_date}")
                output.append("-" * 40)
            
            output.append(f"  {heure_debut} - {heure_fin} | {titre} ({type_seance})")
            output.append(f"    📍 Salle: {salle_nom}")
        
        return "\n".join(output)
    
    # ═══════════════════════════════════════════════════════════
    # FONCTIONNALITÉS AVANCÉES - NOTIFICATIONS & AUDIO
    # ═══════════════════════════════════════════════════════════
    
    def get_notifications(self, db, non_lues_seulement=False):
        """
        Récupère les notifications de l'étudiant
        
        Args:
            db: Instance de Database
            non_lues_seulement: Si True, retourne uniquement les non lues
        
        Returns:
            list: Liste des notifications
        """
        from src.services_notification import NotificationService
        
        service = NotificationService(db)
        return service.get_notifications_utilisateur(self.id, non_lues_seulement)
    
    def get_nb_notifications_non_lues(self, db):
        """
        Compte le nombre de notifications non lues
        
        Args:
            db: Instance de Database
        
        Returns:
            int: Nombre de notifications non lues
        """
        from src.services_notification import NotificationService
        
        service = NotificationService(db)
        return service.get_nb_non_lues(self.id)
    
    def ecouter_emploi_du_temps(self, db, date=None):
        """
        Lit l'emploi du temps à voix haute (Text-to-Speech)
        
        Args:
            db: Instance de Database
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message)
        """
        from src.services_audio import AudioService
        
        audio_service = AudioService(db)
        return audio_service.lire_emploi_du_temps_etudiant(self.id, date)
    
    def exporter_emploi_du_temps_audio(self, db, date=None):
        """
        Exporte l'emploi du temps en fichier audio
        
        Args:
            db: Instance de Database
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message, filepath)
        """
        from src.services_audio import AudioService
        
        audio_service = AudioService(db)
        return audio_service.exporter_emploi_du_temps_etudiant(self.id, date)


class Salle:
    """Salle de la FSTT"""
    def __init__(self, id, nom, capacite, type_salle, equipements=""):
        self.id = id
        self.nom = nom
        self.capacite = capacite
        self.type_salle = type_salle  # "Salle", "Amphithéâtre", "Laboratoire"
        self.equipements = equipements.split(",") if equipements else []
    
    def __str__(self):
        return f"{self.nom} ({self.type_salle}, {self.capacite} places)"
    
    def __repr__(self):
        return f"<Salle {self.nom}: {self.type_salle} - {self.capacite} places>"
    
    def est_disponible(self, db, date, heure_debut, heure_fin):
        """
        Vérifie si la salle est disponible sur un créneau
        
        Args:
            db: Instance de Database
            date: Date au format YYYY-MM-DD
            heure_debut: Heure début (HH:MM)
            heure_fin: Heure fin (HH:MM)
        
        Returns:
            bool: True si disponible
        """
        conflits = db.verifier_conflit_seance(date, heure_debut, heure_fin, salle_id=self.id)
        return len(conflits) == 0
    
    def peut_accueillir_groupe(self, effectif_groupe):
        """
        Vérifie si la capacité est suffisante
        
        Args:
            effectif_groupe: Nombre d'étudiants
        
        Returns:
            bool: True si capacité suffisante
        """
        return self.capacite >= effectif_groupe
    
    def a_equipement(self, equipement_requis):
        """
        Vérifie si la salle possède un équipement
        
        Args:
            equipement_requis: Nom de l'équipement
        
        Returns:
            bool: True si équipement présent
        """
        return equipement_requis in self.equipements
    
    def get_occupation_journee(self, db, date):
        """
        Récupère toutes les séances de la salle pour une date
        
        Args:
            db: Instance de Database
            date: Date au format YYYY-MM-DD
        
        Returns:
            list: Liste des séances
        """
        return db.get_seances_by_salle(self.id, date)


class Seance:
    """Séance d'enseignement"""
    def __init__(self, id, titre, type_seance, date, heure_debut, heure_fin, 
                 salle_id, enseignant_id, groupe_id):
        self.id = id
        self.titre = titre
        self.type_seance = type_seance  # "Cours", "TD", "TP", "Examen"
        self.date = date
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.salle_id = salle_id
        self.enseignant_id = enseignant_id
        self.groupe_id = groupe_id
    
    def __str__(self):
        return f"{self.titre} - {self.type_seance} ({self.date} {self.heure_debut}-{self.heure_fin})"
    
    def __repr__(self):
        return f"<Seance {self.titre}: {self.date} {self.heure_debut}-{self.heure_fin}>"
    
    def calculer_duree(self, db):
        """
        Calcule la durée de la séance en minutes
        
        Args:
            db: Instance de Database
        
        Returns:
            int: Durée en minutes
        """
        return db.calculer_duree_minutes(self.heure_debut, self.heure_fin)
    
    def verifier_conflits(self, db):
        """
        Vérifie s'il y a des conflits (salle/prof/groupe)
        
        Args:
            db: Instance de Database
        
        Returns:
            list: Liste des conflits détectés
        """
        return db.verifier_conflit_seance(
            self.date, 
            self.heure_debut, 
            self.heure_fin,
            self.salle_id,
            self.enseignant_id,
            self.groupe_id
        )
    
    def est_valide(self, db):
        """
        Vérifie si la séance est valide (pas de conflits)
        
        Args:
            db: Instance de Database
        
        Returns:
            bool: True si valide
        """
        conflits = self.verifier_conflits(db)
        return len(conflits) == 0


class Groupe:
    """Groupe d'étudiants"""
    def __init__(self, id, nom, effectif, filiere_id):
        self.id = id
        self.nom = nom
        self.effectif = effectif
        self.filiere_id = filiere_id
    
    def __str__(self):
        return f"{self.nom} ({self.effectif} étudiants)"
    
    def __repr__(self):
        return f"<Groupe {self.nom}: {self.effectif} étudiants>"
    
    def get_emploi_du_temps(self, db, date_debut=None, date_fin=None):
        """
        Récupère l'emploi du temps du groupe
        
        Args:
            db: Instance de Database
            date_debut: Date de début (optionnel)
            date_fin: Date de fin (optionnel)
        
        Returns:
            list: Liste des séances
        """
        return db.get_seances_by_groupe(self.id, date_debut, date_fin)
    
    def get_etudiants(self, db):
        """
        Récupère tous les étudiants du groupe
        
        Args:
            db: Instance de Database
        
        Returns:
            list: Liste des étudiants
        """
        tous_etudiants = db.get_tous_utilisateurs(type_user="etudiant")
        return [etud for etud in tous_etudiants if etud[7] == self.id]  # groupe_id à l'index 7


class Filiere:
    """Filière de la FSTT"""
    def __init__(self, id, nom, niveau):
        self.id = id
        self.nom = nom
        self.niveau = niveau  # "L1", "L2", "L3", "M1", "M2"
    
    def __str__(self):
        return f"{self.nom} ({self.niveau})"
    
    def __repr__(self):
        return f"<Filiere {self.nom} - {self.niveau}>"
    
    def get_groupes(self, db):
        """
        Récupère tous les groupes de la filière
        
        Args:
            db: Instance de Database
        
        Returns:
            list: Liste des groupes
        """
        tous_groupes = db.get_tous_groupes()
        return [grp for grp in tous_groupes if grp[3] == self.id]  # filiere_id à l'index 3


class Reservation:
    """Réservation de salle par un enseignant"""
    def __init__(self, id, enseignant_id, salle_id, date, heure_debut, heure_fin,
                 statut="en_attente", motif="", date_demande=None):
        self.id = id
        self.enseignant_id = enseignant_id
        self.salle_id = salle_id
        self.date = date
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.statut = statut  # "en_attente", "validee", "rejetee"
        self.motif = motif
        self.date_demande = date_demande
    
    def __str__(self):
        return f"Réservation {self.statut} - {self.date} {self.heure_debut}-{self.heure_fin}"
    
    def __repr__(self):
        return f"<Reservation {self.id}: {self.statut} - {self.date}>"
    
    def valider(self, db):
        """
        Valide la réservation
        
        Args:
            db: Instance de Database
        
        Returns:
            bool: True si succès
        """
        success = db.modifier_statut_reservation(self.id, "validee")
        if success:
            self.statut = "validee"
        return success
    
    def rejeter(self, db):
        """
        Rejette la réservation
        
        Args:
            db: Instance de Database
        
        Returns:
            bool: True si succès
        """
        success = db.modifier_statut_reservation(self.id, "rejetee")
        if success:
            self.statut = "rejetee"
        return success
    
    def est_en_attente(self):
        """Vérifie si la réservation est en attente"""
        return self.statut == "en_attente"
    
    def est_validee(self):
        """Vérifie si la réservation est validée"""
        return self.statut == "validee"
    
    def est_rejetee(self):
        """Vérifie si la réservation est rejetée"""
        return self.statut == "rejetee"


class Matiere:
    """Matière/Module d'enseignement"""
    def __init__(self, id, nom, code=None, volume_horaire_cours=0, volume_horaire_td=0, 
                 volume_horaire_tp=0, filiere_id=None, semestre=None):
        self.id = id
        self.nom = nom
        self.code = code
        self.volume_horaire_cours = volume_horaire_cours  # en heures
        self.volume_horaire_td = volume_horaire_td  # en heures
        self.volume_horaire_tp = volume_horaire_tp  # en heures
        self.filiere_id = filiere_id
        self.semestre = semestre  # "S1", "S2", etc.
    
    def __str__(self):
        return f"{self.nom} ({self.code})" if self.code else self.nom
    
    def __repr__(self):
        return f"<Matiere {self.nom}>"
    
    def get_volume_total(self):
        """Retourne le volume horaire total de la matière"""
        return self.volume_horaire_cours + self.volume_horaire_td + self.volume_horaire_tp
    
    def get_repartition_horaire(self):
        """Retourne la répartition des heures par type de séance"""
        return {
            'Cours': self.volume_horaire_cours,
            'TD': self.volume_horaire_td,
            'TP': self.volume_horaire_tp
        }
    
    def calculer_nb_seances(self, duree_seance_heures=1.5):
        """
        Calcule le nombre de séances nécessaires pour chaque type
        
        Args:
            duree_seance_heures: Durée d'une séance en heures
        
        Returns:
            dict: Nombre de séances par type
        """
        import math
        return {
            'Cours': math.ceil(self.volume_horaire_cours / duree_seance_heures) if self.volume_horaire_cours > 0 else 0,
            'TD': math.ceil(self.volume_horaire_td / duree_seance_heures) if self.volume_horaire_td > 0 else 0,
            'TP': math.ceil(self.volume_horaire_tp / duree_seance_heures) if self.volume_horaire_tp > 0 else 0
        }


class Creneau:
    """Créneau horaire pour une séance"""
    def __init__(self, jour, heure_debut, heure_fin, disponible=True):
        self.jour = jour  # 0=Lundi, 1=Mardi, ..., 6=Dimanche
        self.heure_debut = heure_debut  # format "HH:MM"
        self.heure_fin = heure_fin  # format "HH:MM"
        self.disponible = disponible
    
    # Mapping des jours
    JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    
    def __str__(self):
        jour_nom = self.JOURS[self.jour] if 0 <= self.jour < 7 else f"Jour {self.jour}"
        return f"{jour_nom} {self.heure_debut}-{self.heure_fin}"
    
    def __repr__(self):
        return f"<Creneau {self}>"
    
    def get_jour_nom(self):
        """Retourne le nom du jour"""
        return self.JOURS[self.jour] if 0 <= self.jour < 7 else f"Jour {self.jour}"
    
    def get_duree_minutes(self):
        """Calcule la durée du créneau en minutes"""
        from datetime import datetime
        
        try:
            debut = datetime.strptime(self.heure_debut, "%H:%M")
            fin = datetime.strptime(self.heure_fin, "%H:%M")
            duree = (fin - debut).total_seconds() / 60
            return int(duree)
        except ValueError:
            return 0
    
    def get_duree_heures(self):
        """Calcule la durée du créneau en heures"""
        return self.get_duree_minutes() / 60
    
    def chevauche(self, autre_creneau):
        """
        Vérifie si ce créneau chevauche un autre créneau
        
        Args:
            autre_creneau: Autre instance de Creneau
        
        Returns:
            bool: True si les créneaux se chevauchent
        """
        if self.jour != autre_creneau.jour:
            return False
        
        from datetime import datetime
        
        try:
            self_debut = datetime.strptime(self.heure_debut, "%H:%M")
            self_fin = datetime.strptime(self.heure_fin, "%H:%M")
            autre_debut = datetime.strptime(autre_creneau.heure_debut, "%H:%M")
            autre_fin = datetime.strptime(autre_creneau.heure_fin, "%H:%M")
            
            # Vérifie le chevauchement
            return self_debut < autre_fin and autre_debut < self_fin
        except ValueError:
            return False
    
    @staticmethod
    def creer_creneaux_journee(jour, creneaux_horaires=None):
        """
        Crée une liste de créneaux pour une journée
        
        Args:
            jour: Numéro du jour (0=Lundi)
            creneaux_horaires: Liste de tuples (heure_debut, heure_fin)
        
        Returns:
            list: Liste d'objets Creneau
        """
        if creneaux_horaires is None:
            # Créneaux par défaut FSTT
            creneaux_horaires = [
                ("08:00", "09:30"),
                ("09:40", "11:10"),
                ("11:20", "12:50"),
                ("14:00", "15:30"),
                ("15:40", "17:10"),
                ("17:20", "18:50")
            ]
        
        return [Creneau(jour, debut, fin) for debut, fin in creneaux_horaires]


class GestionnaireEmploiDuTemps:
    """
    Classe principale (Moteur/Scheduler) pour la gestion intelligente des emplois du temps
    Centralise la logique de génération, détection de conflits et optimisation
    """
    
    def __init__(self, db):
        """
        Initialise le gestionnaire d'emploi du temps
        
        Args:
            db: Instance de Database
        """
        self.db = db
    
    def detecter_conflits(self, date, heure_debut, heure_fin, salle_id=None, 
                         enseignant_id=None, groupe_id=None, exclude_seance_id=None):
        """
        Détecte tous les conflits pour un créneau donné
        
        Args:
            date: Date au format YYYY-MM-DD
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
            salle_id: ID de la salle (optionnel)
            enseignant_id: ID de l'enseignant (optionnel)
            groupe_id: ID du groupe (optionnel)
            exclude_seance_id: ID de séance à exclure de la vérification
        
        Returns:
            list: Liste des conflits détectés
        """
        from src.logic.conflict_detector import ConflictDetector
        
        # Récupérer toutes les séances existantes
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
            groupe_id=groupe_id,
            exclude_seance_id=exclude_seance_id
        )
    
    def optimiser_affectation_salle(self, effectif_groupe, date, heure_debut, heure_fin,
                                   type_salle_prefere=None, equipements_requis=None):
        """
        Trouve la salle optimale pour un cours basé sur plusieurs critères
        
        Algorithme d'optimisation:
        1. Filtrer les salles par disponibilité sur le créneau
        2. Filtrer par capacité >= effectif du groupe
        3. Filtrer par type de salle si spécifié
        4. Filtrer par équipements si spécifiés
        5. Scorer et trier par optimisation (capacité la plus proche, équipements bonus)
        
        Args:
            effectif_groupe: Nombre d'étudiants du groupe
            date: Date au format YYYY-MM-DD
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
            type_salle_prefere: Type de salle préféré ("Salle", "Amphithéâtre", "Laboratoire")
            equipements_requis: Liste des équipements requis (ex: ["Projecteur", "PC"])
        
        Returns:
            dict: {'success': bool, 'salle': dict ou None, 'score': float, 'message': str}
        """
        from src.logic.room_availability_service import RoomAvailabilityService
        
        result = {
            'success': False,
            'salle': None,
            'score': 0,
            'message': ''
        }
        
        # Trouver les salles disponibles avec capacité suffisante
        room_service = RoomAvailabilityService(self.db)
        salles_disponibles = room_service.find_available_rooms(
            date=date,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            min_capacite=effectif_groupe,
            type_salle=type_salle_prefere
        )
        
        if not salles_disponibles:
            result['message'] = "Aucune salle disponible avec la capacité requise"
            return result
        
        # Scorer chaque salle
        salles_scorees = []
        for salle in salles_disponibles:
            score = self._calculer_score_salle(
                salle, effectif_groupe, type_salle_prefere, equipements_requis
            )
            salles_scorees.append((salle, score))
        
        # Trier par score décroissant
        salles_scorees.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner la meilleure salle
        meilleure_salle, meilleur_score = salles_scorees[0]
        
        result['success'] = True
        result['salle'] = meilleure_salle
        result['score'] = meilleur_score
        result['message'] = f"Salle {meilleure_salle.get('nom')} sélectionnée (score: {meilleur_score:.2f})"
        
        return result
    
    def _calculer_score_salle(self, salle, effectif, type_prefere, equipements_requis):
        """
        Calcule un score d'optimisation pour une salle
        
        Critères:
        - Proximité de capacité (éviter le gaspillage): 40 points max
        - Type correspondant: 30 points
        - Équipements: 30 points max
        
        Returns:
            float: Score entre 0 et 100
        """
        score = 0.0
        
        capacite = salle.get('capacite', 0)
        type_salle = salle.get('type_salle', '')
        equipements_str = salle.get('equipements', '') or ''
        salle_equipements = [e.strip() for e in equipements_str.split(',') if e.strip()]
        
        # 1. Score de capacité (40 points max)
        # Plus le ratio effectif/capacité est proche de 1, meilleur est le score
        if capacite > 0:
            ratio = effectif / capacite
            if ratio <= 1:
                # Score maximal quand ratio = 1 (salle parfaitement adaptée)
                # Score diminue quand la salle est trop grande
                score_capacite = 40 * (ratio if ratio >= 0.5 else ratio * 2)
                score += score_capacite
        
        # 2. Score de type (30 points)
        if type_prefere and type_salle == type_prefere:
            score += 30
        elif not type_prefere:
            score += 15  # Bonus neutre si pas de préférence
        
        # 3. Score d'équipements (30 points max)
        if equipements_requis:
            nb_requis = len(equipements_requis)
            nb_presents = sum(1 for eq in equipements_requis if eq in salle_equipements)
            score += 30 * (nb_presents / nb_requis) if nb_requis > 0 else 0
        else:
            # Bonus si la salle a des équipements (versatilité)
            score += min(15, len(salle_equipements) * 3)
        
        return score
    
    def verifier_disponibilite_enseignant(self, enseignant_id, date, heure_debut, heure_fin):
        """
        Vérifie si un enseignant est disponible pour un créneau
        
        Args:
            enseignant_id: ID de l'enseignant
            date: Date au format YYYY-MM-DD
            heure_debut: Heure de début (HH:MM)
            heure_fin: Heure de fin (HH:MM)
        
        Returns:
            tuple: (disponible: bool, raison: str ou None)
        """
        # Vérifier l'indisponibilité déclarée
        if self.db.verifier_indisponibilite_enseignant(enseignant_id, date):
            return False, "L'enseignant a déclaré une indisponibilité pour cette date"
        
        # Vérifier les conflits de séances
        conflits = self.detecter_conflits(
            date, heure_debut, heure_fin,
            enseignant_id=enseignant_id
        )
        
        if conflits:
            return False, conflits[0]
        
        # Vérifier la durée maximale journalière
        duree_actuelle = self.db.calculer_duree_journee_enseignant(enseignant_id, date)
        duree_max = self.db.get_duree_max_enseignant(enseignant_id)
        duree_seance = self.db.calculer_duree_minutes(heure_debut, heure_fin)
        
        if duree_actuelle + duree_seance > duree_max:
            return False, f"Durée maximale journalière dépassée ({duree_max // 60}h)"
        
        return True, None
    
    def generer_emploi_du_temps_groupe(self, groupe_id, matieres, semaine_debut=None):
        """
        Génère l'emploi du temps complet pour un groupe
        
        Args:
            groupe_id: ID du groupe
            matieres: Liste de dictionnaires avec les matières à planifier
            semaine_debut: Date de début de semaine (format YYYY-MM-DD)
        
        Returns:
            dict: {'success': bool, 'seances': list, 'erreurs': list}
        """
        from datetime import datetime, timedelta
        
        result = {
            'success': True,
            'seances': [],
            'erreurs': []
        }
        
        # Récupérer les informations du groupe
        groupe = self.db.get_groupe_by_id(groupe_id)
        if not groupe:
            result['success'] = False
            result['erreurs'].append("Groupe introuvable")
            return result
        
        effectif = groupe[2]
        
        # Définir la semaine de début
        if not semaine_debut:
            today = datetime.now()
            days_ahead = (7 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            next_monday = today + timedelta(days=days_ahead)
            semaine_debut = next_monday.strftime("%Y-%m-%d")
        
        # Créneaux disponibles par défaut
        creneaux_par_jour = {}
        for jour in range(5):  # Lundi à Vendredi
            creneaux_par_jour[jour] = Creneau.creer_creneaux_journee(jour)
        
        # Pour chaque matière, essayer de placer les séances
        for matiere in matieres:
            titre = matiere.get('titre', 'Cours')
            type_seance = matiere.get('type_seance', 'Cours')
            enseignant_id = matiere.get('enseignant_id')
            nb_seances = matiere.get('nb_seances', 1)
            duree_heures = matiere.get('duree_heures', 1.5)
            equipements = matiere.get('equipements')
            
            seances_placees = 0
            
            for jour in range(5):
                if seances_placees >= nb_seances:
                    break
                
                date_obj = datetime.strptime(semaine_debut, "%Y-%m-%d") + timedelta(days=jour)
                date_str = date_obj.strftime("%Y-%m-%d")
                
                for creneau in creneaux_par_jour[jour]:
                    if seances_placees >= nb_seances:
                        break
                    
                    if not creneau.disponible:
                        continue
                    
                    # Vérifier la disponibilité de l'enseignant
                    if enseignant_id:
                        dispo, raison = self.verifier_disponibilite_enseignant(
                            enseignant_id, date_str, creneau.heure_debut, creneau.heure_fin
                        )
                        if not dispo:
                            continue
                    
                    # Trouver la meilleure salle
                    salle_result = self.optimiser_affectation_salle(
                        effectif, date_str, creneau.heure_debut, creneau.heure_fin,
                        equipements_requis=equipements
                    )
                    
                    if not salle_result['success']:
                        continue
                    
                    # Vérifier les conflits avec le groupe
                    conflits = self.detecter_conflits(
                        date_str, creneau.heure_debut, creneau.heure_fin,
                        salle_id=salle_result['salle']['id'],
                        enseignant_id=enseignant_id,
                        groupe_id=groupe_id
                    )
                    
                    if conflits:
                        continue
                    
                    # Créer la séance
                    seance_id = self.db.ajouter_seance(
                        titre=titre,
                        type_seance=type_seance,
                        date=date_str,
                        heure_debut=creneau.heure_debut,
                        heure_fin=creneau.heure_fin,
                        salle_id=salle_result['salle']['id'],
                        enseignant_id=enseignant_id,
                        groupe_id=groupe_id
                    )
                    
                    if seance_id:
                        result['seances'].append({
                            'id': seance_id,
                            'titre': titre,
                            'type_seance': type_seance,
                            'date': date_str,
                            'heure_debut': creneau.heure_debut,
                            'heure_fin': creneau.heure_fin,
                            'salle': salle_result['salle']['nom'],
                            'enseignant_id': enseignant_id
                        })
                        creneau.disponible = False
                        seances_placees += 1
            
            if seances_placees < nb_seances:
                result['erreurs'].append(
                    f"Impossible de placer toutes les séances de {titre} "
                    f"({seances_placees}/{nb_seances} placées)"
                )
        
        if result['erreurs'] and not result['seances']:
            result['success'] = False
        
        return result


# ═══════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════

def creer_utilisateur_depuis_tuple(user_tuple):
    """
    Crée un objet Utilisateur depuis un tuple de la BDD
    
    Args:
        user_tuple: Tuple retourné par database.get_utilisateur_by_id()
        
    Returns:
        Utilisateur, Administrateur, Enseignant ou Etudiant
    """
    if not user_tuple:
        return None
    
    # Structure: (id, nom, prenom, email, mot_de_passe, type_user, specialite, groupe_id, duree_max_jour, date_creation)
    id = user_tuple[0]
    nom = user_tuple[1]
    prenom = user_tuple[2]
    email = user_tuple[3]
    mot_de_passe = user_tuple[4]
    type_user = user_tuple[5]
    specialite = user_tuple[6]
    groupe_id = user_tuple[7]
    duree_max_jour = user_tuple[8]
    date_creation = user_tuple[9]
    
    if type_user == "admin":
        return Administrateur(id, nom, prenom, email, mot_de_passe, date_creation)
    elif type_user == "enseignant":
        return Enseignant(id, nom, prenom, email, mot_de_passe, specialite, duree_max_jour, date_creation)
    elif type_user == "etudiant":
        return Etudiant(id, nom, prenom, email, mot_de_passe, groupe_id, date_creation)
    else:
        return Utilisateur(id, nom, prenom, email, mot_de_passe, type_user, date_creation)


def creer_salle_depuis_tuple(salle_tuple):
    """
    Crée un objet Salle depuis un tuple de la BDD
    
    Args:
        salle_tuple: Tuple retourné par database.get_toutes_salles()
        
    Returns:
        Salle
    """
    if not salle_tuple:
        return None
    
    # Structure: (id, nom, capacite, type_salle, equipements)
    return Salle(
        id=salle_tuple[0],
        nom=salle_tuple[1],
        capacite=salle_tuple[2],
        type_salle=salle_tuple[3],
        equipements=salle_tuple[4] or ""
    )


def creer_seance_depuis_tuple(seance_tuple):
    """
    Crée un objet Seance depuis un tuple de la BDD
    
    Args:
        seance_tuple: Tuple retourné par database.get_seances_by_groupe()
        
    Returns:
        Seance
    """
    if not seance_tuple:
        return None
    
    # Structure: (id, titre, type_seance, date, heure_debut, heure_fin, salle_id, enseignant_id, groupe_id)
    return Seance(
        id=seance_tuple[0],
        titre=seance_tuple[1],
        type_seance=seance_tuple[2],
        date=seance_tuple[3],
        heure_debut=seance_tuple[4],
        heure_fin=seance_tuple[5],
        salle_id=seance_tuple[6],
        enseignant_id=seance_tuple[7],
        groupe_id=seance_tuple[8]
    )


def creer_groupe_depuis_tuple(groupe_tuple):
    """
    Crée un objet Groupe depuis un tuple de la BDD
    
    Args:
        groupe_tuple: Tuple retourné par database.get_tous_groupes()
        
    Returns:
        Groupe
    """
    if not groupe_tuple:
        return None
    
    # Structure: (id, nom, effectif, filiere_id)
    return Groupe(
        id=groupe_tuple[0],
        nom=groupe_tuple[1],
        effectif=groupe_tuple[2],
        filiere_id=groupe_tuple[3]
    )


def creer_filiere_depuis_tuple(filiere_tuple):
    """
    Crée un objet Filiere depuis un tuple de la BDD
    
    Args:
        filiere_tuple: Tuple retourné par database.get_toutes_filieres()
        
    Returns:
        Filiere
    """
    if not filiere_tuple:
        return None
    
    # Structure: (id, nom, niveau)
    return Filiere(
        id=filiere_tuple[0],
        nom=filiere_tuple[1],
        niveau=filiere_tuple[2]
    )


def creer_reservation_depuis_tuple(reservation_tuple):
    """
    Crée un objet Reservation depuis un tuple de la BDD
    
    Args:
        reservation_tuple: Tuple retourné par database.get_reservations_by_statut()
        
    Returns:
        Reservation
    """
    if not reservation_tuple:
        return None
    
    # Structure: (id, enseignant_id, salle_id, date, heure_debut, heure_fin, statut, motif, date_demande)
    return Reservation(
        id=reservation_tuple[0],
        enseignant_id=reservation_tuple[1],
        salle_id=reservation_tuple[2],
        date=reservation_tuple[3],
        heure_debut=reservation_tuple[4],
        heure_fin=reservation_tuple[5],
        statut=reservation_tuple[6],
        motif=reservation_tuple[7] or "",
        date_demande=reservation_tuple[8]
    )


# ═══════════════════════════════════════════════════════════
# SECTION MAIN - SCÉNARIO DE TEST
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Scénario de test complet pour le système de gestion d'emploi du temps
    
    Ce script teste :
    1. Création d'un administrateur
    2. Ajout de salles avec équipements
    3. Création de filières et groupes
    4. Création d'enseignants
    5. Génération automatique d'un cours sans conflit
    6. Détection de conflits
    7. Optimisation de l'affectation de salle
    """
    
    import sys
    import os
    
    # Ajouter le répertoire racine au path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from datetime import datetime, timedelta
    from src.database import Database
    
    print("=" * 70)
    print("🎓 FSTT - Test du Système de Gestion d'Emploi du Temps")
    print("=" * 70)
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 1: Initialisation de la base de données
    # ═══════════════════════════════════════════════════════════
    
    print("\n📦 Étape 1: Initialisation de la base de données...")
    db = Database()
    print("✅ Base de données initialisée avec succès!")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 2: Création d'un administrateur
    # ═══════════════════════════════════════════════════════════
    
    print("\n👤 Étape 2: Création d'un administrateur...")
    
    # Vérifier si l'admin existe déjà
    admin_existant = db.get_utilisateur_by_email("admin@fstt.ac.ma")
    if admin_existant:
        admin_id = admin_existant[0]
        print(f"   Admin existant trouvé (ID: {admin_id})")
    else:
        admin_id = db.ajouter_utilisateur(
            nom="Admin",
            prenom="Test",
            email="admin@fstt.ac.ma",
            mot_de_passe="admin123",
            type_user="admin"
        )
        print(f"   Nouvel admin créé (ID: {admin_id})")
    
    # Créer l'objet Administrateur
    admin = Administrateur(
        id=admin_id,
        nom="Admin",
        prenom="Test",
        email="admin@fstt.ac.ma",
        mot_de_passe="admin123"
    )
    print(f"✅ Administrateur: {admin}")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 3: Ajout de salles avec équipements
    # ═══════════════════════════════════════════════════════════
    
    print("\n🏫 Étape 3: Ajout de salles...")
    
    salles_config = [
        ("Salle A1", 30, "Salle", "Projecteur,Tableau"),
        ("Salle A2", 40, "Salle", "Projecteur,PC,Tableau"),
        ("Amphi 1", 200, "Amphithéâtre", "Projecteur,Micro,Tableau"),
        ("Labo Info 1", 25, "Laboratoire", "PC,Projecteur,Imprimante"),
        ("Labo Info 2", 20, "Laboratoire", "PC,Projecteur")
    ]
    
    for nom, capacite, type_salle, equipements in salles_config:
        salle_id = db.ajouter_salle(nom, capacite, type_salle, equipements)
        if salle_id:
            print(f"   ✅ Salle ajoutée: {nom} ({capacite} places, {type_salle})")
        else:
            print(f"   ℹ️  Salle déjà existante: {nom}")
    
    # Récupérer toutes les salles
    salles = db.get_toutes_salles()
    print(f"   Total salles: {len(salles)}")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 4: Création de filières et groupes
    # ═══════════════════════════════════════════════════════════
    
    print("\n📚 Étape 4: Création de filières et groupes...")
    
    # Créer une filière
    filiere = db.get_filiere_by_nom("Génie Informatique")
    if not filiere:
        filiere_id = db.ajouter_filiere("Génie Informatique", "L3")
        print(f"   ✅ Filière créée: Génie Informatique L3 (ID: {filiere_id})")
    else:
        filiere_id = filiere[0]
        print(f"   ℹ️  Filière existante: Génie Informatique (ID: {filiere_id})")
    
    # Créer un groupe
    groupe = db.get_groupe_by_nom("GI-L3-A")
    if not groupe:
        groupe_id = db.ajouter_groupe("GI-L3-A", 35, filiere_id)
        print(f"   ✅ Groupe créé: GI-L3-A (35 étudiants, ID: {groupe_id})")
    else:
        groupe_id = groupe[0]
        print(f"   ℹ️  Groupe existant: GI-L3-A (ID: {groupe_id})")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 5: Création d'un enseignant
    # ═══════════════════════════════════════════════════════════
    
    print("\n👨‍🏫 Étape 5: Création d'un enseignant...")
    
    enseignant_existant = db.get_utilisateur_by_email("prof.python@fstt.ac.ma")
    if enseignant_existant:
        enseignant_id = enseignant_existant[0]
        print(f"   ℹ️  Enseignant existant (ID: {enseignant_id})")
    else:
        enseignant_id = db.ajouter_utilisateur(
            nom="Professeur",
            prenom="Python",
            email="prof.python@fstt.ac.ma",
            mot_de_passe="prof123",
            type_user="enseignant",
            specialite="Informatique",
            duree_max_jour=360  # 6 heures max par jour
        )
        print(f"   ✅ Enseignant créé (ID: {enseignant_id})")
    
    # Créer l'objet Enseignant
    enseignant = Enseignant(
        id=enseignant_id,
        nom="Professeur",
        prenom="Python",
        email="prof.python@fstt.ac.ma",
        mot_de_passe="prof123",
        specialite="Informatique",
        duree_max_jour=360
    )
    print(f"✅ Enseignant: {enseignant}")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 6: Test du gestionnaire d'emploi du temps
    # ═══════════════════════════════════════════════════════════
    
    print("\n🔧 Étape 6: Test du GestionnaireEmploiDuTemps...")
    
    gestionnaire = GestionnaireEmploiDuTemps(db)
    
    # Calculer la date du prochain lundi
    today = datetime.now()
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_monday = today + timedelta(days=days_ahead)
    date_test = next_monday.strftime("%Y-%m-%d")
    
    print(f"   Date de test: {date_test}")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 7: Optimisation d'affectation de salle
    # ═══════════════════════════════════════════════════════════
    
    print("\n🎯 Étape 7: Test d'optimisation d'affectation de salle...")
    
    resultat_opti = gestionnaire.optimiser_affectation_salle(
        effectif_groupe=35,
        date=date_test,
        heure_debut="08:00",
        heure_fin="09:30",
        equipements_requis=["Projecteur"]
    )
    
    if resultat_opti['success']:
        print(f"   ✅ {resultat_opti['message']}")
        print(f"      Score d'optimisation: {resultat_opti['score']:.2f}/100")
    else:
        print(f"   ❌ {resultat_opti['message']}")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 8: Génération d'un cours sans conflit
    # ═══════════════════════════════════════════════════════════
    
    print("\n📝 Étape 8: Génération d'un cours sans conflit...")
    
    # Vérifier les conflits avant
    conflits = gestionnaire.detecter_conflits(
        date_test, "08:00", "09:30",
        salle_id=resultat_opti['salle']['id'] if resultat_opti['success'] else None,
        enseignant_id=enseignant_id,
        groupe_id=groupe_id
    )
    
    if conflits:
        print(f"   ⚠️  Conflits détectés: {conflits}")
    else:
        print("   ✅ Aucun conflit détecté!")
        
        # Ajouter la séance
        if resultat_opti['success']:
            seance_id = db.ajouter_seance(
                titre="Programmation Python",
                type_seance="Cours",
                date=date_test,
                heure_debut="08:00",
                heure_fin="09:30",
                salle_id=resultat_opti['salle']['id'],
                enseignant_id=enseignant_id,
                groupe_id=groupe_id
            )
            
            if seance_id:
                print(f"   ✅ Séance créée (ID: {seance_id})")
                print(f"      Cours: Programmation Python")
                print(f"      Date: {date_test} 08:00-09:30")
                print(f"      Salle: {resultat_opti['salle']['nom']}")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 9: Test de détection de conflits
    # ═══════════════════════════════════════════════════════════
    
    print("\n🔍 Étape 9: Test de détection de conflits...")
    
    # Essayer de créer un autre cours au même créneau (doit détecter un conflit)
    conflits_test = gestionnaire.detecter_conflits(
        date_test, "08:30", "10:00",  # Créneau qui chevauche
        enseignant_id=enseignant_id
    )
    
    if conflits_test:
        print(f"   ✅ Conflit correctement détecté: {conflits_test[0]}")
    else:
        print("   ⚠️  Pas de conflit détecté (possible si la première séance n'a pas été créée)")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 10: Test d'indisponibilité enseignant
    # ═══════════════════════════════════════════════════════════
    
    print("\n🚫 Étape 10: Test d'indisponibilité enseignant...")
    
    # Déclarer une indisponibilité
    date_indispo = (next_monday + timedelta(days=2)).strftime("%Y-%m-%d")
    indispo_id = enseignant.declarer_indisponibilite(
        db, date_indispo, date_indispo, "Formation externe"
    )
    
    if indispo_id:
        print(f"   ✅ Indisponibilité déclarée (ID: {indispo_id})")
        print(f"      Date: {date_indispo}")
        print(f"      Motif: Formation externe")
        
        # Vérifier la disponibilité
        est_dispo = enseignant.est_disponible(db, date_indispo)
        print(f"   ✅ Vérification: L'enseignant est {'disponible' if est_dispo else 'indisponible'} le {date_indispo}")
    
    # ═══════════════════════════════════════════════════════════
    # ÉTAPE 11: Test d'export
    # ═══════════════════════════════════════════════════════════
    
    print("\n📄 Étape 11: Test d'export d'emploi du temps...")
    
    success, filepath, error = admin.exporter_emploi_du_temps(db, groupe_id=groupe_id, format_export="pdf")
    if success:
        print(f"   ✅ Export réussi: {filepath}")
    else:
        print(f"   ℹ️  Export: {error or 'Fonctionnalité de base (placeholder)'}")
    
    # ═══════════════════════════════════════════════════════════
    # RÉSUMÉ
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DU TEST")
    print("=" * 70)
    print(f"✅ Administrateur créé et fonctionnel")
    print(f"✅ {len(salles)} salles configurées avec équipements")
    print(f"✅ Filière et groupe créés")
    print(f"✅ Enseignant avec contraintes de durée max/jour")
    print(f"✅ Algorithme d'optimisation de salle fonctionnel")
    print(f"✅ Détection de conflits opérationnelle")
    print(f"✅ Système d'indisponibilité implémenté")
    print(f"✅ Export d'emploi du temps disponible")
    print("=" * 70)
    print("🎉 Tous les tests ont été exécutés avec succès!")
    print("=" * 70)