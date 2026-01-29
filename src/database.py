# src/database.py
import sqlite3
import hashlib
import os
import shutil
from datetime import datetime
from config import DATABASE_PATH

class Database:
    """Classe pour gérer la base de données SQLite - FSTT"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def hash_password(self, password):
        """Hash un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ═══════════════════════════════════════════════════════════
    # CRÉATION DES TABLES
    # ═══════════════════════════════════════════════════════════
    
    def init_database(self):
        """Crée toutes les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table 1 : Utilisateurs (avec duree_max_jour)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL,
                type_user TEXT NOT NULL CHECK(type_user IN ('admin', 'enseignant', 'etudiant')),
                specialite TEXT,
                groupe_id INTEGER,
                duree_max_jour INTEGER DEFAULT 480,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (groupe_id) REFERENCES groupes(id) ON DELETE SET NULL
            )
        ''')
        
        # Table 2 : Filières
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filieres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                niveau TEXT NOT NULL CHECK(niveau IN ('L1', 'L2', 'L3', 'M1', 'M2'))
            )
        ''')
        
        # Table 3 : Groupes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groupes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                effectif INTEGER NOT NULL CHECK(effectif > 0),
                filiere_id INTEGER NOT NULL,
                FOREIGN KEY (filiere_id) REFERENCES filieres(id) ON DELETE CASCADE
            )
        ''')
        
        # Table 4 : Salles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                capacite INTEGER NOT NULL CHECK(capacite > 0),
                type_salle TEXT NOT NULL CHECK(type_salle IN ('Salle', 'Amphithéâtre', 'Laboratoire')),
                equipements TEXT
            )
        ''')
        
        # Table 5 : Séances
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                type_seance TEXT NOT NULL CHECK(type_seance IN ('Cours', 'TD', 'TP', 'Examen')),
                date TEXT NOT NULL,
                heure_debut TEXT NOT NULL,
                heure_fin TEXT NOT NULL,
                salle_id INTEGER,
                enseignant_id INTEGER,
                groupe_id INTEGER,
                FOREIGN KEY (salle_id) REFERENCES salles(id) ON DELETE SET NULL,
                FOREIGN KEY (enseignant_id) REFERENCES utilisateurs(id) ON DELETE SET NULL,
                FOREIGN KEY (groupe_id) REFERENCES groupes(id) ON DELETE CASCADE
            )
        ''')
        
        # Table 6 : Réservations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enseignant_id INTEGER NOT NULL,
                salle_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                heure_debut TEXT NOT NULL,
                heure_fin TEXT NOT NULL,
                statut TEXT DEFAULT 'en_attente' CHECK(statut IN ('en_attente', 'validee', 'rejetee')),
                motif TEXT,
                date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (enseignant_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
                FOREIGN KEY (salle_id) REFERENCES salles(id) ON DELETE CASCADE
            )
        ''')
        
        # Table 7 : Disponibilités
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disponibilites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enseignant_id INTEGER NOT NULL,
                date_debut TEXT NOT NULL,
                date_fin TEXT NOT NULL,
                motif TEXT,
                FOREIGN KEY (enseignant_id) REFERENCES utilisateurs(id) ON DELETE CASCADE
            )
        ''')
        
        # Table 8 : Historique des imports
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historique_imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_import TEXT NOT NULL,
                nb_lignes INTEGER NOT NULL,
                date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fichier_nom TEXT,
                admin_id INTEGER,
                FOREIGN KEY (admin_id) REFERENCES utilisateurs(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée avec succès!")
        print(f"📁 Fichier : {self.db_path}")
        print(f"📊 Tables créées : 8 tables")
    
    # ═══════════════════════════════════════════════════════════
    # SÉCURITÉ ET BACKUP
    # ═══════════════════════════════════════════════════════════

    def sauvegarder_bdd(self):
        """Crée une sauvegarde de sécurité de la base de données"""
        if os.path.exists(self.db_path):
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_fstt_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_name)
            
            shutil.copy2(self.db_path, backup_path)
            print(f"🛡️ Sauvegarde créée : {backup_path}")
            return backup_path
        return None
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES CRUD - UTILISATEURS
    # ═══════════════════════════════════════════════════════════
    
    def ajouter_utilisateur(self, nom, prenom, email, mot_de_passe, type_user, 
                           specialite=None, groupe_id=None, duree_max_jour=480):
        """Ajoute un utilisateur (avec durée max pour enseignants)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        mot_de_passe_hash = self.hash_password(mot_de_passe)
        
        try:
            cursor.execute('''
                INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, type_user, 
                                        specialite, groupe_id, duree_max_jour)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nom, prenom, email, mot_de_passe_hash, type_user, specialite, 
                  groupe_id, duree_max_jour))
            
            conn.commit()
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            print(f"❌ Email {email} déjà utilisé")
            return None
        finally:
            conn.close()
    
    def verifier_connexion(self, email, mot_de_passe):
        """Vérifie les identifiants de connexion"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        mot_de_passe_hash = self.hash_password(mot_de_passe)
        
        cursor.execute('''
            SELECT * FROM utilisateurs 
            WHERE email = ? AND mot_de_passe = ?
        ''', (email, mot_de_passe_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        return user
    
    def supprimer_tous_utilisateurs_type(self, type_user):
        """Supprime tous les utilisateurs d'un type (pour import)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM utilisateurs WHERE type_user = ?', (type_user,))
        nb_supprime = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return nb_supprime
    
    def get_tous_utilisateurs(self, type_user=None):
        """Récupère tous les utilisateurs (optionnel : filtré par type)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if type_user:
            cursor.execute('SELECT * FROM utilisateurs WHERE type_user = ?', (type_user,))
        else:
            cursor.execute('SELECT * FROM utilisateurs')
        
        utilisateurs = cursor.fetchall()
        conn.close()
        
        return utilisateurs

    def get_utilisateur_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM utilisateurs WHERE id = ?', (user_id,))
        utilisateur = cursor.fetchone()
        
        conn.close()
        return utilisateur

    def get_utilisateur_by_email(self, email):
        """Récupère un utilisateur par son email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM utilisateurs WHERE email = ?', (email,))
        utilisateur = cursor.fetchone()
        
        conn.close()
        return utilisateur

    def modifier_utilisateur(self, user_id, nom=None, prenom=None, email=None, 
                            mot_de_passe=None, specialite=None, groupe_id=None,
                            duree_max_jour=None):
        """Modifie les informations d'un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Construction dynamique de la requête
        champs = []
        valeurs = []
        
        if nom:
            champs.append("nom = ?")
            valeurs.append(nom)
        if prenom:
            champs.append("prenom = ?")
            valeurs.append(prenom)
        if email:
            champs.append("email = ?")
            valeurs.append(email)
        if mot_de_passe:
            champs.append("mot_de_passe = ?")
            valeurs.append(self.hash_password(mot_de_passe))
        if specialite is not None:
            champs.append("specialite = ?")
            valeurs.append(specialite)
        if groupe_id is not None:
            champs.append("groupe_id = ?")
            valeurs.append(groupe_id)
        if duree_max_jour is not None:
            champs.append("duree_max_jour = ?")
            valeurs.append(duree_max_jour)
        
        if not champs:
            return False
        
        valeurs.append(user_id)
        requete = f"UPDATE utilisateurs SET {', '.join(champs)} WHERE id = ?"
        
        try:
            cursor.execute(requete, valeurs)
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"❌ Erreur lors de la modification : {e}")
            return False
        finally:
            conn.close()

    def supprimer_utilisateur(self, user_id):
        """Supprime un utilisateur par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM utilisateurs WHERE id = ?', (user_id,))
        nb_supprime = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return nb_supprime > 0

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES - CONTRAINTES ENSEIGNANTS
    # ═══════════════════════════════════════════════════════════

    def get_duree_max_enseignant(self, enseignant_id):
        """Récupère la durée max journalière d'un enseignant (en minutes)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT duree_max_jour FROM utilisateurs 
            WHERE id = ? AND type_user = 'enseignant'
        ''', (enseignant_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 480  # 480 min = 8h par défaut

    def modifier_duree_max_enseignant(self, enseignant_id, duree_minutes):
        """Modifie la durée max journalière d'un enseignant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE utilisateurs 
            SET duree_max_jour = ?
            WHERE id = ? AND type_user = 'enseignant'
        ''', (duree_minutes, enseignant_id))
        
        conn.commit()
        nb_modif = cursor.rowcount
        conn.close()
        
        return nb_modif > 0

    def calculer_duree_journee_enseignant(self, enseignant_id, date):
        """Calcule le total d'heures d'un enseignant pour une date donnée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT heure_debut, heure_fin 
            FROM seances 
            WHERE enseignant_id = ? AND date = ?
        ''', (enseignant_id, date))
        
        seances = cursor.fetchall()
        conn.close()
        
        total_minutes = 0
        for seance in seances:
            heure_debut = seance[0]
            heure_fin = seance[1]
            duree = self.calculer_duree_minutes(heure_debut, heure_fin)
            total_minutes += duree
        
        return total_minutes

    def calculer_duree_minutes(self, heure_debut, heure_fin):
        """Calcule la durée en minutes entre deux heures (format HH:MM)"""
        from datetime import datetime
        
        fmt = "%H:%M"
        debut = datetime.strptime(heure_debut, fmt)
        fin = datetime.strptime(heure_fin, fmt)
        
        duree = (fin - debut).total_seconds() / 60
        return int(duree)

    def peut_ajouter_seance_enseignant(self, enseignant_id, date, duree_seance):
        """Vérifie si on peut ajouter une séance sans dépasser la durée max"""
        duree_actuelle = self.calculer_duree_journee_enseignant(enseignant_id, date)
        duree_max = self.get_duree_max_enseignant(enseignant_id)
        
        return (duree_actuelle + duree_seance) <= duree_max
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES CRUD - FILIÈRES
    # ═══════════════════════════════════════════════════════════
    
    def ajouter_filiere(self, nom, niveau):
        """Ajoute une filière"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO filieres (nom, niveau)
            VALUES (?, ?)
        ''', (nom, niveau))
        
        conn.commit()
        filiere_id = cursor.lastrowid
        conn.close()
        
        return filiere_id
    
    def get_toutes_filieres(self):
        """Récupère toutes les filières"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM filieres ORDER BY niveau, nom')
        filieres = cursor.fetchall()
        
        conn.close()
        return filieres
    
    def get_filiere_by_nom(self, nom):
        """Récupère une filière par son nom"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM filieres WHERE nom = ?', (nom,))
        filiere = cursor.fetchone()
        
        conn.close()
        return filiere
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES CRUD - GROUPES
    # ═══════════════════════════════════════════════════════════
    
    def ajouter_groupe(self, nom, effectif, filiere_id):
        """Ajoute un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO groupes (nom, effectif, filiere_id)
            VALUES (?, ?, ?)
        ''', (nom, effectif, filiere_id))
        
        conn.commit()
        groupe_id = cursor.lastrowid
        conn.close()
        
        return groupe_id
    
    def get_tous_groupes(self):
        """Récupère tous les groupes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM groupes')
        groupes = cursor.fetchall()
        
        conn.close()
        return groupes
    
    def get_groupe_by_nom_filiere(self, nom_groupe, filiere_id):
        """Récupère un groupe par nom et filière"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM groupes 
            WHERE nom = ? AND filiere_id = ?
        ''', (nom_groupe, filiere_id))
        
        groupe = cursor.fetchone()
        conn.close()
        
        return groupe
    
    def get_groupe_by_nom(self, nom_groupe):
        """Récupère un groupe par son nom (sans filière)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM groupes WHERE nom = ?', (nom_groupe,))
        groupe = cursor.fetchone()
        
        conn.close()
        return groupe
    
    def supprimer_tous_groupes(self):
        """Supprime tous les groupes (pour import)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM groupes')
        nb_supprime = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return nb_supprime
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES CRUD - SALLES
    # ═══════════════════════════════════════════════════════════
    
    def ajouter_salle(self, nom, capacite, type_salle, equipements=""):
        """Ajoute une salle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO salles (nom, capacite, type_salle, equipements)
                VALUES (?, ?, ?, ?)
            ''', (nom, capacite, type_salle, equipements))
            
            conn.commit()
            salle_id = cursor.lastrowid
            return salle_id
        except sqlite3.IntegrityError:
            print(f"❌ Salle {nom} existe déjà")
            return None
        finally:
            conn.close()
    
    def get_toutes_salles(self):
        """Récupère toutes les salles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM salles ORDER BY nom')
        salles = cursor.fetchall()
        
        conn.close()
        return salles
    
    def supprimer_toutes_salles(self):
        """Supprime toutes les salles (pour import)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM salles')
        nb_supprime = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return nb_supprime
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES CRUD - SÉANCES
    # ═══════════════════════════════════════════════════════════

    def ajouter_seance(self, titre, type_seance, date, heure_debut, heure_fin,
                      salle_id, enseignant_id, groupe_id):
        """Ajoute une séance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO seances (titre, type_seance, date, heure_debut, heure_fin,
                                   salle_id, enseignant_id, groupe_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (titre, type_seance, date, heure_debut, heure_fin,
                  salle_id, enseignant_id, groupe_id))
            
            conn.commit()
            seance_id = cursor.lastrowid
            return seance_id
        except Exception as e:
            print(f"❌ Erreur ajout séance : {e}")
            return None
        finally:
            conn.close()

    def get_seances_by_groupe(self, groupe_id, date_debut=None, date_fin=None):
        """Récupère les séances d'un groupe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if date_debut and date_fin:
            cursor.execute('''
                SELECT * FROM seances 
                WHERE groupe_id = ? AND date BETWEEN ? AND ?
                ORDER BY date, heure_debut
            ''', (groupe_id, date_debut, date_fin))
        else:
            cursor.execute('''
                SELECT * FROM seances 
                WHERE groupe_id = ?
                ORDER BY date, heure_debut
            ''', (groupe_id,))
        
        seances = cursor.fetchall()
        conn.close()
        
        return seances

    def get_seances_by_enseignant(self, enseignant_id, date_debut=None, date_fin=None):
        """Récupère les séances d'un enseignant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if date_debut and date_fin:
            cursor.execute('''
                SELECT * FROM seances 
                WHERE enseignant_id = ? AND date BETWEEN ? AND ?
                ORDER BY date, heure_debut
            ''', (enseignant_id, date_debut, date_fin))
        else:
            cursor.execute('''
                SELECT * FROM seances 
                WHERE enseignant_id = ?
                ORDER BY date, heure_debut
            ''', (enseignant_id,))
        
        seances = cursor.fetchall()
        conn.close()
        
        return seances

    def get_seances_by_salle(self, salle_id, date):
        """Récupère les séances d'une salle pour une date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM seances 
            WHERE salle_id = ? AND date = ?
            ORDER BY heure_debut
        ''', (salle_id, date))
        
        seances = cursor.fetchall()
        conn.close()
        
        return seances

    def verifier_conflit_seance(self, date, heure_debut, heure_fin, 
                               salle_id=None, enseignant_id=None, groupe_id=None):
        """Vérifie s'il y a un conflit pour une séance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        conflits = []
        
        # Conflit salle
        if salle_id:
            cursor.execute('''
                SELECT * FROM seances 
                WHERE salle_id = ? AND date = ? 
                AND ((heure_debut < ? AND heure_fin > ?) OR 
                     (heure_debut < ? AND heure_fin > ?) OR
                     (heure_debut >= ? AND heure_fin <= ?))
            ''', (salle_id, date, heure_fin, heure_debut, 
                  heure_fin, heure_debut, heure_debut, heure_fin))
            
            if cursor.fetchone():
                conflits.append("Salle déjà occupée")
        
        # Conflit enseignant
        if enseignant_id:
            cursor.execute('''
                SELECT * FROM seances 
                WHERE enseignant_id = ? AND date = ? 
                AND ((heure_debut < ? AND heure_fin > ?) OR 
                     (heure_debut < ? AND heure_fin > ?) OR
                     (heure_debut >= ? AND heure_fin <= ?))
            ''', (enseignant_id, date, heure_fin, heure_debut, 
                  heure_fin, heure_debut, heure_debut, heure_fin))
            
            if cursor.fetchone():
                conflits.append("Enseignant déjà occupé")
        
        # Conflit groupe
        if groupe_id:
            cursor.execute('''
                SELECT * FROM seances 
                WHERE groupe_id = ? AND date = ? 
                AND ((heure_debut < ? AND heure_fin > ?) OR 
                     (heure_debut < ? AND heure_fin > ?) OR
                     (heure_debut >= ? AND heure_fin <= ?))
            ''', (groupe_id, date, heure_fin, heure_debut, 
                  heure_fin, heure_debut, heure_debut, heure_fin))
            
            if cursor.fetchone():
                conflits.append("Groupe déjà occupé")
        
        conn.close()
        
        return conflits
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES CRUD - RÉSERVATIONS
    # ═══════════════════════════════════════════════════════════

    def ajouter_reservation(self, enseignant_id, salle_id, date, heure_debut, 
                           heure_fin, motif=""):
        """Crée une demande de réservation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reservations (enseignant_id, salle_id, date, heure_debut,
                                     heure_fin, motif)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (enseignant_id, salle_id, date, heure_debut, heure_fin, motif))
        
        conn.commit()
        reservation_id = cursor.lastrowid
        conn.close()
        
        return reservation_id

    def get_reservations_by_statut(self, statut="en_attente"):
        """Récupère les réservations par statut"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reservations 
            WHERE statut = ?
            ORDER BY date_demande DESC
        ''', (statut,))
        
        reservations = cursor.fetchall()
        conn.close()
        
        return reservations

    def modifier_statut_reservation(self, reservation_id, statut):
        """Modifie le statut d'une réservation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reservations 
            SET statut = ?
            WHERE id = ?
        ''', (statut, reservation_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    # ═══════════════════════════════════════════════════════════
    # HISTORIQUE IMPORTS
    # ═══════════════════════════════════════════════════════════
    
    def ajouter_historique_import(self, type_import, nb_lignes, fichier_nom, admin_id):
        """Enregistre un import dans l'historique"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO historique_imports (type_import, nb_lignes, fichier_nom, admin_id)
            VALUES (?, ?, ?, ?)
        ''', (type_import, nb_lignes, fichier_nom, admin_id))
        
        conn.commit()
        conn.close()
        
        return True