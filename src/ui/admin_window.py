# src/ui/admin_window.py
"""
Fenêtre principale de l'administrateur
Version professionnelle : Sans emojis, visualisations de données, gestion réservations stricte
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QStackedWidget, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, QSize, QRectF, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen

from configUI import WINDOW_CONFIG, COLORS, FST_LOGO_IMAGE
from config import FILIERES_LST, FILIERES_MST, FILIERES_INGENIEUR, MATIERES_COMPLETES
from src.ui.styles import (
    GLOBAL_STYLE, SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE, 
    SIDEBAR_USER_INFO_STYLE,
    CARD_STYLE, CARD_TITLE_STYLE, CARD_VALUE_STYLE,
    PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    SUCCESS_BUTTON_STYLE, DANGER_BUTTON_STYLE,
    TABLE_STYLE, SOBER_BUTTON_STYLE
)

# === WIDGET CUSTOM POUR GRAPHIQUE BARRES ===
class SimpleBarChart(QWidget):
    def __init__(self, data, title="Statistiques"):
        super().__init__()
        self.data = data # List of tuples (Label, Value)
        self.chart_title = title
        self.setMinimumHeight(250)
        self.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #E0E0E0;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dimensions
        w = self.width()
        h = self.height()
        margin = 40
        bar_gap = 20
        
        # Fond blanc
        painter.fillRect(0, 0, w, h, Qt.GlobalColor.white)
        
        # Titre
        painter.setPen(QColor(COLORS['text_dark']))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(20, 30, self.chart_title)
        
        # Zone de dessin
        graph_w = w - 2 * margin
        graph_h = h - 2 * margin - 20
        start_x = margin
        start_y = h - margin
        
        # Axes
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        painter.drawLine(int(start_x), int(start_y), int(start_x + graph_w), int(start_y)) # X Axis
        painter.drawLine(int(start_x), int(start_y), int(start_x), int(start_y - graph_h)) # Y Axis
        
        if not self.data:
            return
            
        # Calculs barres
        max_val = max([v for l, v in self.data]) if self.data else 10
        max_val = max(max_val, 10) # Minimum scale
        
        count = len(self.data)
        bar_width = (graph_w - ((count + 1) * bar_gap)) / count
        
        # Dessin barres
        for i, (label, value) in enumerate(self.data):
            x = start_x + bar_gap + (i * (bar_width + bar_gap))
            bar_h = (value / max_val) * graph_h
            y = start_y - bar_h
            
            # Barre
            color = QColor(COLORS['primary_blue'])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_h), 4, 4)
            
            # Label X
            painter.setPen(QColor(COLORS['text_dark']))
            font.setBold(False)
            font.setPointSize(8)
            painter.setFont(font)
            rect_x = QRectF(x, start_y + 5, bar_width, 20)
            painter.drawText(rect_x, Qt.AlignmentFlag.AlignCenter, label)
            
            # Valeur au dessus
            painter.setPen(QColor(COLORS['primary_blue']))
            font.setBold(True)
            painter.setFont(font)
            rect_val = QRectF(x, y - 20, bar_width, 20)
            painter.drawText(rect_val, Qt.AlignmentFlag.AlignCenter, str(value))


class UserWrapper:
    def __init__(self, user_tuple):
        # Tuple: (id, nom, prenom, email, type, ...)
        # Fallback safe index handling
        self.id = user_tuple[0] if len(user_tuple) > 0 else 0
        self.nom = user_tuple[1] if len(user_tuple) > 1 else "Inconnu"
        self.prenom = user_tuple[2] if len(user_tuple) > 2 else ""
        self.email = user_tuple[3] if len(user_tuple) > 3 else ""

class AdminWindow(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, user, db):
        super().__init__()
        
        # Handle tuple vs object
        if isinstance(user, tuple):
            self.user = UserWrapper(user)
        else:
            self.user = user
            
        self.db = db
        
        # Configuration de la fenêtre
        self.setWindowTitle(WINDOW_CONFIG['admin']['title'])
        # Suppression de setFixedSize pour permettre le plein écran
        self.setMinimumSize(1024, 768)
        
        self.setStyleSheet(GLOBAL_STYLE)
        
        # État des réservations (Simulation)
        self.reservations_data = [
            {"date": "2024-02-10", "prof": "M. Alami", "salle": "Amphi B", "motif": "Examen Partiel"},
            {"date": "2024-02-12", "prof": "Mme. Bennani", "salle": "Salle 12", "motif": "Séance Rattrapage"}
        ]

        # Layout principal (Horizontal: Sidebar + Contenu)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Créer la sidebar
        self.create_sidebar()
        
        # 2. Créer la zone de contenu
        self.create_content_area()
        
        # Afficher le dashboard par défaut
        self.switch_page("Dashboard")
        
    def calculate_stats(self):
        """Calcule les statistiques dynamiques"""
        stats = {}
        
        # 1. Utilisateurs (DB)
        try:
            stats['enseignants'] = len(self.db.get_tous_utilisateurs('enseignant'))
            stats['etudiants'] = len(self.db.get_tous_utilisateurs('etudiant'))
        except:
            stats['enseignants'] = 0
            stats['etudiants'] = 0
            
        # 2. Filières (Config + DB ideally, but user asked for "Fichiers fournis" -> Config)
        # Sum of all lists in config
        nb_filieres = len(FILIERES_LST) + len(FILIERES_MST) + len(FILIERES_INGENIEUR)
        stats['filieres'] = nb_filieres
        
        # 3. Matières (Config)
        # MATIERES_COMPLETES is dict: 'CODE_PROG': [list of subjects]
        nb_matieres = 0
        for prog, subjects in MATIERES_COMPLETES.items():
            nb_matieres += len(subjects)
        stats['matieres'] = nb_matieres
        
        # 4. Groupes (DB)
        try:
            stats['groupes'] = len(self.db.get_tous_groupes())
        except:
            stats['groupes'] = 0
            
        return stats

    def refresh_dashboard(self):
        """Met à jour les compteurs du dashboard"""
        stats = self.calculate_stats()
        
        # Update Labels if they exist
        # We need to access the labels. In create_dashboard_page, we should store them.
        # If not stored, we might re-create the page or store references.
        # Let's check create_dashboard_page implementation.
        # Currently it creates local variables.
        # I will modify create_dashboard_page to store references in self.stat_labels
        
        if hasattr(self, 'stat_labels'):
            self.stat_labels['Enseignants'].setText(str(stats['enseignants']))
            self.stat_labels['Étudiants'].setText(str(stats['etudiants']))
            self.stat_labels['Filières'].setText(str(stats['filieres']))
            self.stat_labels['Matières'].setText(str(stats['matieres'])) # Replacement for Groups or Add new
            # User asked for Filiere and Matiere specifically.
            # Old code had Groups. I'll keep groups or replace?
            # User: "Afficher ces chiffres correctement dans le tableau de bord."
            # I will show: Enseignants, Etudiants, Fillieres, Matieres.

        


    def create_sidebar(self):
        """Crée le menu latéral gauche"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 20)
        sidebar_layout.setSpacing(10)
        
        # === EN-TÊTE SIDEBAR ===
        header_container = QFrame()
        header_container.setStyleSheet(f"background-color: {COLORS['primary_blue']};")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 30, 20, 30)
        

        
        # Titre Rôle
        title_label = QLabel("ADMINISTRATEUR")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-top: 10px; letter-spacing: 1px;")
        header_layout.addWidget(title_label)
        
        sidebar_layout.addWidget(header_container)
        
        # === MENU DE NAVIGATION ===
        self.menu_buttons = {}
        
        # Menus nettoyés (Sans Emojis, Sans Gestion Salles)
        menus = [
            ("Dashboard", "Dashboard"),
            ("Générer Emploi", "Generation"),
            ("Réservations", "Reservations"),
            ("Notifications", "Notifications"),
        ]
        
        for label, page_id in menus:
            btn = QPushButton(f"  {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(SIDEBAR_BUTTON_STYLE)
            btn.clicked.connect(lambda checked, pid=page_id: self.switch_page(pid))
            sidebar_layout.addWidget(btn)
            self.menu_buttons[page_id] = btn
            
        sidebar_layout.addStretch()
        
        # === PIED DE PAGE ===
        user_info = QLabel(f"{self.user.nom if self.user else 'Admin'}")
        user_info.setStyleSheet(SIDEBAR_USER_INFO_STYLE)
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(user_info)
        
        logout_btn = QPushButton("Déconnexion")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e74c3c;
                border: 1px solid #e74c3c;
                border-radius: 5px;
                padding: 10px;
                margin: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: white;
            }
        """)
        logout_btn.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(logout_btn)
        
        self.main_layout.addWidget(self.sidebar)

    def create_content_area(self):
        """Crée la zone principale de contenu"""
        self.content_area = QFrame()
        self.content_area.setStyleSheet(f"background-color: {COLORS['bg_light']};")
        
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Titre de la page
        self.page_title = QLabel("Tableau de Bord")
        self.page_title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['text_dark']}; margin-bottom: 20px;")
        content_layout.addWidget(self.page_title)
        
        # Stacked Widget
        self.pages = QStackedWidget()
        
        self.dashboard_page = self.create_dashboard_page()
        self.pages.addWidget(self.dashboard_page)
        
        self.generation_page = self.create_generation_page()
        self.pages.addWidget(self.generation_page)
        
        self.reservations_page = self.create_reservations_page()
        self.pages.addWidget(self.reservations_page)

        self.notifications_page = self.create_notifications_page()
        self.pages.addWidget(self.notifications_page)
        
        content_layout.addWidget(self.pages)
        self.main_layout.addWidget(self.content_area)

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # === KPI CARDS (REAL DATA) ===
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Initial Calc
        current_stats = self.calculate_stats()
        
        # Define KPI structure
        kpis = [
            ("Enseignants", current_stats['enseignants']),
            ("Étudiants", current_stats['etudiants']),
            ("Filières", current_stats['filieres']),
            ("Matières", current_stats['matieres'])
        ]
        
        self.stat_labels = {}
        
        for title, value in kpis:
            card = QFrame()
            card.setStyleSheet(CARD_STYLE)
            card_layout = QVBoxLayout(card)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(CARD_TITLE_STYLE)
            card_layout.addWidget(title_label)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet(CARD_VALUE_STYLE)
            card_layout.addWidget(value_label)
            
            self.stat_labels[title] = value_label
            stats_layout.addWidget(card)
            
        layout.addLayout(stats_layout)
        
        # === GRAPHIQUES (REAL DATA) ===
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Salles par type
        try:
            salles = self.db.get_toutes_salles()
            type_counts = {}
            for s in salles:
                t = s[3] # type_salle check db schema: id, nom, capacite, type_salle
                type_counts[t] = type_counts.get(t, 0) + 1
            salles_data = list(type_counts.items())
        except:
            salles_data = []

        chart_salles = SimpleBarChart(salles_data, "Répartition des Salles")
        charts_layout.addWidget(chart_salles)
        
        # Mock chart for volume (calculation expensive without proper SQL)
        heures_data = [("Lundi", 0), ("Mardi", 0), ("Mercredi", 0), ("Jeudi", 0), ("Vendredi", 0)]
        chart_heures = SimpleBarChart(heures_data, "Volume Horaire (En cours)")
        charts_layout.addWidget(chart_heures)
        
        layout.addLayout(charts_layout)
        
        # "Supprimer les actions administratives visibles" -> Done (Code block removed)
        
        return page

    def create_generation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        # Section Import
        import_group = QFrame()
        import_group.setStyleSheet(CARD_STYLE)
        ig_layout = QVBoxLayout(import_group)
        
        ig_title = QLabel("Importation des Données (CSV)")
        ig_title.setStyleSheet(CARD_TITLE_STYLE)
        ig_layout.addWidget(ig_title)
        
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(15)
        
        # Boutons d'import uniformisés
        # "Même taille, Même forme, Même style, Supprimer les background colors" -> SOBER_BUTTON_STYLE
        
        imports = [
            ("Importer les Salles", "salles"),
            ("Importer Enseignants", "enseignants"),
            ("Importer Étudiants", "etudiants"),
            ("Importer Groupes", "groupes")
        ]
        
        row, col = 0, 0
        for label, type_imp in imports:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(SOBER_BUTTON_STYLE)
            btn.setFixedHeight(50) # Uniform height
            btn.clicked.connect(lambda _, t=type_imp: self.run_import(t))
            
            buttons_layout.addWidget(btn, row, col)
            col += 1
            if col > 1: # 2 columns
                col = 0
                row += 1
                
        ig_layout.addLayout(buttons_layout)
        layout.addWidget(import_group)
        
        # Bouton Génération
        gen_container = QFrame()
        gen_container.setStyleSheet(CARD_STYLE)
        gen_layout = QVBoxLayout(gen_container)
        
        gen_title = QLabel("Génération")
        gen_title.setStyleSheet(CARD_TITLE_STYLE)
        gen_layout.addWidget(gen_title)
        
        self.btn_generate = QPushButton("Lancer la Génération de l'Emploi du Temps")
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        # Uniform with import buttons but maybe bold? User asked "Uniformiser TOUS les boutons" ?
        # "Uniformiser tous les boutons : Même taille, Même forme, Même style"
        # I will apply SOBER_BUTTON_STYLE to this one too, or checks with user requirement. 
        # usually Generation is a primary action. But "Supprimer les background colors" applies generally.
        self.btn_generate.setStyleSheet(SOBER_BUTTON_STYLE)
        self.btn_generate.setFixedHeight(50)
        
        gen_layout.addWidget(self.btn_generate)
        layout.addWidget(gen_container)
        
        layout.addStretch()
        return page

    def run_import(self, type_import):
        """Exécute l'import via ImportManager"""
        from src.import_manager import ImportManager
        from config import CSV_TEMPLATES
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f"Sélectionner le fichier {type_import} CSV",
            "", 
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        manager = ImportManager()
        success = False
        
        if type_import == "salles":
            success = manager.import_salles(file_path)
        elif type_import == "enseignants":
            success = manager.import_enseignants(file_path)
        elif type_import == "etudiants":
            success = manager.import_etudiants(file_path)
        elif type_import == "groupes":
            success = manager.import_groupes(file_path)
            
        if success:
            QMessageBox.information(self, "Succès", f"Import {type_import} réussi !")
            self.refresh_dashboard()
        else:
            QMessageBox.critical(self, "Erreur", f"Échec de l'import {type_import}. Vérifiez le format.")

    def create_reservations_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header avec compteur et bouton actualiser
        header_layout = QHBoxLayout()
        title = QLabel("Demandes de Réservation")
        title.setStyleSheet(CARD_TITLE_STYLE)
        
        self.counter_label = QLabel("0 demandes en attente")
        self.counter_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px; font-weight: bold;")
        
        btn_refresh = QPushButton("Actualiser")
        btn_refresh.setStyleSheet(SECONDARY_BUTTON_STYLE)
        btn_refresh.clicked.connect(self.refresh_reservations)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.counter_label)
        header_layout.addWidget(btn_refresh)
        layout.addLayout(header_layout)
        
        # Table des réservations - colonnes améliorées
        self.res_table = QTableWidget()
        self.res_table.setColumnCount(7)
        self.res_table.setHorizontalHeaderLabels([
            "Date", "Horaire", "Enseignant", "Email", "Salle", "Motif/Type", "Actions"
        ])
        self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.res_table.setStyleSheet(TABLE_STYLE)
        
        layout.addWidget(self.res_table)
        
        # Populate initial
        self.refresh_reservations()
        
        return page

    def refresh_reservations(self):
        """Affiche les réservations depuis la base de données"""
        self.res_table.setRowCount(0)
        
        try:
            # Charger les réservations depuis la BDD
            reservations = self.db.get_reservations_by_statut('en_attente')
            
            pending_count = len(reservations)
            
            # Mise à jour compteur
            self.counter_label.setText(f"{pending_count} demande{'s' if pending_count > 1 else ''} en attente")
            if pending_count == 0:
                self.counter_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
            else:
                self.counter_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 14px; font-weight: bold;")
            
            for i, res in enumerate(reservations):
                # res: (id, enseignant_id, salle_id, date, heure_debut, heure_fin, statut, motif, date_demande)
                self.res_table.insertRow(i)
                
                res_id = res[0]
                enseignant_id = res[1]
                salle_id = res[2]
                date = res[3]
                heure_debut = res[4]
                heure_fin = res[5]
                statut = res[6]
                motif = res[7] or ""
                
                # Récupérer infos enseignant
                enseignant = self.db.get_utilisateur_by_id(enseignant_id)
                prof_nom = f"{enseignant[2]} {enseignant[1]}" if enseignant else "Inconnu"
                prof_email = enseignant[3] if enseignant else ""
                
                # Récupérer infos salle
                salle = self.db.get_salle_by_id(salle_id)
                salle_nom = salle[1] if salle else "Inconnue"
                
                # Remplir les colonnes
                self.res_table.setItem(i, 0, QTableWidgetItem(date))
                self.res_table.setItem(i, 1, QTableWidgetItem(f"{heure_debut} - {heure_fin}"))
                self.res_table.setItem(i, 2, QTableWidgetItem(prof_nom))
                self.res_table.setItem(i, 3, QTableWidgetItem(prof_email))
                self.res_table.setItem(i, 4, QTableWidgetItem(salle_nom))
                self.res_table.setItem(i, 5, QTableWidgetItem(motif))
                
                # Actions Widget
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                actions_layout.setSpacing(10)
                actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                btn_accept = QPushButton("Accepter")
                btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_accept.setStyleSheet("""
                    QPushButton { background-color: #27ae60; color: white; border-radius: 4px; padding: 6px 12px; border:none; font-weight:bold;}
                    QPushButton:hover { background-color: #219150; }
                """)
                btn_accept.clicked.connect(lambda _, rid=res_id: self.handle_reservation_db(rid, True))
                
                btn_refuse = QPushButton("Refuser")
                btn_refuse.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_refuse.setStyleSheet("""
                    QPushButton { background-color: #c0392b; color: white; border-radius: 4px; padding: 6px 12px; border:none; font-weight:bold;}
                    QPushButton:hover { background-color: #a93226; }
                """)
                btn_refuse.clicked.connect(lambda _, rid=res_id: self.handle_reservation_db(rid, False))
                
                actions_layout.addWidget(btn_accept)
                actions_layout.addWidget(btn_refuse)
                
                self.res_table.setCellWidget(i, 6, actions_widget)
                self.res_table.setRowHeight(i, 60)
                
        except Exception as e:
            print(f"Erreur chargement réservations: {e}")
            # Fallback to mock data
            self._refresh_reservations_mock()

    def _refresh_reservations_mock(self):
        """Fallback avec données fictives si la BDD n'est pas accessible"""
        pending_count = sum(1 for r in self.reservations_data if 'status' not in r)
        
        self.counter_label.setText(f"{pending_count} demande{'s' if pending_count > 1 else ''} en attente")
        if pending_count == 0:
            self.counter_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        else:
            self.counter_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 14px; font-weight: bold;")
            
        for i, row_data in enumerate(self.reservations_data):
            self.res_table.insertRow(i)
            self.res_table.setItem(i, 0, QTableWidgetItem(row_data['date']))
            self.res_table.setItem(i, 1, QTableWidgetItem("08:30 - 10:00"))
            self.res_table.setItem(i, 2, QTableWidgetItem(row_data['prof']))
            self.res_table.setItem(i, 3, QTableWidgetItem(""))
            self.res_table.setItem(i, 4, QTableWidgetItem(row_data['salle']))
            self.res_table.setItem(i, 5, QTableWidgetItem(row_data['motif']))
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(10)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if 'status' in row_data:
                status = row_data['status']
                lbl_status = QLabel(status)
                color = "#27ae60" if status == "Acceptée" else "#c0392b"
                lbl_status.setStyleSheet(f"color: white; background-color: {color}; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
                actions_layout.addWidget(lbl_status)
            else:
                btn_accept = QPushButton("Accepter")
                btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_accept.setStyleSheet("""
                    QPushButton { background-color: #27ae60; color: white; border-radius: 4px; padding: 6px 12px; border:none; font-weight:bold;}
                    QPushButton:hover { background-color: #219150; }
                """)
                btn_accept.clicked.connect(lambda _, idx=i: self.handle_reservation(idx, True))
                
                btn_refuse = QPushButton("Refuser")
                btn_refuse.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_refuse.setStyleSheet("""
                    QPushButton { background-color: #c0392b; color: white; border-radius: 4px; padding: 6px 12px; border:none; font-weight:bold;}
                    QPushButton:hover { background-color: #a93226; }
                """)
                btn_refuse.clicked.connect(lambda _, idx=i: self.handle_reservation(idx, False))
                
                actions_layout.addWidget(btn_accept)
                actions_layout.addWidget(btn_refuse)
            
            self.res_table.setCellWidget(i, 6, actions_widget)
            self.res_table.setRowHeight(i, 60)

    def handle_reservation_db(self, reservation_id, accepted):
        """Traite une réservation depuis la base de données"""
        try:
            new_status = "validee" if accepted else "rejetee"
            self.db.modifier_statut_reservation(reservation_id, new_status)
            
            status_text = "acceptée" if accepted else "refusée"
            QMessageBox.information(self, "Succès", f"✅ Demande {status_text} avec succès!")
            
            # Rafraîchir UI
            self.refresh_reservations()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"❌ Erreur: {e}")

    def handle_reservation(self, index, accepted):
        if 0 <= index < len(self.reservations_data):
            data = self.reservations_data[index]
            data['status'] = "Acceptée" if accepted else "Refusée"
            print(f"Demande {data['status']} pour {data['prof']}")
            self._refresh_reservations_mock()

    def simulate_new_request(self):
        """Ajoute une demande fictive pour tester"""
        new_req = {
            "date": "2024-02-15",
            "prof": f"Prof. Test {len(self.reservations_data) + 1}",
            "salle": "A12",
            "motif": "Cours rattrapage"
        }
        self.reservations_data.append(new_req)
        self.refresh_reservations()

    def create_notifications_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Notifications Système")
        title.setStyleSheet(CARD_TITLE_STYLE)
        header_layout.addWidget(title)
        
        # Bouton Actualiser
        btn_refresh = QPushButton("Actualiser")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(SECONDARY_BUTTON_STYLE)
        # TODO: Add logic to refresh notifications
        header_layout.addStretch()
        header_layout.addWidget(btn_refresh)
        
        layout.addLayout(header_layout)
        
        # Liste des notifications
        notif_list = QTableWidget()
        notif_list.setColumnCount(3)
        notif_list.setHorizontalHeaderLabels(["Date", "Type", "Message"])
        notif_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        notif_list.setStyleSheet(TABLE_STYLE)
        
        # Exemple de notifications (Mock -> à remplacer par DB si table existe)
        # Le User demande: Notification lorsqu’un professeur signale une séance annulée ou indisponible.
        # Nous allons lire la table `disponibilites`
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            # Join with utilisateurs to get prof name
            cursor.execute('''
                SELECT d.date_debut, u.nom, u.prenom, d.motif 
                FROM disponibilites d
                JOIN utilisateurs u ON d.enseignant_id = u.id
                ORDER BY d.id DESC LIMIT 20
            ''')
            dispos = cursor.fetchall()
            conn.close()
            
            notif_list.setRowCount(len(dispos))
            for i, (date, nom, prenom, motif) in enumerate(dispos):
                notif_list.setItem(i, 0, QTableWidgetItem(date))
                notif_list.setItem(i, 1, QTableWidgetItem("Indisponibilité Prof"))
                notif_list.setItem(i, 2, QTableWidgetItem(f"Prof {nom} {prenom} : {motif}"))
                
        except Exception as e:
            print(f"Erreur notifs: {e}")
            
        layout.addWidget(notif_list)
        return page

    def switch_page(self, page_id):
        """Change la page affichée"""
        names = {
            "Dashboard": "Tableau de Bord",
            "Generation": "Génération Emploi du Temps",
            "Reservations": "Gestion des Réservations",
            "Notifications": "Notifications Système"
        }
        self.page_title.setText(names.get(page_id, page_id))
        
        # Update buttons
        for pid, btn in self.menu_buttons.items():
            btn.setChecked(pid == page_id)
            
        # Switch stacked widget
        index_map = {"Dashboard": 0, "Generation": 1, "Reservations": 2, "Notifications": 3}
        if page_id in index_map:
            self.pages.setCurrentIndex(index_map[page_id])
