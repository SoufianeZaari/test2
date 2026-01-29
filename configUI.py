import os
from pathlib import Path
from config import MESSAGES, BASE_DIR

# ═══════════════════════════════════════════════════════════
# CHEMINS DES ASSETS
# ═══════════════════════════════════════════════════════════

ASSETS_DIR = BASE_DIR / 'assets'
IMAGES_DIR = ASSETS_DIR / 'images'

# Créer les dossiers s'ils n'existent pas
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

FST_BACKGROUND_IMAGE = str(IMAGES_DIR / 'fst_background.png')
FST_LOGO_IMAGE = str(IMAGES_DIR / 'fst_log.png')

# ═══════════════════════════════════════════════════════════
# COULEURS (CHARTE GRAPHIQUE FSTT)
# ═══════════════════════════════════════════════════════════

COLORS = {
    'primary_blue': '#0066CC',      # Bleu FST officiel
    'secondary_blue': '#0052a3',    # Bleu foncé (hover)
    'primary_yellow': '#FFC107',    # Jaune/Or (accents)
    'secondary_yellow': '#FFB300',
    'text_dark': '#2C3E50',
    'text_light': '#7F8C8D',
    'bg_light': '#F8F9FA',
    'bg_dark': '#2C3E50',
    'success': '#27AE60',
    'error': '#E74C3C',
    'warning': '#F39C12',
    'overlay_dark': 'rgba(0, 0, 0, 180)'
}

# ═══════════════════════════════════════════════════════════
# CONFIGURATION DES FENÊTRES
# ═══════════════════════════════════════════════════════════

WINDOW_CONFIG = {
    'login': {
        'title': 'FST Tanger - Connexion',
        'width': 1280,
        'height': 720
    },
    'admin': {
        'title': 'FST Tanger - Administration',
        'width': 1400,
        'height': 900
    },
    'enseignant': {
        'title': 'FST Tanger - Espace Enseignant',
        'width': 1280,
        'height': 800
    },
    'etudiant': {
        'title': 'FST Tanger - Espace Étudiant',
        'width': 1280,
        'height': 800
    }
}
