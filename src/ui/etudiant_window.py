# src/ui/etudiant_window.py
"""
Fenêtre principale de l'étudiant
Fonctionnalités : Emploi du temps groupe, Salles libres, Mises à jour
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QStackedWidget, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, QListWidget,
    QListWidgetItem, QDateEdit, QTimeEdit, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime
from PyQt6.QtGui import QIcon, QPixmap, QColor

from configUI import WINDOW_CONFIG, COLORS, FST_LOGO_IMAGE
from src.ui.styles import (
    GLOBAL_STYLE, SIDEBAR_STYLE, SIDEBAR_BUTTON_STYLE, 
    SIDEBAR_USER_INFO_STYLE, CARD_STYLE, CARD_TITLE_STYLE,
    PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE,
    TABLE_STYLE, INPUT_STYLE
)
import os

class UserWrapper:
    def __init__(self, user_tuple):
        # Structure: (id, nom, prenom, email, mot_de_passe, type_user, specialite, groupe_id, duree_max_jour, date_creation)
        self.id = user_tuple[0]
        self.nom = user_tuple[1]
        self.prenom = user_tuple[2]
        self.email = user_tuple[3]
        self.type_user = user_tuple[5] if len(user_tuple) > 5 else None
        self.specialite = user_tuple[6] if len(user_tuple) > 6 else None
        self.groupe_id = user_tuple[7] if len(user_tuple) > 7 else None

class EtudiantWindow(QWidget):
    logout_signal = pyqtSignal()
    
    def __init__(self, user, db):
        super().__init__()
        if isinstance(user, tuple):
            self.user = UserWrapper(user)
        else:
            self.user = user
            
        self.db = db
        
        self.setWindowTitle(WINDOW_CONFIG['etudiant']['title'])
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
        """Menu latéral Étudiant"""
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
        
        
            
        title = QLabel("ESPACE ÉTUDIANT")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-weight: bold; margin-top: 10px;")
        h_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Menu
        self.menu_buttons = {}
        menus = [
            ("Emploi du Temps", "Schedule"),
            ("Salles Libres", "Search"),
            ("Mises à jour", "Updates")
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
        
        # Footer - Get actual group name
        group_text = "Non assigné"
        if hasattr(self.user, 'groupe_id') and self.user.groupe_id:
            try:
                groupe = self.db.get_groupe_by_id(self.user.groupe_id)
                if groupe:
                    group_text = groupe[1] if isinstance(groupe, tuple) else groupe.get('nom', 'N/A')
            except:
                pass
                
        user_lbl = QLabel(f"{self.user.prenom} {self.user.nom}\nGroupe: {group_text}")
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
        
        self.page_title = QLabel("Emploi du Temps")
        self.page_title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {COLORS['text_dark']}; margin-bottom: 20px;")
        layout.addWidget(self.page_title)
        
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_schedule_page())
        self.pages.addWidget(self.create_search_page())
        self.pages.addWidget(self.create_updates_page())
        
        layout.addWidget(self.pages)
        self.main_layout.addWidget(self.content)

    def create_schedule_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # En-tête (Info Étudiant)
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            background-color: white; 
            border-radius: 10px; 
            padding: 15px;
            border: 1px solid #E0E0E0;
        """)
        h_layout = QHBoxLayout(header_frame)
        
        # Get groupe name
        groupe_nom = "N/A"
        if hasattr(self.user, 'groupe_id') and self.user.groupe_id:
            try:
                groupe = self.db.get_groupe_by_id(self.user.groupe_id)
                if groupe:
                    groupe_nom = groupe[1] if isinstance(groupe, tuple) else groupe.get('nom', 'N/A')
            except:
                pass
        
        # Info Étudiant
        info_str = f"""
        <div style='font-size: 16px; color: {COLORS['text_dark']};'>
            <b>Étudiant:</b> {self.user.nom} {self.user.prenom} | 
            <b>Email:</b> {self.user.email} |
            <b>Groupe:</b> {groupe_nom}
        </div>
        """
        info_label = QLabel(info_str)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        h_layout.addWidget(info_label)
        h_layout.addStretch()
        
        # Actions (Imprimer) with real export functionality
        for fmt in ["PDF", "Excel", "PNG"]:
            btn = QPushButton(f"Télécharger {fmt}")
            btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
            btn.clicked.connect(lambda _, f=fmt: self.export_timetable(f))
            h_layout.addWidget(btn)
            
        layout.addWidget(header_frame)
        
        # Table
        self.schedule_table = QTableWidget(5, 6)
        self.schedule_table.setHorizontalHeaderLabels(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"])
        time_slots = ["08:30 - 10:00", "10:15 - 11:45", "12:00 - 13:30", "13:45 - 15:15", "15:30 - 17:00"]
        self.schedule_table.setVerticalHeaderLabels(time_slots)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setStyleSheet(TABLE_STYLE)
        
        # Load Real Data
        self.load_schedule()
        
        layout.addWidget(self.schedule_table)
        return page
    
    def export_timetable(self, format_type):
        """Export the student's group timetable to the specified format"""
        if not hasattr(self.user, 'groupe_id') or not self.user.groupe_id:
            QMessageBox.warning(self, "Erreur", "Vous n'êtes associé à aucun groupe.")
            return
        
        try:
            from src.logic.timetable_export_service import TimetableExportService
            from PyQt6.QtWidgets import QFileDialog
            
            export_service = TimetableExportService(self.db)
            
            # Map format
            format_map = {"PDF": "pdf", "Excel": "excel", "PNG": "png"}
            export_format = format_map.get(format_type, "pdf")
            
            # Export
            success, filepath, error = export_service.export_group_timetable(
                self.user.groupe_id, 
                export_format
            )
            
            if success and filepath:
                QMessageBox.information(
                    self, 
                    "Export Réussi", 
                    f"Votre emploi du temps a été exporté avec succès!\n\nFichier: {filepath}"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Erreur d'Export", 
                    f"L'export a échoué: {error or 'Erreur inconnue'}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export: {str(e)}")

    def load_schedule(self):
        self.schedule_table.clearContents()
        try:
             if hasattr(self.user, 'groupe_id') and self.user.groupe_id:
                 conn = self.db.get_connection()
                 cursor = conn.cursor()
                 cursor.execute('''
                    SELECT s.date, s.heure_debut, s.titre, s.type_seance, sa.nom, u.nom
                    FROM seances s
                    LEFT JOIN salles sa ON s.salle_id = sa.id
                    LEFT JOIN utilisateurs u ON s.enseignant_id = u.id
                    WHERE s.groupe_id = ?
                 ''', (self.user.groupe_id,))
                 seances = cursor.fetchall()
                 conn.close()
                 
                 def get_row(time_str):
                    if "08" in time_str or "09" in time_str: return 0
                    if "10" in time_str or "11" in time_str: return 1
                    if "12" in time_str or "13" in time_str: return 2
                    if "14" in time_str or "15" in time_str: return 3
                    if "16" in time_str or "17" in time_str: return 4
                    return -1

                 for s in seances:
                    date_str = s[0]
                    qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                    day_idx = qdate.dayOfWeek() - 1 
                    
                    if 0 <= day_idx <= 5:
                        row = get_row(s[1])
                        if row != -1:
                            txt = f"{s[2]}\n{s[4] if s[4] else '?'}"
                            color = COLORS['primary_blue'] if s[3] == 'Cours' else COLORS['secondary_blue']
                            self.set_course(self.schedule_table, row, day_idx, s[2], s[4] if s[4] else "?", color)
        except Exception as e:
            print(f"Student schedule error: {e}")

    def set_course(self, table, row, col, subject, room, color):
        item = QLabel(f"{subject}\n{room}")
        item.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px; margin: 2px; font-weight: bold;")
        table.setCellWidget(row, col, item)

    def create_search_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Filtres
        filters_frame = QFrame()
        filters_frame.setStyleSheet(CARD_STYLE)
        f_layout = QGridLayout(filters_frame)
        
        f_layout.addWidget(QLabel("Date:"), 0, 0)
        self.search_date = QDateEdit(QDate.currentDate())
        self.search_date.setCalendarPopup(True)
        self.search_date.setStyleSheet(INPUT_STYLE)
        f_layout.addWidget(self.search_date, 0, 1)
        
        f_layout.addWidget(QLabel("Heure:"), 0, 2)
        self.search_time = QTimeEdit(QTime.currentTime())
        self.search_time.setStyleSheet(INPUT_STYLE)
        f_layout.addWidget(self.search_time, 0, 3)
        
        btn_search = QPushButton("Trouver Salles Libres")
        btn_search.setStyleSheet(SECONDARY_BUTTON_STYLE)
        btn_search.clicked.connect(self.find_available_rooms)
        f_layout.addWidget(btn_search, 1, 3)
        
        layout.addWidget(filters_frame)
        
        # Resultats
        title = QLabel("Salles Disponibles")
        title.setStyleSheet(CARD_TITLE_STYLE)
        layout.addWidget(title)
        
        self.rooms_table = QTableWidget()
        self.rooms_table.setColumnCount(4)
        self.rooms_table.setHorizontalHeaderLabels(["Nom", "Type", "Capacité", "État"])
        self.rooms_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rooms_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.rooms_table)
        
        return page

    def find_available_rooms(self):
        date_Val = self.search_date.date().toString("yyyy-MM-dd")
        time_Val = self.search_time.time().toString("HH:mm")
        
        # 1. Get all rooms
        try:
             all_rooms = self.db.get_toutes_salles()
             conn = self.db.get_connection()
             cursor = conn.cursor()
             
             # 2. Get occupied rooms
             query = """
                SELECT DISTINCT salle_id FROM seances 
                WHERE date = ? 
                AND ? BETWEEN heure_debut AND heure_fin
             """
             cursor.execute(query, (date_Val, time_Val))
             occupied_ids = [row[0] for row in cursor.fetchall()]
             conn.close()
             
             available = [r for r in all_rooms if r[0] not in occupied_ids]
             
             self.rooms_table.setRowCount(len(available))
             for i, r in enumerate(available):
                 self.rooms_table.setItem(i, 0, QTableWidgetItem(r[1]))
                 self.rooms_table.setItem(i, 1, QTableWidgetItem(r[3]))
                 self.rooms_table.setItem(i, 2, QTableWidgetItem(str(r[2])))
                 item_state = QTableWidgetItem("LIBRE")
                 item_state.setForeground(QColor("green"))
                 self.rooms_table.setItem(i, 3, item_state)
                 
        except Exception as e:
            print(f"Room search error: {e}")

    def create_updates_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Mes Notifications")
        title.setStyleSheet(CARD_TITLE_STYLE)
        layout.addWidget(title)
        
        notif_list = QTableWidget()
        notif_list.setColumnCount(2)
        notif_list.setHorizontalHeaderLabels(["Date", "Message"])
        notif_list.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        notif_list.setStyleSheet(TABLE_STYLE)
        
        # Fetch real notifications (Disponibilites from Professors)
        try:
             conn = self.db.get_connection()
             cursor = conn.cursor()
             # Show cancellations/unavailabilities from ANY professor? 
             # Or only professors teaching to this group?
             # For simplicity, show all recent unavailabilities (Global announcements)
             cursor.execute('''
                SELECT d.date_debut, u.nom, u.prenom, d.motif
                FROM disponibilites d
                JOIN utilisateurs u ON d.enseignant_id = u.id
                ORDER BY d.id DESC LIMIT 20
             ''')
             rows = cursor.fetchall()
             conn.close()
             
             notif_list.setRowCount(len(rows))
             for i, (date, nom, prenom, motif) in enumerate(rows):
                 notif_list.setItem(i, 0, QTableWidgetItem(date))
                 msg = f"Prof. {nom} {prenom} : {motif}"
                 notif_list.setItem(i, 1, QTableWidgetItem(msg))
                 
        except Exception as e:
            pass

        layout.addWidget(notif_list)
        return page

    def switch_page(self, page_id):
        titles = {
            "Schedule": "Mon Emploi du Temps",
            "Search": "Trouver une Salle",
            "Updates": "Actualités & Modifications"
        }
        self.page_title.setText(titles.get(page_id, page_id))
        
        mapping = {"Schedule": 0, "Search": 1, "Updates": 2}
        if page_id in mapping:
            self.pages.setCurrentIndex(mapping[page_id])
            
        for pid, btn in self.menu_buttons.items():
            btn.setChecked(pid == page_id)
