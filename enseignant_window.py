# src/ui/enseignant_window.py
"""
Fenêtre principale de l'enseignant
Fonctionnalités : Emploi du temps, Réservations, Recherche Salles, Indisponibilités
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QStackedWidget, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, QDateEdit,
    QTimeEdit, QTextEdit, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor

from configUI import WINDOW_CONFIG, COLORS, FST_LOGO_IMAGE
from src.ui.styles import (
    GLOBAL_STYLE, SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE, 
    SIDEBAR_USER_INFO_STYLE, CARD_STYLE, CARD_TITLE_STYLE,
    PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    TABLE_STYLE, INPUT_STYLE, DANGER_BUTTON_STYLE
)

class UserWrapper:
    def __init__(self, user_tuple):
        self.id = user_tuple[0]
        self.nom = user_tuple[1]
        self.prenom = user_tuple[2]
        self.email = user_tuple[3]
        # Map other fields if necessary

class EnseignantWindow(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, user, db):
        super().__init__()
        # Handle tuple vs object
        if isinstance(user, tuple):
            self.user = UserWrapper(user)
        else:
            self.user = user
            
        self.db = db
        
        self.setWindowTitle(WINDOW_CONFIG['enseignant']['title'])
        self.setMinimumSize(1024, 768)
        self.showMaximized()
        self.setStyleSheet(GLOBAL_STYLE)
        
        # Layout principal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.create_sidebar()
        self.create_content_area()
        self.switch_page("Emploi du Temps")

    def create_sidebar(self):
        """Menu latéral Enseignant"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 20)
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"background-color: {COLORS['primary_blue']};")
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(20, 30, 20, 30)
        

            
        title = QLabel("ESPACE ENSEIGNANT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-weight: bold; margin-top: 10px;")
        h_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Menu
        self.menu_buttons = {}
        menus = [
            ("Emploi du Temps", "Schedule"),
            ("Réserver une séance", "Reservation"), # Renamed from SearchSession
            ("Indisponibilités", "Unavailability")
        ]
        
        for label, pid in menus:
            btn = QPushButton(f"  {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(SIDEBAR_BUTTON_STYLE)
            btn.clicked.connect(lambda _, p=pid: self.switch_page(p))
            layout.addWidget(btn)
            self.menu_buttons[pid] = btn
            
        layout.addStretch()
        
        # Footer
        user_lbl = QLabel(f"Prof. {self.user.nom if self.user else 'Enseignant'}")
        user_lbl.setStyleSheet(SIDEBAR_USER_INFO_STYLE)
        user_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(user_lbl)
        
        logout = QPushButton("Déconnexion")
        logout.setCursor(Qt.CursorShape.PointingHandCursor)
        logout.setStyleSheet("""
            QPushButton {
                background: transparent; color: #e74c3c; border: 1px solid #e74c3c;
                border-radius: 5px; padding: 8px; margin: 15px; font-weight: bold;
            }
            QPushButton:hover { background: #e74c3c; color: white; }
        """)
        logout.clicked.connect(self.logout_signal.emit)
        layout.addWidget(logout)
        
        self.main_layout.addWidget(self.sidebar)

    def create_content_area(self):
        self.content = QFrame()
        self.content.setStyleSheet(f"background-color: {COLORS['bg_light']};")
        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.page_title = QLabel("Mon Emploi du Temps")
        self.page_title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['text_dark']}; margin-bottom: 20px;")
        layout.addWidget(self.page_title)
        
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_schedule_page())
        self.pages.addWidget(self.create_reservation_page()) 
        self.pages.addWidget(self.create_unavailability_page())
        # Removed create_search_page (Room Search)
        
        layout.addWidget(self.pages)
        self.main_layout.addWidget(self.content)

    def create_schedule_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Actions (Imprimer)
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        for fmt in ["PDF", "Excel", "Image"]:
            btn = QPushButton(f"Imprimer {fmt}")
            btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
            btn.clicked.connect(lambda _, f=fmt: QMessageBox.information(self, "Export", f"Export {f} lancé..."))
            actions_layout.addWidget(btn)
            
        layout.addLayout(actions_layout)
        
        # Table
        self.schedule_table = QTableWidget(5, 6)
        self.schedule_table.setHorizontalHeaderLabels(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"])
        time_slots = ["08:30 - 10:00", "10:15 - 11:45", "12:00 - 13:30", "13:45 - 15:15", "15:30 - 17:00"]
        self.schedule_table.setVerticalHeaderLabels(time_slots) # Using standard slots roughly
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setStyleSheet(TABLE_STYLE)
        
        # Load Real Data
        self.load_schedule()
        
        layout.addWidget(self.schedule_table)
        return page

    def load_schedule(self):
        """Charge l'emploi du temps de l'enseignant"""
        self.schedule_table.clearContents()
        
        # Mapping jours/heures
        days_map = {'Lundi': 0, 'Mardi': 1, 'Mercredi': 2, 'Jeudi': 3, 'Vendredi': 4, 'Samedi': 5}
        # Time mapping (Simplified)
        def get_row(time_str):
            if "08" in time_str or "09" in time_str: return 0
            if "10" in time_str or "11" in time_str: return 1
            if "12" in time_str or "13" in time_str: return 2
            if "14" in time_str or "15" in time_str: return 3
            if "16" in time_str or "17" in time_str: return 4
            return -1

        try:
            # Assuming get_seances_by_enseignant exists in DB
            seances = self.db.get_seances_by_enseignant(self.user.id)
            for s in seances:
                # s: id, titre, type, date, h_debut, h_fin, salle_id...
                # We need day of week from date
                date_str = s[3]
                qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                day_idx = qdate.dayOfWeek() - 1 # 1=Mon, 7=Sun
                
                if 0 <= day_idx <= 5:
                    row = get_row(s[4]) # h_debut
                    if row != -1:
                        # Fetch Room Name
                        salle_name = "Salle ?"
                        if s[6]: # salle_id
                            # Need to fetch salle name. ideally JOIN in get_seances_by_enseignant
                            # Hack: do query or cache.
                            pass
                        
                        txt = f"{s[1]}\n{s[2]}"
                        self.set_course(self.schedule_table, row, day_idx, s[1], s[2], COLORS['primary_blue'])
                        
        except Exception as e:
            print(f"Schedule load error: {e}")

    def set_course(self, table, row, col, subject, room, color):
        item = QLabel(f"{subject}\n{room}")
        item.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px; margin: 2px; font-weight: bold;")
        table.setCellWidget(row, col, item)

    def create_reservation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # 2 Options: Choisir ou Créer
        
        # =========================
        # Option A : Séance existante
        # =========================
        opt1_frame = QFrame()
        opt1_frame.setStyleSheet(CARD_STYLE)
        opt1_layout = QVBoxLayout(opt1_frame)

        opt1_layout.addWidget(QLabel("Option A : Pour une séance existante"))

        cb_layout = QHBoxLayout()
        cb_layout.addWidget(QLabel("Groupe:"))
        self.res_group_cb = QComboBox()
        self.res_group_cb.addItem("G1 - Génie Info")
        self.res_group_cb.setStyleSheet(INPUT_STYLE)
        cb_layout.addWidget(self.res_group_cb)

        cb_layout.addWidget(QLabel("Séance:"))
        self.res_session_cb = QComboBox()
        self.res_session_cb.addItem("Lundi 08:30 - Java")
        self.res_session_cb.setStyleSheet(INPUT_STYLE)
        cb_layout.addWidget(self.res_session_cb)

        opt1_layout.addLayout(cb_layout)

        # Bouton Option A
        btnA_layout = QHBoxLayout()
        btnA = QPushButton("Envoyer Demande")
        btnA.setStyleSheet(PRIMARY_BUTTON_STYLE)
        btnA.clicked.connect(
            lambda: QMessageBox.information(
                self,
                "Réservation",
                "Demande envoyée pour une séance existante."
            )
        )
        btnA_layout.addStretch()
        btnA_layout.addWidget(btnA)
        opt1_layout.addLayout(btnA_layout)

        layout.addWidget(opt1_frame)

        # =========================
        # Option B : Créer séance
        # =========================
        opt2_frame = QFrame()
        opt2_frame.setStyleSheet(CARD_STYLE)
        opt2_layout = QVBoxLayout(opt2_frame)

        opt2_layout.addWidget(QLabel("Option B : Créer une nouvelle séance"))

        grid = QGridLayout()

        grid.addWidget(QLabel("Date:"), 0, 0)
        self.new_res_date = QDateEdit(QDate.currentDate())
        self.new_res_date.setCalendarPopup(True)
        self.new_res_date.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_date, 0, 1)

        grid.addWidget(QLabel("Heure:"), 0, 2)
        self.new_res_time = QTimeEdit(QTime(8, 30))
        self.new_res_time.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_time, 0, 3)

        grid.addWidget(QLabel("Matière:"), 1, 0)
        self.new_res_subject = QComboBox()
        self.new_res_subject.addItems(["Java", "UML", "Anglais"])
        self.new_res_subject.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_subject, 1, 1)

        grid.addWidget(QLabel("Type:"), 1, 2)
        self.new_res_type = QComboBox()
        self.new_res_type.addItems(
            ["Cours", "TP", "TD", "Examen", "Rattrapage"]
        )
        self.new_res_type.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_type, 1, 3)

        opt2_layout.addLayout(grid)

        # Bouton Option B
        btnB_layout = QHBoxLayout()
        btnB = QPushButton("Envoyer Demande")
        btnB.setStyleSheet(PRIMARY_BUTTON_STYLE)
        btnB.clicked.connect(
            lambda: QMessageBox.information(
                self,
                "Réservation",
                "Demande envoyée pour une nouvelle séance."
            )
        )
        btnB_layout.addStretch()
        btnB_layout.addWidget(btnB)
        opt2_layout.addLayout(btnB_layout)

        layout.addWidget(opt2_frame)

        layout.addStretch()
        return page
    # Removed perform_session_search


    # Old Search Page Removed


    def create_unavailability_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        info = QLabel("Signaler une absence ou indisponibilité")
        info.setStyleSheet(CARD_TITLE_STYLE)
        layout.addWidget(info)
        
        # Formulaire
        form_frame = QFrame()
        form_frame.setStyleSheet(CARD_STYLE)
        form_layout = QGridLayout(form_frame)
        form_layout.setSpacing(20)
        
        # Date Début
        form_layout.addWidget(QLabel("Date Début:"), 0, 0)
        self.ab_date_start = QDateEdit(QDate.currentDate())
        self.ab_date_start.setCalendarPopup(True)
        self.ab_date_start.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.ab_date_start, 0, 1)

        # Date Fin (Optional, for range)
        form_layout.addWidget(QLabel("Date Fin (Optionnel):"), 0, 2)
        self.ab_date_end = QDateEdit(QDate.currentDate())
        self.ab_date_end.setCalendarPopup(True)
        self.ab_date_end.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.ab_date_end, 0, 3)
        
        # Checkbox Journée Entière
        from PyQt6.QtWidgets import QCheckBox
        self.chk_full_day = QCheckBox("Journée Entière")
        self.chk_full_day.setStyleSheet("font-size: 14px;")
        self.chk_full_day.setChecked(True)
        form_layout.addWidget(self.chk_full_day, 1, 0, 1, 2)
        
        # Heure Début / Fin (Hidden if full day)
        self.lbl_h_start = QLabel("Heure Début:")
        self.ab_time_start = QTimeEdit(QTime(8, 30))
        self.ab_time_start.setStyleSheet(INPUT_STYLE)
        
        self.lbl_h_end = QLabel("Heure Fin:")
        self.ab_time_end = QTimeEdit(QTime(18, 30))
        self.ab_time_end.setStyleSheet(INPUT_STYLE)
        
        form_layout.addWidget(self.lbl_h_start, 2, 0)
        form_layout.addWidget(self.ab_time_start, 2, 1)
        form_layout.addWidget(self.lbl_h_end, 2, 2)
        form_layout.addWidget(self.ab_time_end, 2, 3)
        
        # Logic visibility
        def toggle_time():
            visible = not self.chk_full_day.isChecked()
            self.lbl_h_start.setVisible(visible)
            self.ab_time_start.setVisible(visible)
            self.lbl_h_end.setVisible(visible)
            self.ab_time_end.setVisible(visible)
            
        self.chk_full_day.toggled.connect(toggle_time)
        toggle_time() # Init
        
        form_layout.addWidget(QLabel("Motif:"), 3, 0)
        self.ab_reason = QTextEdit()
        self.ab_reason.setStyleSheet(INPUT_STYLE)
        self.ab_reason.setMaximumHeight(80)
        form_layout.addWidget(self.ab_reason, 3, 1, 1, 3)
        
        btn_submit = QPushButton("Signaler Indisponibilité")
        btn_submit.setStyleSheet(DANGER_BUTTON_STYLE)
        btn_submit.clicked.connect(self.save_unavailability)
        form_layout.addWidget(btn_submit, 4, 1, 1, 2)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        return page

    def save_unavailability(self):
        d_start = self.ab_date_start.date().toString("yyyy-MM-dd")
        d_end = self.ab_date_end.date().toString("yyyy-MM-dd") 
        reason = self.ab_reason.toPlainText()
        
        # Validation Date
        if self.ab_date_start.date() > self.ab_date_end.date():
             QMessageBox.warning(self, "Erreur", "La date de fin doit être postérieure à la date de début.")
             return

        # Construction du motif avec les périodes
        full_msg = reason
        period_msg = ""
        
        # Période de dates
        if d_start != d_end:
            period_msg = f"[Période: {d_start} -> {d_end}]"
        else:
            period_msg = f"[Date: {d_start}]"

        # Période d'heures
        if not self.chk_full_day.isChecked():
            t_start = self.ab_time_start.time().toString("HH:mm")
            t_end = self.ab_time_end.time().toString("HH:mm")
            
            if self.ab_time_start.time() >= self.ab_time_end.time():
                QMessageBox.warning(self, "Erreur", "L'heure de fin doit être postérieure à l'heure de début.")
                return
                
            period_msg += f" [Heure: {t_start} -> {t_end}]"
        else:
            period_msg += " [Journée entière]"
            
        final_motif = f"{period_msg} {full_msg}"
            
        try:
             conn = self.db.get_connection()
             cursor = conn.cursor()
             
             # Tentative d'insertion avec gestion adaptative des colonnes
             try:
                 # Le schéma standard a date_debut ET date_fin (NOT NULL)
                 cursor.execute('''
                    INSERT INTO disponibilites (enseignant_id, date_debut, date_fin, motif) 
                    VALUES (?, ?, ?, ?)
                 ''', (self.user.id, d_start, d_end, final_motif))
             except Exception as e:
                 # Fallback sur 'date' si la colonne 'date_debut' n'existe pas (ancienne version)
                 # Note: Si date_fin manque, cela echouera aussi si on essaie d'inserer date_fin.
                 # On suppose ici un fallback simple.
                 cursor.execute('''
                    INSERT INTO disponibilites (enseignant_id, date, motif) 
                    VALUES (?, ?, ?)
                 ''', (self.user.id, d_start, final_motif))
                 
             conn.commit()
             conn.close()
             QMessageBox.information(self, "Succès", "Votre indisponibilité a été enregistrée avec succès.")
             self.ab_reason.clear()
        except Exception as e:
             QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement: {e}")

    def switch_page(self, page_id):
        titles = {
            "Schedule": "Mon Emploi du Temps",
            "Reservation": "Réserver une Salle",
            # "Search": "Rechercher une Salle Vide", # Removed
            "Unavailability": "Mes Indisponibilités"
        }
        self.page_title.setText(titles.get(page_id, page_id))
        
        # Correct mapping based on create_content_area order:
        # 0: Schedule, 1: Reservation, 2: Unavailability
        mapping = {"Schedule": 0, "Reservation": 1, "Unavailability": 2}
        
        if page_id in mapping:
            self.pages.setCurrentIndex(mapping[page_id])
            
        for pid, btn in self.menu_buttons.items():
            btn.setChecked(pid == page_id)

import sys
import os
