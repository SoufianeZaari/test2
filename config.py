"""
═══════════════════════════════════════════════════════════════
CONFIG.PY - CONFIGURATION DU PROJET FST TANGER
Version complète avec toutes les données réelles de la FST
═══════════════════════════════════════════════════════════════
"""

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# CHEMINS DU PROJET
# ═══════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
EXPORTS_DIR = BASE_DIR / 'exports'
TEMPLATES_CSV_DIR = BASE_DIR / 'templates_csv'
SRC_DIR = BASE_DIR / 'src'
GUI_DIR = SRC_DIR / 'gui'

# Créer les dossiers s'ils n'existent pas
for directory in [DATA_DIR, EXPORTS_DIR, TEMPLATES_CSV_DIR, GUI_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════

DATABASE_PATH = DATA_DIR / 'emploi_du_temps.db'
SCHEMA_SQL_PATH = BASE_DIR / 'schema.sql'

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION APPLICATION
# ═══════════════════════════════════════════════════════════════

APP_CONFIG = {
    'etablissement': 'Faculté des Sciences et Techniques - Tanger',
    'ville': 'Tanger',
    'adresse': 'Route de l\'Aéroport BP 416',
    'annee_universitaire': '2025/2026',
    'semestres': ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'],
    'version': '1.0.0',
    'auteurs': 'Équipe Python FST'
}

# Constants for export service compatibility
EXPORT_FOLDER = str(EXPORTS_DIR)
ETABLISSEMENT = APP_CONFIG['etablissement']
ANNEE_UNIVERSITAIRE = APP_CONFIG['annee_universitaire']

# ═══════════════════════════════════════════════════════════════
# CYCLES D'ÉTUDES FST TANGER (LMD)
# ═══════════════════════════════════════════════════════════════

CYCLES = [
    {
        'code': 'DEUST',
        'nom': 'Diplôme d\'Études Universitaires en Sciences et Techniques',
        'niveau': 'Bac+2',
        'duree': 2
    },
    {
        'code': 'LST',
        'nom': 'Licence Sciences et Techniques',
        'niveau': 'Bac+3',
        'duree': 3
    },
    {
        'code': 'MST',
        'nom': 'Master Sciences et Techniques',
        'niveau': 'Bac+5',
        'duree': 2
    },
    {
        'code': 'ING',
        'nom': 'Diplôme d\'Ingénieur d\'État',
        'niveau': 'Bac+5',
        'duree': 3
    },
    {
        'code': 'DOCT',
        'nom': 'Doctorat en Sciences et Techniques',
        'niveau': 'Bac+8',
        'duree': 3
    }
]

# ═══════════════════════════════════════════════════════════════
# TRONCS COMMUNS LST (S1 et S2)
# ═══════════════════════════════════════════════════════════════

TRONCS_COMMUNS_LST = [
    # Nouveaux troncs communs (Accréditation 2024)
    ('TC-GB', 'Génie Biologique', 2024),
    ('TC-GEG', 'Génie de l\'Environnement et Géosciences', 2024),
    ('TC-GP', 'Génie Physique', 2024),
    ('TC-GC', 'Génie Chimique', 2024),
    ('TC-GI', 'Génie Informatique', 2024),
    ('TC-MSD', 'Mathématiques et Sciences des Données', 2024),
    ('TC-GMSI', 'Génie Mécanique et Systèmes Industriels', 2024),
    ('TC-GESE', 'Génie Électrique et Systèmes Embarqués', 2024),
    
    # Anciens troncs communs (Accréditation 2014-2024)
    ('TC-BCG', 'Biologie-Chimie-Géologie', 2014),
    ('TC-GEGM', 'Génie Électrique – Génie Mécanique', 2014),
    ('TC-MIP', 'Mathématiques-Informatique-Physique', 2014),
    ('TC-MIPC', 'Mathématiques-Informatique-Physique-Chimie', 2014)
]

# ═══════════════════════════════════════════════════════════════
# FILIÈRES LST (S3, S4, S5, S6)
# ═══════════════════════════════════════════════════════════════

FILIERES_LST = [
    ('AD', 'Analytique des Données'),
    ('BIOT', 'Biotechnologies', 'Options: animale et végétale'),
    ('DIP', 'Design Industriel et Productique'),
    ('ENR', 'Énergies Renouvelables'),
    ('GC', 'Génie Civil'),
    ('GP', 'Génie des Procédés'),
    ('GESI', 'Génie Électrique & Système Industriel'),
    ('GI', 'Génie Industriel'),
    ('GI-INFO', 'Génie Informatique'),
    ('GA', 'Géosciences Appliquées'),
    ('IDAI', 'Ingénierie de Développement d\'Applications Informatiques'),
    ('IS', 'Ingénierie Statistique'),
    ('MA', 'Mathématiques et Applications'),
    ('LMID', 'Mathématiques et Informatique Décisionnelles'),
    ('RRN', 'Risques et Ressources Naturels'),
    ('LSSD', 'Statistique et Science des Données'),
    ('TAC', 'Techniques d\'Analyses Chimiques')
]

# ═══════════════════════════════════════════════════════════════
# FILIÈRES MST (M1 et M2)
# ═══════════════════════════════════════════════════════════════

FILIERES_MST = [
    ('AAIS', 'Analyse Appliquée et Ingénierie Statistique'),
    ('BCMB', 'Bases Cellulaires et Moléculaires en Biotechnologie'),
    ('EADD', 'Environnement, Aquaculture et Développement Durable'),
    ('GER', 'Géoressources Energétiques et Réservoirs'),
    ('GC-M', 'Génie Civil'),
    ('GMPM', 'Génie des Matériaux pour Plasturgie et Métallurgie'),
    ('GE', 'Génie Energétique'),
    ('IECDD', 'Ingénierie Environnementale, Changement Climatique et DD'),
    ('IASD', 'Intelligence Artificielle et Sciences de Données'),
    ('MBD', 'Mobiquité et Big Data'),
    ('MMSD', 'Modélisation Mathématique et Science de Données'),
    ('SA', 'Sciences Agroalimentaires'),
    ('SE', 'Sciences de l\'Environnement'),
    ('SLAP', 'Sciences du Littoral: Approche Pluridisciplinaire'),
    ('SITBD', 'Sécurité IT et Big Data'),
    ('SIM', 'Systèmes Informatiques et Mobiles')
]

# ═══════════════════════════════════════════════════════════════
# CYCLE INGÉNIEUR (Accréditation 2024)
# ═══════════════════════════════════════════════════════════════

FILIERES_INGENIEUR = [
    ('GA-ING', 'Génie Agroalimentaire', 'Validée'),
    ('GEMI', 'Génie Électrique et Management Industriel', 'Validée'),
    ('GI-ING', 'Génie Industriel', 'Validée'),
    ('GEOINF', 'Géoinformation', 'Validée'),
    ('IAGE', 'Ingénierie Aquacole et Gestion des Exploitations', 'En cours'),
    ('IME', 'Ingénierie et Management de l\'Eau', 'En cours'),
    ('LSI', 'Logiciels et Systèmes Intelligents', 'Validée')
]

# ═══════════════════════════════════════════════════════════════
# SALLES FST TANGER (STRUCTURE RÉELLE)
# ═══════════════════════════════════════════════════════════════

# Bâtiment B - Salles B01 à B17
SALLES_BATIMENT_B = [(f"B{str(i).zfill(2)}", 35, "Salle") for i in range(1, 18)]

# Bâtiment C - Salles C01 à C17
SALLES_BATIMENT_C = [(f"C{str(i).zfill(2)}", 35, "Salle") for i in range(1, 18)]

# Bâtiment E - Salles E11 à E18
SALLES_BATIMENT_E = [
    ("E11", 40, "Salle"),
    ("E12", 35, "Salle"),
    ("E13", 35, "Salle"),
    ("E14", 40, "Salle"),
    ("E15", 45, "Salle"),
    ("E16", 35, "Salle"),
    ("E17", 40, "Salle"),
    ("E18", 40, "Salle")
]

# Bâtiment F - Salles F01 à F14
SALLES_BATIMENT_F = [
    ("F01", 45, "Salle"),
    ("F02", 35, "Salle"),
    ("F03", 35, "Salle"),
    ("F04", 40, "Salle"),
    ("F05", 35, "Salle"),
    ("F06", 35, "Salle"),
    ("F07", 40, "Salle"),
    ("F08", 35, "Salle"),
    ("F09", 35, "Salle"),
    ("F10", 40, "Salle"),
    ("F11", 35, "Salle"),
    ("F12", 38, "Salle"),
    ("F13", 40, "Salle"),
    ("F14", 40, "Salle")
]

# Amphithéâtres (6 au total)
AMPHITHEATRES = [
    ("Amphi 1", 200, "Amphithéâtre"),
    ("Amphi 2", 180, "Amphithéâtre"),
    ("Amphi 3", 180, "Amphithéâtre"),
    ("Amphi 4", 200, "Amphithéâtre"),
    ("Amphi 5", 220, "Amphithéâtre"),
    ("Amphi 6", 150, "Amphithéâtre")
]

# Laboratoires par département
LABORATOIRES = [
    # Département Informatique
    ("Labo Info 1", 30, "Laboratoire", "Département Informatique"),
    ("Labo Info 2", 30, "Laboratoire", "Département Informatique"),
    ("Labo Info 3", 25, "Laboratoire", "Département Informatique"),
    
    # Département Mathématiques
    ("Labo Math 1", 25, "Laboratoire", "Département Mathématiques"),
    ("Labo Math 2", 25, "Laboratoire", "Département Mathématiques"),
    
    # Département Chimie
    ("Labo Chimie 1", 20, "Laboratoire", "Département Chimie"),
    ("Labo Chimie 2", 20, "Laboratoire", "Département Chimie"),
    ("Labo Chimie 3", 20, "Laboratoire", "Département Chimie"),
    
    # Département Physique
    ("Labo Physique 1", 20, "Laboratoire", "Département Physique"),
    ("Labo Physique 2", 20, "Laboratoire", "Département Physique"),
    
    # Département Biologie
    ("Labo Bio 1", 20, "Laboratoire", "Département Biologie"),
    ("Labo Bio 2", 20, "Laboratoire", "Département Biologie"),
    ("Labo Bio 3", 20, "Laboratoire", "Département Biologie"),
    
    # Génie Mécanique
    ("Labo GM 1", 25, "Laboratoire", "Département Génie Mécanique"),
    ("Salle Info Dept. GM", 30, "Laboratoire", "Département Génie Mécanique")
]

# Consolidation de toutes les salles
SALLES_FSTT = (
    SALLES_BATIMENT_B + 
    SALLES_BATIMENT_C + 
    SALLES_BATIMENT_E + 
    SALLES_BATIMENT_F + 
    AMPHITHEATRES + 
    LABORATOIRES
)

# ═══════════════════════════════════════════════════════════════
# CRÉNEAUX HORAIRES
# ═══════════════════════════════════════════════════════════════

JOURS_SEMAINE = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']

CRENEAUX_HORAIRES = [
    ('09:00', '10:30', 90),
    ('10:45', '12:15', 90),
    ('12:30', '14:00', 90),
    ('14:15', '15:45', 90),
    ('16:00', '17:30', 90)
]

# ═══════════════════════════════════════════════════════════════
# TYPES ET CONTRAINTES
# ═══════════════════════════════════════════════════════════════

TYPES_SEANCES = ['Cours', 'TD', 'TP', 'Examen', 'Rattrapage', 'Soutenance']
TYPES_SALLES = ['Salle', 'Amphithéâtre', 'Laboratoire']
TYPES_UTILISATEURS = ['Administrateur', 'Enseignant', 'Etudiant']

STATUTS_SEANCE = ['Planifiée', 'En cours', 'Terminée', 'Annulée']
STATUTS_RESERVATION = ['En attente', 'Validée', 'Rejetée']

# Contraintes métier
CONTRAINTES = {
    'capacite_min_salle': 20,
    'capacite_max_salle': 250,
    'capacite_min_amphi': 100,
    'duree_min_seance': 90,  # minutes
    'duree_max_seance': 180,
    'duree_max_jour_enseignant': 480,  # 8h par défaut
    'duree_max_semaine_enseignant': 2400,  # 40h par défaut
    'nb_max_seances_jour_groupe': 5,
    'pause_dejeuner_debut': '12:15',
    'pause_dejeuner_fin': '14:00'
}

# ═══════════════════════════════════════════════════════════════
# TEMPLATES CSV (4 fichiers seulement)
# ═══════════════════════════════════════════════════════════════

CSV_TEMPLATES = {
    'enseignants': TEMPLATES_CSV_DIR / 'enseignants.csv',
    'etudiants': TEMPLATES_CSV_DIR / 'etudiants.csv',
    'groupes': TEMPLATES_CSV_DIR / 'groupes.csv',
    'salles': TEMPLATES_CSV_DIR / 'salles.csv'
}

# Colonnes requises pour validation des CSV
COLONNES_ENSEIGNANTS = ['nom', 'prenom', 'email', 'specialite', 'duree_max_jour']
COLONNES_ETUDIANTS = ['nom', 'prenom', 'email', 'groupe']
COLONNES_SALLES = ['nom', 'capacite', 'type_salle', 'equipements']
COLONNES_GROUPES = ['nom', 'effectif', 'filiere']

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION EXPORT (PDF, EXCEL, IMAGE)
# ═══════════════════════════════════════════════════════════════

EXPORT_CONFIG = {
    'formats_disponibles': ['PDF', 'Excel', 'Image', 'CSV'],
    
    # Répertoires d'export
    'pdf_dir': EXPORTS_DIR / 'pdf',
    'excel_dir': EXPORTS_DIR / 'excel',
    'images_dir': EXPORTS_DIR / 'images',
    'csv_dir': EXPORTS_DIR / 'csv',
    
    # Configuration PDF
    'pdf_format': 'A4',
    'pdf_orientation': 'landscape',  # ou 'portrait'
    'pdf_police': 'Helvetica',
    'pdf_taille_police': 10,
    
    # Configuration Excel
    'excel_format': '.xlsx',
    'excel_feuille_par': 'filiere',  # ou 'groupe', 'enseignant'
    
    # Configuration Image
    'image_format': 'PNG',  # ou 'JPEG'
    'image_dpi': 300,
    'image_largeur': 1920,
    'image_hauteur': 1080
}

# Créer les sous-dossiers d'export
for export_dir in [EXPORT_CONFIG['pdf_dir'], EXPORT_CONFIG['excel_dir'], 
                   EXPORT_CONFIG['images_dir'], EXPORT_CONFIG['csv_dir']]:
    export_dir.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION INTERFACE GRAPHIQUE
# ═══════════════════════════════════════════════════════════════

GUI_CONFIG = {
    'window_title': 'FST Tanger - Gestion Emplois du Temps',
    'window_width': 1400,
    'window_height': 900,
    'theme': 'modern',
    'language': 'fr',
    'logo_path': BASE_DIR / 'assets' / 'logo_fst.png',
    
    # Couleurs
    'color_primary': '#1e3a8a',  # Bleu FST
    'color_secondary': '#3b82f6',
    'color_success': '#10b981',
    'color_warning': '#f59e0b',
    'color_danger': '#ef4444',
    'color_background': '#f3f4f6'
}

# ═══════════════════════════════════════════════════════════════
# MESSAGES SYSTÈME
# ═══════════════════════════════════════════════════════════════

MESSAGES = {
    'success': {
        'import': '✅ Import réussi !',
        'export': '✅ Export réussi !',
        'creation': '✅ Création réussie !',
        'modification': '✅ Modification réussie !',
        'suppression': '✅ Suppression réussie !',
        'generation': '✅ Emploi du temps généré avec succès !'
    },
    'error': {
        'import': '❌ Erreur lors de l\'import',
        'export': '❌ Erreur lors de l\'export',
        'database': '❌ Erreur de base de données',
        'validation': '❌ Données invalides',
        'conflit': '⚠️ Conflit détecté',
        'generation': '❌ Échec de la génération'
    },
    'warning': {
        'capacite': '⚠️ Capacité de la salle dépassée',
        'chevauchement': '⚠️ Chevauchement horaire détecté',
        'disponibilite': '⚠️ Enseignant non disponible',
        'duree_max': '⚠️ Durée maximale dépassée'
    },
    'info': {
        'chargement': 'ℹ️ Chargement en cours...',
        'sauvegarde': 'ℹ️ Sauvegarde en cours...',
        'verification': 'ℹ️ Vérification des contraintes...'
    }
}

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION GÉNÉRATION AUTOMATIQUE
# ═══════════════════════════════════════════════════════════════

GENERATION_CONFIG = {
    'algorithme': 'backtracking',  # ou 'genetic', 'constraint'
    'max_iterations': 10000,
    'timeout_secondes': 300,  # 5 minutes
    
    # Priorités (1 = max, 5 = min)
    'priorite_amphitheatre_cours': 1,
    'priorite_laboratoire_tp': 1,
    'priorite_equilibre_journees': 2,
    'priorite_preferences_enseignant': 3,
    
    # Contraintes strictes
    'respecter_capacite_salle': True,
    'respecter_duree_max_enseignant': True,
    'eviter_samedi': False,
    'pause_dejeuner_obligatoire': True
}

# ═══════════════════════════════════════════════════════════════
# DÉPARTEMENTS FST
# ═══════════════════════════════════════════════════════════════

DEPARTEMENTS = [
    'Mathématiques',
    'Informatique',
    'Physique',
    'Chimie',
    'Biologie',
    'Géologie',
    'Génie Mécanique',
    'Génie Électrique',
    'Génie Industriel',
    'Génie Civil'
]

# ═══════════════════════════════════════════════════════════════
# AFFICHAGE CONFIGURATION (Pour debug)
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 70)
    print(" CONFIGURATION DU PROJET FST TANGER")
    print("═" * 70)
    print(f"📁 Répertoire de base : {BASE_DIR}")
    print(f"💾 Base de données : {DATABASE_PATH}")
    print(f"📊 Templates CSV : {TEMPLATES_CSV_DIR}")
    print(f"📤 Exports : {EXPORTS_DIR}")
    print(f"🏫 Établissement : {APP_CONFIG['etablissement']}")
    print(f"📅 Année : {APP_CONFIG['annee_universitaire']}")
    print(f"\n📚 Cycles disponibles : {len(CYCLES)}")
    print(f"📖 Filières LST : {len(FILIERES_LST)}")
    print(f"🎓 Filières MST : {len(FILIERES_MST)}")
    print(f"👷 Filières Ingénieur : {len(FILIERES_INGENIEUR)}")
    print(f"🏢 Salles totales : {len(SALLES_FSTT)}")
    print(f"   - Bâtiment B : {len(SALLES_BATIMENT_B)}")
    print(f"   - Bâtiment C : {len(SALLES_BATIMENT_C)}")
    print(f"   - Bâtiment E : {len(SALLES_BATIMENT_E)}")
    print(f"   - Bâtiment F : {len(SALLES_BATIMENT_F)}")
    print(f"   - Amphithéâtres : {len(AMPHITHEATRES)}")
    print(f"   - Laboratoires : {len(LABORATOIRES)}")
    print(f"📤 Formats d'export : {', '.join(EXPORT_CONFIG['formats_disponibles'])}")
    print("═" * 70)

MATIERES_COMPLETES = {
    # ═══════════════════════════════════════════════════════════════
    # NIVEAU DEUST - TOUS LES TRONCS COMMUNS
    # ═══════════════════════════════════════════════════════════════
    
    # TC-GI : Génie Informatique
    'DEUST_TC-GI_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('ALGO1', 'Algorithmique et programmation 1', 'Mixte', 20, 10, 15),
        ('ELEC2', 'Électricité 2', 'Mixte', 20, 10, 10),
        ('THERMO', 'Thermodynamique', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('MTU', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-GI_S3': [
        ('STAT', 'Statistiques et Probabilités', 'Cours', 25, 20, 0),
        ('ALGO2', 'Algorithmique & Programmation 2', 'Mixte', 20, 10, 15),
        ('ANAL3', 'Analyse 3', 'Cours', 30, 15, 0),
        ('MICRO', 'Micro-contrôleur et Capteurs', 'Mixte', 20, 10, 10),
        ('ARCH', 'Architecture des Ordinateurs', 'Mixte', 25, 10, 10),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # TC-MSD : Mathématiques et Sciences des Données
    'DEUST_TC-MSD_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('ALGO1', 'Algorithmique et programmation 1', 'Mixte', 20, 10, 15),
        ('ELEC2', 'Électricité 2', 'Mixte', 20, 10, 10),
        ('THERMO', 'Thermodynamique', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('MTU', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-MSD_S3': [
        ('STAT', 'Statistiques et Probabilités', 'Cours', 25, 20, 0),
        ('ALGO2', 'Algorithmique & Programmation 2', 'Mixte', 20, 10, 15),
        ('ANAL3', 'Analyse 3', 'Cours', 30, 15, 0),
        ('ENQ', 'Enquêtes et Techniques de Sondage', 'Mixte', 15, 15, 10),
        ('ALG3', 'Algèbre 3', 'Cours', 30, 15, 0),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # TC-GP : Génie Physique
    'DEUST_TC-GP_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('ALGO1', 'Algorithmique et programmation 1', 'Mixte', 20, 10, 15),
        ('CIR-ELEC', 'Circuits électriques et électronique', 'Mixte', 20, 10, 10),
        ('ELEC', 'Électricité', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('MTU', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-GP_S3': [
        ('STAT', 'Statistiques et Probabilités', 'Cours', 25, 20, 0),
        ('ALGO2', 'Algorithmique & Programmation 2', 'Mixte', 20, 10, 15),
        ('ANAL3', 'Analyse 3', 'Cours', 30, 15, 0),
        ('ELMAG', 'Électromagnétisme', 'Cours', 25, 15, 0),
        ('MEC-SOL', 'Mécanique des Solides', 'Mixte', 25, 15, 10),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # TC-GC : Génie Chimique
    'DEUST_TC-GC_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('ALGO1', 'Algorithmique et programmation 1', 'Mixte', 20, 10, 15),
        ('CIR-ELEC', 'Circuits électriques et électronique', 'Mixte', 20, 10, 10),
        ('ELEC', 'Électricité', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('MTU', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-GC_S3': [
        ('STAT', 'Statistiques et Probabilités', 'Cours', 25, 20, 0),
        ('CHIM-ORG1', 'Chimie Organique 1', 'Mixte', 25, 10, 15),
        ('BIOCHIM', 'Biochimie structurale et Métabolique', 'Mixte', 20, 15, 10),
        ('REACT', 'Réactivité Chimique', 'Cours', 25, 15, 0),
        ('CHIM-MIN1', 'Chimie Minérale 1', 'Mixte', 20, 10, 15),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # TC-GEG : Génie de l'Environnement et Géosciences
    'DEUST_TC-GEG_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('BIO-CELL', 'Biologie cellulaire', 'Mixte', 20, 10, 15),
        ('OPT-RAD', 'Optique et Radioactivité', 'Mixte', 20, 10, 10),
        ('COSMO', 'Cosmologie & Géodynamique interne', 'Cours', 25, 15, 0),
        ('STRUCT-MAT', 'Structure de la matière', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-GEG_S3': [
        ('STAT-DATA', 'Statistiques et Analyse des Données', 'Mixte', 20, 15, 10),
        ('STRAT', 'Stratigraphie / Paléo-Environnement', 'Mixte', 20, 10, 15),
        ('PETRO', 'Pétrographie / Minéralogie', 'Mixte', 20, 10, 15),
        ('GEOM', 'Géomatique', 'Mixte', 15, 10, 20),
        ('CHIM-MIN', 'Chimie Minérale', 'Mixte', 20, 10, 15),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # TC-GB : Génie Biologique
    'DEUST_TC-GB_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('BIO-CELL', 'Biologie cellulaire', 'Mixte', 20, 10, 15),
        ('OPT-RAD', 'Optique et Radioactivité', 'Mixte', 20, 10, 10),
        ('COSMO', 'Cosmologie & Géodynamique interne', 'Cours', 25, 15, 0),
        ('STRUCT-MAT', 'Structure de la matière', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-GB_S3': [
        ('STAT', 'Statistiques et Probabilités', 'Cours', 25, 20, 0),
        ('BIOCHIM-S', 'Biochimie Structurale', 'Mixte', 20, 10, 15),
        ('HISTO', 'Histologie/Embryologie', 'Mixte', 20, 10, 15),
        ('MICRO', 'Microbiologie', 'Mixte', 20, 10, 15),
        ('CHIM-ORG', 'Chimie Organique', 'Mixte', 20, 10, 15),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # TC-GESE : Génie Électrique et Systèmes Embarqués
    'DEUST_TC-GESE_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('ALGO1', 'Algorithmique et programmation 1', 'Mixte', 20, 10, 15),
        ('CIR-ELEC', 'Circuits électriques et électronique', 'Mixte', 20, 10, 10),
        ('ELEC', 'Électricité', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-GESE_S3': [
        ('STAT', 'Statistiques et Probabilités', 'Cours', 25, 20, 0),
        ('ALGO2', 'Algorithmique & Programmation 2', 'Mixte', 20, 10, 15),
        ('ELEC-ANA', 'Électronique Analogique', 'Mixte', 20, 15, 10),
        ('ELMAG', 'Électromagnétisme', 'Cours', 25, 15, 0),
        ('METRO', 'Métrologie et instrumentation', 'Mixte', 15, 10, 20),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # TC-GMSI : Génie Mécanique et Systèmes Industriels
    'DEUST_TC-GMSI_S1': [
        ('ANAL1', 'Analyse 1', 'Cours', 30, 15, 0),
        ('ALG1', 'Algèbre 1', 'Cours', 30, 15, 0),
        ('ALGO1', 'Algorithmique et programmation 1', 'Mixte', 20, 10, 15),
        ('CIR-ELEC', 'Circuits électriques et électronique', 'Mixte', 20, 10, 10),
        ('ELEC', 'Électricité', 'Cours', 25, 15, 0),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    'DEUST_TC-GMSI_S3': [
        ('STAT', 'Statistiques et Probabilités', 'Cours', 25, 20, 0),
        ('ALGO2', 'Algorithmique & Programmation 2', 'Mixte', 20, 10, 15),
        ('ANAL3', 'Analyse 3', 'Cours', 30, 15, 0),
        ('ELMAG', 'Électromagnétisme', 'Cours', 25, 15, 0),
        ('MEC-SOL', 'Mécanique des Solides', 'Mixte', 25, 15, 10),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 20, 0),
    ],
    
    # Anciens TC
    'DEUST_TC-MIP_S3': [
        ('ELMAG', 'Électromagnétisme', 'Cours', 25, 15, 0),
        ('ANAL3', 'Analyse 3', 'Cours', 30, 15, 0),
        ('STAT-D', 'Statistique descriptive/probabilités', 'Cours', 25, 20, 0),
        ('ALGO2', 'Algorithmique et Programmation 2', 'Mixte', 20, 10, 15),
        ('REACT-C', 'Réactivité chimique', 'Cours', 25, 15, 0),
        ('LANG3', 'Langues et communication 3', 'TD', 0, 30, 0),
    ],
    'DEUST_TC-MIPC_S3': [
        ('ELMAG', 'Électromagnétisme', 'Cours', 25, 15, 0),
        ('ANAL3', 'Analyse 3', 'Cours', 30, 15, 0),
        ('STAT-D', 'Statistique descriptive/probabilités', 'Cours', 25, 20, 0),
        ('ALGO2', 'Algorithmique et Programmation 2', 'Mixte', 20, 10, 15),
        ('REACT-C', 'Réactivité chimique', 'Cours', 25, 15, 0),
        ('LANG3', 'Langues et communication 3', 'TD', 0, 30, 0),
    ],
    'DEUST_TC-BCG_S3': [
        ('BIO-VEG', 'Biologie végétale', 'Mixte', 20, 10, 15),
        ('ELEC', 'Électricité', 'Cours', 25, 15, 0),
        ('STRAT-P', 'Stratigraphie & Paléo-environnement', 'Mixte', 20, 10, 15),
        ('CHIM-ORG1', 'Chimie Organique 1', 'Mixte', 20, 10, 15),
        ('CHIM-MIN1', 'Chimie Minérale 1', 'Mixte', 20, 10, 15),
        ('PROB-STAT', 'Probabilités/Statistiques', 'Cours', 25, 20, 0),
        ('MICRO', 'Microbiologie', 'Mixte', 15, 10, 20),
        ('BIOCHIM-S', 'Biochimie structurale', 'Mixte', 20, 10, 15),
    ],
    
    # ═══════════════════════════════════════════════════════════════
    # NIVEAU LST - TOUTES LES FILIÈRES S5
    # ═══════════════════════════════════════════════════════════════
    
    'LST_AD_S5': [
        ('MATH-DS', 'Mathématiques pour la science des données', 'Cours', 30, 15, 0),
        ('STRUCT-ADV', 'Structures des données avancées', 'Mixte', 20, 15, 10),
        ('FOND-BD', 'Fondamentaux des BD', 'Mixte', 20, 10, 15),
        ('ALGO-ADV', 'Algorithmique Avancée', 'Mixte', 25, 15, 10),
        ('DEV-WEB', 'Développement WEB', 'Mixte', 15, 10, 20),
        ('SOFT', 'Soft Skills', 'TD', 0, 25, 0),
    ],
    'LST_IDAI_S5': [
        ('MOD-ADV', 'Modélisation avancée', 'Mixte', 20, 15, 10),
        ('DEV-WEB', 'Développement Web', 'Mixte', 15, 10, 20),
        ('BD-NS', 'BD Structurées et Non structurées', 'Mixte', 20, 10, 15),
        ('POO', 'POO (C++/Java)', 'Mixte', 20, 15, 15),
        ('SYS-RES', 'Systèmes et réseaux', 'Mixte', 20, 10, 15),
        ('SOFT', 'Soft Skills', 'TD', 0, 25, 0),
    ],
    'LST_LSSD_S5': [
        ('PYTHON', 'Programmation Python/POO', 'Mixte', 20, 10, 15),
        ('INT-PROB', 'Intégration et Probabilité', 'Cours', 30, 15, 0),
        ('ANG-M', 'Anglais/Management de Projet', 'TD', 0, 30, 0),
        ('STAT-M', 'Statistique Mathématique', 'Cours', 25, 20, 0),
        ('OPT', 'Optimisation et RO', 'Mixte', 25, 15, 5),
        ('BD-NO', 'BD Relationnelles/NoSQL', 'Mixte', 20, 10, 15),
    ],
    'LST_LMID_S5': [
        ('BD-NO', 'BD Relationnelles/NoSQL', 'Mixte', 20, 10, 15),
        ('ANG-M', 'Anglais/Management', 'TD', 0, 30, 0),
        ('PYTHON', 'Python et POO', 'Mixte', 20, 10, 15),
        ('INT-PROB', 'Intégration et Probabilités', 'Cours', 30, 15, 0),
        ('TOPO', 'Topologie et Calcul Différentiel', 'Cours', 30, 15, 0),
        ('RO', 'Recherche opérationnelle', 'Mixte', 25, 15, 10),
    ],
    'LST_GC_S5': [
        ('MMC', 'Mécanique des milieux continus', 'Cours', 25, 20, 0),
        ('MDS', 'Mécanique des sols', 'Mixte', 20, 15, 10),
        ('DYN', 'Dynamique des structures', 'Mixte', 20, 15, 10),
        ('RDM', 'Résistance des matériaux', 'Mixte', 25, 15, 10),
        ('BA', 'Béton armé', 'Mixte', 20, 15, 10),
        ('MAT', 'Matériaux de construction', 'Mixte', 20, 10, 15),
    ],
    'LST_ENR_S5': [
        ('MDF', 'Mécanique des Fluides', 'Mixte', 25, 15, 10),
        ('ELEC', 'Électrotechnique', 'Mixte', 20, 15, 10),
        ('CONV', 'Convertisseurs statiques', 'Mixte', 20, 10, 15),
        ('PROD', 'Production des ENR', 'Mixte', 20, 10, 15),
        ('GM', 'Génie des Matériaux', 'Cours', 25, 15, 0),
        ('CALC', 'Calcul Scientifique', 'Mixte', 15, 15, 15),
    ],
    'LST_GESI_S5': [
        ('TRAIT-SIG', 'Traitement du signal', 'Mixte', 20, 15, 10),
        ('ACT-IND', 'Actionneurs industriels', 'Mixte', 20, 10, 15),
        ('ELEC-PUIS', 'Électronique de puissance', 'Mixte', 20, 15, 10),
        ('AUTO', 'Automatisme', 'Mixte', 25, 15, 10),
        ('ELEC-SYS', 'Électronique et systèmes', 'Mixte', 20, 10, 15),
        ('MAINT', 'Maintenance', 'Cours', 20, 20, 0),
    ],
    'LST_GI_S5': [
        ('MACH-HYD', 'Machines Hydrauliques', 'Mixte', 20, 15, 10),
        ('GEST-PROD', 'Gestion de production', 'Cours', 25, 20, 0),
        ('MACH-THERM', 'Machines Thermiques', 'Mixte', 20, 15, 10),
        ('GEST-QUAL', 'Gestion de la qualité', 'Cours', 20, 20, 0),
        ('MAINT', 'Maintenance', 'Cours', 20, 20, 0),
        ('MAT-RDM', 'Matériaux et RDM', 'Mixte', 25, 15, 10),
    ],
    'LST_DIP_S5': [
        ('CHOIX-MAT', 'Choix des matériaux', 'Cours', 25, 15, 0),
        ('ELEM-MACH', 'Éléments de machines', 'Mixte', 20, 15, 10),
        ('MACH-IND', 'Machines industrielles', 'Mixte', 20, 15, 10),
        ('MGT-IND', 'Management Industriel', 'Cours', 20, 20, 0),
        ('CAO', 'CAO', 'Mixte', 10, 10, 25),
        ('METRO', 'Métrologie', 'Mixte', 15, 10, 20),
    ],
    'LST_BIOT_S5': [
        ('BM', 'Biologie moléculaire', 'Mixte', 25, 10, 15),
        ('GEN', 'Génétique', 'Mixte', 25, 15, 10),
        ('ENZ', 'Enzymologie', 'Mixte', 20, 10, 15),
        ('IMM', 'Immunologie', 'Mixte', 20, 15, 10),
        ('GMI', 'Génie Microbiologique', 'Mixte', 20, 10, 15),
        ('TECH', 'Techniques appliquées à la Biologie', 'TP', 0, 0, 45),
    ],
    'LST_GP_S5': [
        ('CALC-REACT', 'Calculs des réacteurs', 'Mixte', 25, 15, 10),
        ('BILAN', 'Bilan Matière et Énergie', 'Mixte', 25, 15, 10),
        ('OP-UNIT', 'Opérations Unitaires', 'Mixte', 20, 15, 10),
        ('MDF', 'Mécanique des fluides', 'Mixte', 25, 15, 10),
        ('OPT-PROC', 'Optimisation des Procédés', 'Mixte', 20, 15, 10),
        ('MODEL', 'Modélisation', 'Mixte', 20, 15, 10),
    ],
    'LST_TAC_S5': [
        ('CHIM-ORG', 'Chimie organique/inorganique', 'Mixte', 25, 10, 15),
        ('THERMO-C', 'Thermochimie', 'Cours', 25, 20, 0),
        ('ELECTRO-C', 'Électrochimie', 'Mixte', 20, 15, 10),
        ('SPECTRO', 'Méthodes Spectroscopiques', 'Mixte', 20, 10, 15),
        ('TECH-ANAL', 'Techniques d\'analyse', 'Mixte', 15, 10, 20),
    ],
    'LST_RRN_S5': [
        ('RISQ-RES', 'Risques et ressources naturels', 'Cours', 25, 20, 0),
        ('TECH-GEO', 'Techniques géophysiques/géomatiques', 'Mixte', 20, 10, 15),
        ('INFO', 'Informatiques', 'Mixte', 15, 10, 20),
        ('MODEL-DATA', 'Modélisation de données', 'Mixte', 20, 15, 10),
        ('SOFT', 'Soft Skills', 'TD', 0, 25, 0),
    ],
    
    # ═══════════════════════════════════════════════════════════════
    # NIVEAU MASTER - TOUTES LES FILIÈRES
    # ═══════════════════════════════════════════════════════════════
    
    'MST_IASD_S1': [
        ('MATH-D', 'Maths pour analyse de données', 'Cours', 30, 15, 0),
        ('PROG', 'Programmation Avancée', 'Mixte', 20, 10, 15),
        ('BDA', 'BD Avancées', 'Mixte', 20, 10, 15),
        ('ML1', 'Machine Learning 1', 'Mixte', 25, 15, 10),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('RAIS', 'Raisonnement Intelligent', 'Mixte', 20, 15, 10),
    ],
    'MST_IASD_S3': [
        ('DL', 'Deep Learning', 'Mixte', 25, 15, 15),
        ('MM', 'Multimedia Mining', 'Mixte', 20, 10, 15),
        ('DI', 'Data Integration', 'Mixte', 20, 10, 15),
        ('BC', 'Blockchain', 'Mixte', 15, 15, 15),
        ('DS', 'Digital Strategies', 'TD', 0, 30, 0),
        ('CLOUD', 'Cloud/Edge Computing', 'Mixte', 20, 10, 15),
    ],
    'MST_SITBD_S1': [
        ('POO-ADV', 'POO Avancée (Java/Python)', 'Mixte', 20, 15, 15),
        ('RES-ADV', 'Réseaux avancés', 'Mixte', 20, 15, 10),
        ('ADMIN-BD-D', 'Admin BD Distribuées', 'Mixte', 20, 10, 15),
        ('ADMIN-SR', 'Admin Systèmes/Réseaux', 'Mixte', 15, 10, 20),
        ('IA-FUND', 'Concepts Fondamentaux IA', 'Cours', 25, 20, 0),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
    ],
    'MST_SITBD_S3': [
        ('DL', 'Deep Learning', 'Mixte', 25, 15, 15),
        ('AUDIT', 'Audit SI', 'Mixte', 20, 15, 10),
        ('CYBER', 'Cyber Security/Hacking', 'Mixte', 20, 10, 15),
        ('IE', 'Intelligence Émotionnelle', 'TD', 0, 30, 0),
        ('HPC', 'Calcul Haute Performance', 'Mixte', 20, 10, 15),
        ('ADMIN-BIG', 'Admin BD Clusters Big Data', 'Mixte', 20, 10, 15),
    ],
    'MST_GC-M_S1': [
        ('NUM', 'Méthodes numériques', 'Mixte', 20, 15, 10),
        ('CS', 'Calcul des structures', 'Mixte', 25, 15, 10),
        ('MI', 'Maths pour ingénieur', 'Cours', 30, 15, 0),
        ('GP', 'Géophysique', 'Mixte', 20, 15, 10),
        ('GT', 'Géotechnique', 'Mixte', 20, 15, 10),
        ('MC', 'Matériaux de construction', 'Mixte', 20, 10, 15),
    ],
    'MST_GC-M_S3': [
        ('OUV-GC', 'Ouvrages de Génie Civil', 'Mixte', 25, 15, 10),
        ('ASSAIN', 'Assainissement', 'Mixte', 20, 15, 10),
        ('CONST-MET', 'Construction Métallique', 'Mixte', 20, 15, 10),
        ('URB', 'Urbanisme', 'Cours', 20, 20, 0),
        ('EFF-ENER', 'Efficacité énergétique', 'Mixte', 20, 15, 10),
        ('BIM', 'Management BIM', 'Mixte', 15, 15, 15),
    ],
    'MST_BCMB_S1': [
        ('TECH-EXP', 'Techniques Expérimentales', 'TP', 0, 0, 45),
        ('BIO-MOL', 'Biologie Moléculaire', 'Mixte', 25, 10, 15),
        ('ADN-REC', 'Technologie d\'ADN recombinant', 'Mixte', 20, 10, 15),
        ('COM-CELL', 'Communication cellulaire', 'Cours', 25, 15, 0),
        ('BIOINFO', 'Bioinformatique', 'Mixte', 15, 10, 20),
        ('RED-SCI', 'Rédaction scientifique', 'TD', 0, 30, 0),
    ],
    'MST_BCMB_S3-A': [
        ('KIT-EMP', 'Kit Emploi', 'TD', 0, 30, 0),
        ('NEURO', 'Neurobiologie', 'Mixte', 20, 15, 10),
        ('BIO-DEV', 'Biologie développement', 'Mixte', 20, 10, 15),
        ('SEL-ANIM', 'Sélection animale', 'Cours', 20, 20, 0),
        ('THER-GEN', 'Thérapie génique', 'Mixte', 20, 10, 15),
        ('PATH', 'Pathologies', 'Cours', 25, 15, 0),
    ],
    'MST_BCMB_S3-V': [
        ('CELL-VEG', 'Cellules végétales', 'Mixte', 20, 10, 15),
        ('INT-PLANTE', 'Interaction plante/microbe', 'Mixte', 20, 10, 15),
        ('TECH-PAM', 'Technologies PAM', 'Mixte', 15, 10, 20),
        ('MARQ-MOL', 'Marqueurs moléculaires', 'Mixte', 20, 10, 15),
        ('EPID', 'Épidémiologie', 'Cours', 20, 20, 0),
        ('BIOTECH-BIO', 'Biotechnologie biomolécules', 'Mixte', 20, 10, 15),
    ],
    'MST_GMPM_S1': [
        ('CRYST', 'Cristallographie', 'Mixte', 20, 15, 10),
        ('METAL', 'Métallurgie', 'Mixte', 20, 15, 10),
        ('POLY', 'Polymères', 'Mixte', 20, 10, 15),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('CORR', 'Corrosion', 'Mixte', 20, 15, 10),
        ('NANO', 'Nanomatériaux', 'Mixte', 20, 10, 15),
        ('TRIBO', 'Tribologie', 'Mixte', 15, 15, 15),
        ('LEAN', 'Lean Manufacturing', 'Cours', 20, 20, 0),
    ],
    'MST_MMSD_S1': [
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PROG-PR', 'Programmation Python/R', 'Mixte', 20, 10, 15),
        ('CALC-FRAC', 'Calcul fractionnaire', 'Cours', 25, 20, 0),
        ('ANAL-NUM', 'Analyse Numérique', 'Mixte', 25, 15, 10),
        ('EDS', 'EDS', 'Cours', 25, 20, 0),
        ('ANAL-FONC', 'Analyse fonctionnelle', 'Cours', 30, 15, 0),
        ('BIGDATA', 'Big Data', 'Mixte', 20, 10, 15),
        ('SER-CHRON', 'Séries chronologiques', 'Mixte', 20, 15, 10),
    ],
    'MST_GE_S1': [
        ('THERMO-IND', 'Thermo Industrielle', 'Mixte', 25, 15, 10),
        ('TRANS-TH', 'Transferts Thermiques', 'Mixte', 25, 15, 10),
        ('MATH', 'Mathématiques', 'Cours', 30, 15, 0),
        ('MDF', 'Mécanique des Fluides', 'Mixte', 25, 15, 10),
        ('METH-NUM', 'Méthodes Numériques', 'Mixte', 20, 15, 10),
        ('SOL', 'Solaire', 'Mixte', 20, 10, 15),
        ('EFF-ENER', 'Efficacité Énergétique', 'Mixte', 20, 15, 10),
    ],
    'MST_SE_S1': [
        ('TRAIT-EAU', 'Traitement des eaux', 'Mixte', 20, 15, 10),
        ('ENV-MAR', 'Environnement marin', 'Cours', 20, 20, 0),
        ('DECH', 'Déchets', 'Mixte', 20, 15, 10),
        ('ZONE-COT', 'Zones côtières', 'Cours', 20, 20, 0),
        ('GEST-PROJ', 'Gestion de projet', 'TD', 0, 30, 0),
        ('DROIT-ENV', 'Droit environnemental', 'Cours', 20, 20, 0),
    ],
    'MST_IECDD_S1': [
        ('ACC-CLIM', 'Accords climat', 'Cours', 20, 20, 0),
        ('VULNER', 'Vulnérabilité/Adaptation', 'Cours', 20, 20, 0),
        ('GES', 'Gaz à effet de serre', 'Mixte', 20, 15, 10),
        ('POL-CLIM', 'Politique climat', 'Cours', 20, 20, 0),
        ('ANG-SCI', 'Anglais scientifique', 'TD', 0, 30, 0),
    ],
    
    # ═══════════════════════════════════════════════════════════════
    # CYCLE INGÉNIEUR - TOUTES LES FILIÈRES
    # ═══════════════════════════════════════════════════════════════
    
    'ING_GEMI_S1': [
        ('M1', 'Mathématiques I', 'Cours', 30, 15, 0),
        ('EL', 'Électronique', 'Mixte', 20, 15, 10),
        ('EI', 'Électricité industrielle', 'Mixte', 20, 15, 10),
        ('EM', 'Énergétique et MDF', 'Mixte', 20, 15, 10),
        ('INF', 'Informatique', 'Mixte', 15, 10, 20),
        ('LNG', 'Langues', 'TD', 0, 30, 0),
        ('IA', 'Digital Skills & IA', 'Mixte', 15, 10, 15),
    ],
    'ING_GEMI_S3': [
        ('ET', 'Électrotechnique', 'Mixte', 25, 15, 10),
        ('AUTO', 'Automatique avancée', 'Mixte', 25, 15, 10),
        ('MI', 'Machines Industrielles', 'Mixte', 20, 15, 10),
        ('ANG', 'Anglais', 'TD', 0, 30, 0),
        ('M2', 'Mathématiques II', 'Cours', 30, 15, 0),
        ('CP', 'Compétences professionnelles', 'TD', 0, 25, 0),
        ('TS', 'Traitement du Signal', 'Mixte', 20, 15, 10),
    ],
    'ING_GEMI_S5': [
        ('MOD-CMD', 'Modélisation/Commande des machines', 'Mixte', 25, 15, 10),
        ('AMEL-PROC', 'Amélioration des processus', 'Cours', 20, 20, 0),
        ('SYS-EMB', 'Systèmes embarqués', 'Mixte', 20, 10, 15),
        ('RES-TEL', 'Réseaux et Télécom', 'Mixte', 20, 10, 15),
        ('AUTO-ADV', 'Automatique avancée', 'Mixte', 25, 15, 10),
        ('INNOV', 'Innovation', 'TD', 0, 30, 0),
    ],
    'ING_GI-ING_S1': [
        ('MOD-POO', 'Modélisation et POO', 'Mixte', 20, 15, 15),
        ('MATH-APP', 'Mathématiques appliquées', 'Cours', 30, 15, 0),
        ('EI', 'Électricité industrielle', 'Mixte', 20, 15, 10),
        ('EM', 'Énergétique et MDF', 'Mixte', 20, 15, 10),
        ('ELEC-NUM', 'Électronique numérique', 'Mixte', 20, 10, 15),
        ('FR', 'Français', 'TD', 0, 30, 0),
        ('IA', 'IA', 'Mixte', 15, 10, 15),
    ],
    'ING_GI-ING_S3': [
        ('COM-PRO', 'Communication professionnelle', 'TD', 0, 30, 0),
        ('ET', 'Électrotechnique', 'Mixte', 25, 15, 10),
        ('EXCEL-OP', 'Excellence opérationnelle', 'Cours', 20, 20, 0),
        ('MI', 'Machines Industrielles', 'Mixte', 20, 15, 10),
        ('RDM1', 'RDM I', 'Mixte', 25, 15, 10),
        ('ANG', 'Anglais', 'TD', 0, 30, 0),
        ('OPT-PROC', 'Optimisation des Processus', 'Mixte', 20, 15, 10),
    ],
    'ING_GI-ING_S5': [
        ('GRH-COMPTA', 'GRH et Comptabilité', 'Cours', 30, 15, 0),
        ('GEST-PROD', 'Gestion de Production', 'Cours', 25, 20, 0),
        ('QSE-LEAN', 'QSE et Lean Manufacturing', 'Mixte', 20, 15, 10),
        ('LOG', 'Logistique', 'Cours', 20, 20, 0),
        ('OUT-QUAL', 'Outils de la qualité', 'Mixte', 15, 15, 15),
        ('INNOV', 'Innovation', 'TD', 0, 30, 0),
    ],
    'ING_LSI_S1': [
        ('TG', 'Théorie des graphes', 'Cours', 25, 20, 0),
        ('LNX', 'Système LINUX', 'Mixte', 15, 10, 20),
        ('POO', 'POO', 'Mixte', 20, 15, 15),
        ('BDA', 'BD avancées', 'Mixte', 20, 10, 15),
        ('WEB1', 'Technologies web 1', 'Mixte', 15, 10, 20),
        ('LNG', 'Langues', 'TD', 0, 30, 0),
        ('PS', 'Power Skills', 'TD', 0, 25, 0),
    ],
    'ING_LSI_S3': [
        ('ADB', 'Admin BD', 'Mixte', 20, 10, 15),
        ('IOT', 'Internet des objets', 'Mixte', 20, 10, 15),
        ('MIA', 'Méthodologies IA', 'Mixte', 25, 15, 10),
        ('GL', 'Génie Logiciel', 'Mixte', 20, 15, 10),
        ('COM', 'Communication pro', 'TD', 0, 30, 0),
        ('JEE', 'Web JEE', 'Mixte', 15, 10, 20),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
    ],
    'ING_LSI_S5': [
        ('BI', 'Business Intelligence & Big Data', 'Mixte', 25, 15, 15),
        ('VA', 'Vision Artificielle', 'Mixte', 20, 15, 15),
        ('SEC', 'Sécurité Intelligente', 'Mixte', 20, 15, 10),
        ('CI', 'Cloud Intelligence', 'Mixte', 20, 10, 15),
        ('IE', 'Intelligence économique', 'TD', 0, 30, 0),
        ('AP', 'Anglais pro', 'TD', 0, 25, 0),
    ],
    'ING_GEOINF_S1': [
        ('CM', 'Compléments de maths', 'Cours', 30, 15, 0),
        ('PT', 'Physique de la télédétection', 'Mixte', 20, 15, 10),
        ('ST', 'Statistiques', 'Mixte', 20, 15, 10),
        ('APY', 'Algorithmique Python', 'Mixte', 20, 10, 15),
        ('AR', 'Admin Réseaux', 'Mixte', 15, 10, 20),
        ('LNG', 'Langues', 'TD', 0, 30, 0),
        ('PS', 'Power Skills', 'TD', 0, 25, 0),
    ],
    'ING_GEOINF_S3': [
        ('ANG', 'Anglais', 'TD', 0, 30, 0),
        ('ANAL-SPAT', 'Analyse spatiale', 'Mixte', 20, 10, 15),
        ('SIG', 'SIG', 'Mixte', 20, 10, 15),
        ('GEOD', 'Géodésie/GNSS', 'Mixte', 20, 10, 15),
        ('BD-SPAT', 'BD spatiales', 'Mixte', 20, 10, 15),
        ('CP', 'Compétences professionnelles', 'TD', 0, 25, 0),
        ('TOPO', 'Topographie', 'Mixte', 15, 10, 20),
    ],
    'ING_GEOINF_S5': [
        ('GEST-MGT', 'Gestion/Management', 'Cours', 25, 20, 0),
        ('GEO-ENV', 'Géoinformation/Environnement', 'Mixte', 20, 15, 10),
        ('SIG-DEC', 'SIG et décision', 'Mixte', 20, 10, 15),
        ('TELE-RAD', 'Télédétection Radar/Lidar', 'Mixte', 20, 10, 15),
        ('ADMIN-DS', 'Admin données spatiales', 'Mixte', 15, 10, 20),
    ],
    'ING_GA-ING_S1': [
        ('TECH-ANAL', 'Techniques d\'analyses', 'Mixte', 15, 10, 20),
        ('MICRO', 'Microbiologie', 'Mixte', 20, 10, 15),
        ('BIOCHIM', 'Biochimie', 'Mixte', 20, 10, 15),
        ('BIOSTAT', 'Biostatistique', 'Mixte', 20, 15, 10),
        ('PHYSIO', 'Physiologie animale', 'Mixte', 20, 10, 15),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('PS', 'Power Skills', 'TD', 0, 25, 0),
    ],
    'ING_IAGE_S1': [
        ('ECO-AQUA', 'Écosystèmes aquatiques', 'Mixte', 20, 15, 10),
        ('OCEAN', 'Océanologie', 'Cours', 25, 15, 0),
        ('TYPO-ECO', 'Typologie des écosystèmes', 'Cours', 20, 20, 0),
        ('BIO-ORG', 'Biologie des organismes', 'Mixte', 20, 10, 15),
        ('TELE', 'Télédétection', 'Mixte', 15, 10, 20),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('IA-DIG', 'Digital Skills & IA', 'Mixte', 15, 10, 15),
    ],
    'ING_IME_S1': [
        ('MATH', 'Mathématiques', 'Cours', 30, 15, 0),
        ('CHIM-EAU', 'Chimie de l\'Eau', 'Mixte', 20, 15, 10),
        ('MDF', 'Mécanique des fluides', 'Mixte', 25, 15, 10),
        ('ECOTOX', 'Écotoxicologie', 'Mixte', 20, 10, 15),
        ('SYS-INFO', 'Systèmes d\'information', 'Mixte', 15, 10, 20),
        ('ANG', 'Anglais', 'TD', 0, 25, 0),
        ('CULT-DIG', 'Culture Digitale', 'Mixte', 15, 10, 15),
    ],
}


SPECIALITE_KEYWORDS = {
    # ═══════════════════════════════════════════════════
    # MATHÉMATIQUES
    # ═══════════════════════════════════════════════════
    'Mathématiques': [
        'analyse', 'algèbre', 'statistique', 'probabilité',
        'mathématiques', 'math', 'topologie', 'calcul',
        'optimisation', 'recherche opérationnelle',
        'intégration', 'différentiel', 'numérique',
        'fonctionnelle', 'fractionnaire', 'série'
    ],
    
    'Mathématiques Appliquées': [
        'mathématiques', 'math', 'analyse numérique',
        'optimisation', 'modélisation', 'calcul scientifique',
        'méthodes numériques', 'simulation'
    ],
    
    # ═══════════════════════════════════════════════════
    # INFORMATIQUE
    # ═══════════════════════════════════════════════════
    'Informatique': [
        'algorithmique', 'programmation', 'poo', 'python',
        'java', 'c++', 'base de données', 'bd', 'sql',
        'réseaux', 'système', 'linux', 'web', 'html',
        'javascript', 'développement', 'génie logiciel',
        'uml', 'architecture', 'cloud', 'big data',
        'intelligence artificielle', 'ia', 'machine learning',
        'deep learning', 'data', 'blockchain', 'iot',
        'cyber', 'sécurité', 'admin', 'internet'
    ],
    
    # ═══════════════════════════════════════════════════
    # PHYSIQUE
    # ═══════════════════════════════════════════════════
    'Physique': [
        'physique', 'électromagnétisme', 'optique',
        'mécanique', 'thermodynamique', 'énergétique',
        'radioactivité', 'cosmologie', 'mécanique quantique',
        'transfert thermique', 'fluides'
    ],
    
    # ═══════════════════════════════════════════════════
    # CHIMIE
    # ═══════════════════════════════════════════════════
    'Chimie': [
        'chimie', 'organique', 'inorganique', 'minérale',
        'réactivité', 'thermochimie', 'électrochimie',
        'spectroscopie', 'cinétique', 'structure de la matière',
        'biochimie'
    ],
    
    # ═══════════════════════════════════════════════════
    # BIOLOGIE
    # ═══════════════════════════════════════════════════
    'Biologie': [
        'biologie', 'cellulaire', 'moléculaire', 'génétique',
        'microbiologie', 'biotechnologie', 'immunologie',
        'histologie', 'embryologie', 'physiologie',
        'écologie', 'végétale', 'adn', 'organisme',
        'neurobiology', 'pathologie', 'bioinformatique'
    ],
    
    'Biotechnologie': [
        'biotechnologie', 'biologie', 'génétique',
        'microbiologie', 'biochimie', 'enzymologie',
        'génie microbiologique', 'adn', 'cellulaire'
    ],
    
    # ═══════════════════════════════════════════════════
    # GÉNIE CIVIL
    # ═══════════════════════════════════════════════════
    'Génie Civil': [
        'béton', 'construction', 'rdm', 'résistance',
        'structure', 'sol', 'géotechnique', 'métallique',
        'ouvrage', 'assainissement', 'urbanisme',
        'matériaux de construction', 'géophysique',
        'dynamique', 'mécanique des milieux'
    ],
    
    # ═══════════════════════════════════════════════════
    # GÉNIE ÉLECTRIQUE
    # ═══════════════════════════════════════════════════
    'Génie Électrique': [
        'électronique', 'électrotechnique', 'automatique',
        'signal', 'traitement', 'circuit', 'électricité',
        'puissance', 'actionneur', 'systèmes embarqués',
        'métrologie', 'instrumentation', 'convertisseur',
        'réseau électrique', 'télécommunication'
    ],
    
    # ═══════════════════════════════════════════════════
    # GÉNIE MÉCANIQUE
    # ═══════════════════════════════════════════════════
    'Génie Mécanique': [
        'mécanique', 'fluides', 'thermique', 'cao',
        'machine', 'hydraulique', 'solides', 'fabrication',
        'conception', 'tribologie', 'élément de machine',
        'productique'
    ],
    
    # ═══════════════════════════════════════════════════
    # GÉNIE INDUSTRIEL
    # ═══════════════════════════════════════════════════
    'Génie Industriel': [
        'gestion', 'production', 'qualité', 'maintenance',
        'lean', 'logistique', 'processus', 'excellence',
        'qse', 'grh', 'comptabilité', 'management',
        'industriel', 'supply chain'
    ],
    
    # ═══════════════════════════════════════════════════
    # GÉNIE DES PROCÉDÉS
    # ═══════════════════════════════════════════════════
    'Génie des Procédés': [
        'réacteur', 'procédé', 'opération unitaire',
        'bilan', 'matière', 'énergie', 'génie chimique',
        'modélisation', 'simulation'
    ],
    
    # ═══════════════════════════════════════════════════
    # ÉNERGIES
    # ═══════════════════════════════════════════════════
    'Énergies Renouvelables': [
        'énergie', 'solaire', 'renouvelable', 'enr',
        'photovoltaïque', 'efficacité énergétique',
        'thermique', 'transfert', 'énergétique'
    ],
    
    'Génie Énergétique': [
        'énergie', 'thermique', 'transfert', 'solaire',
        'efficacité', 'thermodynamique', 'mécanique des fluides'
    ],
    
    # ═══════════════════════════════════════════════════
    # GÉOSCIENCES
    # ═══════════════════════════════════════════════════
    'Géosciences': [
        'géologie', 'stratigraphie', 'paléo', 'pétrographie',
        'minéralogie', 'géomatique', 'géophysique',
        'télédétection', 'sig', 'spatial', 'géodésie',
        'topographie', 'environnement', 'écosystème'
    ],
    
    'Géoinformation': [
        'géoinformation', 'sig', 'télédétection', 'spatial',
        'géodésie', 'gnss', 'topographie', 'analyse spatiale',
        'géomatique', 'lidar', 'radar'
    ],
    
    # ═══════════════════════════════════════════════════
    # ENVIRONNEMENT
    # ═══════════════════════════════════════════════════
    'Sciences de l\'Environnement': [
        'environnement', 'traitement', 'eau', 'déchet',
        'côtier', 'marin', 'climat', 'pollution',
        'écotoxicologie', 'aquaculture', 'océan',
        'vulnérabilité', 'gaz à effet de serre'
    ],
    
    # ═══════════════════════════════════════════════════
    # MATÉRIAUX
    # ═══════════════════════════════════════════════════
    'Génie des Matériaux': [
        'matériaux', 'cristallographie', 'métallurgie',
        'polymère', 'corrosion', 'nanomatériaux',
        'tribologie', 'génie des matériaux'
    ],
    
    # ═══════════════════════════════════════════════════
    # STATISTIQUE & DATA SCIENCE
    # ═══════════════════════════════════════════════════
    'Statistique': [
        'statistique', 'probabilité', 'analyse de données',
        'data', 'enquête', 'sondage', 'biostatistique',
        'série chronologique', 'échantillonnage'
    ],
    
    # ═══════════════════════════════════════════════════  
    # LANGUES
    # ═══════════════════════════════════════════════════
    'Langues': [
        'anglais', 'français', 'langue', 'communication',
        'rédaction', 'scientifique'
    ],
    
    # ═══════════════════════════════════════════════════
    # SOFT SKILLS
    # ═══════════════════════════════════════════════════
    'Management': [
        'management', 'gestion', 'projet', 'grh',
        'comptabilité', 'innovation', 'compétence',
        'skill', 'professionnel', 'intelligence émotionnelle',
        'digital', 'leadership', 'droit'
    ],
    
    # ═══════════════════════════════════════════════════
    # AGROALIMENTAIRE
    # ═══════════════════════════════════════════════════
    'Agroalimentaire': [
        'agroalimentaire', 'analyse', 'microbiologie',
        'physiologie animale', 'biochimie'
    ],
}
