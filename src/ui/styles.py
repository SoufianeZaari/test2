# src/ui/styles.py
"""
Styles CSS professionnels pour l'interface FSTT
Utilise les couleurs officielles de la FSTT (Bleu #0066CC et Jaune #FFC107)
"""

from configUI import COLORS

# ═══════════════════════════════════════════════════════════
# STYLE GLOBAL DE L'APPLICATION
# ═══════════════════════════════════════════════════════════

GLOBAL_STYLE = f"""
QWidget {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: {COLORS['text_dark']};
}}

/* Enlever les bordures par défaut */
QFrame, QLabel, QPushButton {{
    border: none;
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES PAGE LOGIN
# ═══════════════════════════════════════════════════════════

LOGIN_TITLE_STYLE = f"""
QLabel {{
    color: {COLORS['primary_blue']};
    font-size: 28px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 20px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['primary_blue']},
        stop:1 {COLORS['primary_yellow']}
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
"""

LOGIN_SUBTITLE_STYLE = f"""
QLabel {{
    color: {COLORS['text_light']};
    font-size: 14px;
    padding: 5px;
}}
"""

# Bouton LOGIN principal (grand bouton sur background)
LOGIN_MAIN_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['primary_blue']};
    color: white;
    font-size: 24px;
    font-weight: bold;
    padding: 25px 60px;
    border: none;
    border-radius: 15px;
    letter-spacing: 2px;
}}
QPushButton:hover {{
    background-color: {COLORS['secondary_blue']};
    transform: scale(1.05);
}}
QPushButton:pressed {{
    background-color: #003366;
}}
"""

# Formulaire de connexion (container)
LOGIN_FORM_CONTAINER_STYLE = f"""
QFrame {{
    background-color: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    border: 2px solid {COLORS['primary_blue']};
}}
"""

# Input fields (Email, Password)
LOGIN_INPUT_STYLE = f"""
QLineEdit {{
    background-color: white;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    padding: 15px;
    font-size: 15px;
    color: {COLORS['text_dark']};
}}
QLineEdit:focus {{
    border: 2px solid {COLORS['primary_blue']};
    background-color: #F8F9FA;
}}
QLineEdit:hover {{
    border: 2px solid {COLORS['primary_yellow']};
}}
"""

# Labels des inputs
LOGIN_LABEL_STYLE = f"""
QLabel {{
    color: {COLORS['text_dark']};
    font-size: 14px;
    font-weight: 600;
    padding: 5px 0px;
}}
"""

# Bouton Se Connecter
LOGIN_SUBMIT_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['primary_blue']};
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 15px;
    border: none;
    border-radius: 8px;
    letter-spacing: 1px;
}}
QPushButton:hover {{
    background-color: {COLORS['secondary_blue']};
}}
QPushButton:pressed {{
    background-color: #003366;
}}
QPushButton:disabled {{
    background-color: #CCCCCC;
    color: #666666;
}}
"""

# Bouton Quitter
LOGIN_QUIT_BUTTON_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: {COLORS['text_light']};
    font-size: 14px;
    padding: 12px;
    border: 2px solid {COLORS['text_light']};
    border-radius: 8px;
}}
QPushButton:hover {{
    background-color: {COLORS['error']};
    color: white;
    border: 2px solid {COLORS['error']};
}}
"""

# Messages d'erreur
LOGIN_ERROR_STYLE = f"""
QLabel {{
    color: {COLORS['error']};
    font-size: 13px;
    padding: 8px;
    background-color: rgba(231, 76, 60, 0.1);
    border-left: 4px solid {COLORS['error']};
    border-radius: 4px;
}}
"""

# Messages de succès
LOGIN_SUCCESS_STYLE = f"""
QLabel {{
    color: {COLORS['success']};
    font-size: 13px;
    padding: 8px;
    background-color: rgba(39, 174, 96, 0.1);
    border-left: 4px solid {COLORS['success']};
    border-radius: 4px;
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES MENU LATÉRAL (Pour Admin/Enseignant/Étudiant)
# ═══════════════════════════════════════════════════════════

SIDEBAR_STYLE = f"""
QFrame {{
    background-color: {COLORS['bg_dark']};
    border: none;
}}
"""

SIDEBAR_BUTTON_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: white;
    text-align: left;
    padding: 15px 20px;
    font-size: 15px;
    border: none;
    border-left: 4px solid transparent;
}}
QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.1);
    border-left: 4px solid {COLORS['primary_yellow']};
}}
QPushButton:checked {{
    background-color: rgba(0, 102, 204, 0.3);
    border-left: 4px solid {COLORS['primary_blue']};
    font-weight: bold;
}}
"""

SIDEBAR_TITLE_STYLE = f"""
QLabel {{
    color: white;
    font-size: 18px;
    font-weight: bold;
    padding: 20px;
    background-color: {COLORS['primary_blue']};
}}
"""

SIDEBAR_USER_INFO_STYLE = f"""
QLabel {{
    color: white;
    font-size: 13px;
    padding: 10px 20px;
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES TABLEAUX (Pour listes d'étudiants, salles, etc.)
# ═══════════════════════════════════════════════════════════

TABLE_STYLE = f"""
QTableWidget {{
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    gridline-color: #F0F0F0;
}}
QTableWidget::item {{
    padding: 10px;
    border-bottom: 1px solid #F0F0F0;
}}
QTableWidget::item:selected {{
    background-color: {COLORS['primary_blue']};
    color: white;
}}
QHeaderView::section {{
    background-color: {COLORS['bg_light']};
    color: {COLORS['text_dark']};
    font-weight: bold;
    padding: 12px;
    border: none;
    border-bottom: 2px solid {COLORS['primary_blue']};
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES BOUTONS STANDARDS
# ═══════════════════════════════════════════════════════════

PRIMARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['primary_blue']};
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 12px 25px;
    border: none;
    border-radius: 6px;
}}
QPushButton:hover {{
    background-color: {COLORS['secondary_blue']};
}}
QPushButton:pressed {{
    background-color: #003366;
}}
QPushButton:disabled {{
    background-color: #CCCCCC;
    color: #666666;
}}
"""

SECONDARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: {COLORS['primary_blue']};
    font-size: 14px;
    padding: 12px 25px;
    border: 2px solid {COLORS['primary_blue']};
    border-radius: 6px;
}}
QPushButton:hover {{
    background-color: {COLORS['primary_blue']};
    color: white;
}}
"""

SUCCESS_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['success']};
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 12px 25px;
    border: none;
    border-radius: 6px;
}}
QPushButton:hover {{
    background-color: #229954;
}}
"""

DANGER_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['error']};
    color: white;
    font-size: 14px;
    font-weight: bold;
    padding: 12px 25px;
    border: none;
    border-radius: 6px;
}}
QPushButton:hover {{
    background-color: #C0392B;
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES CARDS (Pour dashboard)
# ═══════════════════════════════════════════════════════════

CARD_STYLE = f"""
QFrame {{
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 20px;
}}
QFrame:hover {{
    border: 1px solid {COLORS['primary_blue']};
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}}
"""

CARD_TITLE_STYLE = f"""
QLabel {{
    color: {COLORS['text_dark']};
    font-size: 18px;
    font-weight: bold;
    padding-bottom: 10px;
}}
"""

CARD_VALUE_STYLE = f"""
QLabel {{
    color: {COLORS['primary_blue']};
    font-size: 32px;
    font-weight: bold;
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES EMPLOI DU TEMPS (Calendar/Grid)
# ═══════════════════════════════════════════════════════════

SCHEDULE_GRID_STYLE = f"""
QFrame {{
    background-color: white;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
}}
"""

SCHEDULE_CELL_COURS_STYLE = f"""
QLabel {{
    background-color: {COLORS['primary_blue']};
    color: white;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
}}
"""

SCHEDULE_CELL_TD_STYLE = f"""
QLabel {{
    background-color: {COLORS['success']};
    color: white;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
}}
"""

SCHEDULE_CELL_TP_STYLE = f"""
QLabel {{
    background-color: {COLORS['primary_yellow']};
    color: {COLORS['text_dark']};
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
}}
"""

SCHEDULE_CELL_EXAMEN_STYLE = f"""
QLabel {{
    background-color: {COLORS['error']};
    color: white;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES INPUTS & FORMS
# ═══════════════════════════════════════════════════════════

INPUT_STYLE = f"""
QLineEdit, QTextEdit, QComboBox, QSpinBox {{
    background-color: white;
    border: 2px solid #E0E0E0;
    border-radius: 6px;
    padding: 10px;
    font-size: 14px;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 2px solid {COLORS['primary_blue']};
}}
"""

# ═══════════════════════════════════════════════════════════
# STYLES SCROLLBAR
# ═══════════════════════════════════════════════════════════

SCROLLBAR_STYLE = f"""
QScrollBar:vertical {{
    background: #F0F0F0;
    width: 12px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['primary_blue']};
    border-radius: 6px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['secondary_blue']};
}}
QScrollBar:horizontal {{
    background: #F0F0F0;
    height: 12px;
    border-radius: 6px;
}}
QScrollBar::handle:horizontal {{
    background: {COLORS['primary_blue']};
    border-radius: 6px;
    min-width: 20px;
}}
"""

# ═══════════════════════════════════════════════════════════
# FONCTION UTILITAIRE
# ═══════════════════════════════════════════════════════════

def get_icon_button_style(color=None):
    """
    Retourne le style pour un bouton avec icône
    Args:
        color: Couleur de fond (optionnel)
    """
    bg_color = color or COLORS['primary_blue']
    return f"""
    QPushButton {{
        background-color: {bg_color};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        opacity: 0.8;
    }}
    """

SOBER_BUTTON_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: {COLORS['text_dark']};
    font-size: 14px;
    font-weight: 500;
    padding: 12px 25px;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
}}
QPushButton:hover {{
    border: 1px solid {COLORS['primary_blue']};
    color: {COLORS['primary_blue']};
    background-color: #F5F5F5;
}}
"""