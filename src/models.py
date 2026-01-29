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
    """Administrateur du système"""
    def __init__(self, id, nom, prenom, email, mot_de_passe, date_creation=None):
        super().__init__(id, nom, prenom, email, mot_de_passe, "admin", date_creation)
    
    def generer_emploi_du_temps(self, db, groupes, enseignants, salles, contraintes=None):
        """
        Génère automatiquement l'emploi du temps
        
        Args:
            db: Instance de Database
            groupes: Liste des groupes
            enseignants: Liste des enseignants
            salles: Liste des salles
            contraintes: Dictionnaire de contraintes supplémentaires
        
        Returns:
            bool: True si succès, False sinon
        """
        # À implémenter par l'équipe (algorithme de génération)
        pass
    
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
    
    def exporter_emploi_du_temps(self, format_export="pdf"):
        """
        Exporte l'emploi du temps
        
        Args:
            format_export: "pdf", "xlsx", ou "png"
        
        Returns:
            str: Chemin du fichier généré
        """
        # À implémenter par l'équipe (export)
        pass
    
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
            date_debut: Date de début
            date_fin: Date de fin
            motif: Raison de l'indisponibilité
        
        Returns:
            int: ID de la disponibilité
        """
        # À implémenter selon votre méthode dans database.py
        pass


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
    
    def telecharger_emploi_du_temps(self, format_export="pdf"):
        """
        Télécharge son emploi du temps
        
        Args:
            format_export: "pdf", "xlsx", ou "png"
        
        Returns:
            str: Chemin du fichier généré
        """
        # À implémenter par l'équipe (export)
        pass


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