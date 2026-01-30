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
        # Structure: (id, nom, prenom, email, mot_de_passe, type_user, specialite, groupe_id, duree_max_jour, date_creation)
        self.id = user_tuple[0]
        self.nom = user_tuple[1]
        self.prenom = user_tuple[2]
        self.email = user_tuple[3]
        self.type_user = user_tuple[5] if len(user_tuple) > 5 else None
        self.specialite = user_tuple[6] if len(user_tuple) > 6 else None
        self.groupe_id = user_tuple[7] if len(user_tuple) > 7 else None
        self.duree_max_jour = user_tuple[8] if len(user_tuple) > 8 else 480

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
        
        # En-tête avec infos enseignant
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            background-color: white; 
            border-radius: 10px; 
            padding: 15px;
            border: 1px solid #E0E0E0;
        """)
        h_layout = QHBoxLayout(header_frame)
        
        # Info Enseignant
        specialite = getattr(self.user, 'specialite', None) or "N/A"
        info_str = f"""
        <div style='font-size: 16px; color: {COLORS['text_dark']};'>
            <b>Enseignant:</b> {self.user.prenom} {self.user.nom} | 
            <b>Spécialité:</b> {specialite}
        </div>
        """
        info_label = QLabel(info_str)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        h_layout.addWidget(info_label)
        h_layout.addStretch()
        
        # Actions (Export) with real functionality
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
        """Export the teacher's personal timetable to the specified format"""
        try:
            from src.logic.timetable_export_service import TimetableExportService
            
            export_service = TimetableExportService(self.db)
            
            # Map format
            format_map = {"PDF": "pdf", "Excel": "excel", "PNG": "png"}
            export_format = format_map.get(format_type, "pdf")
            
            # Export
            success, filepath, error = export_service.export_teacher_timetable(
                self.user.id, 
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
        """
        Page for professors to request room reservation (Rattrapage/Reprogrammation).
        Requests go to 'pending' status and require Admin approval.
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Info Banner
        info_banner = QLabel(
            "⚠️ Les demandes de réservation sont soumises à l'approbation de l'administrateur. "
            "Vous recevrez une notification une fois votre demande traitée."
        )
        info_banner.setStyleSheet(
            f"background-color: #FFF3CD; color: #856404; padding: 10px; "
            f"border-radius: 5px; border: 1px solid #FFEEBA; font-size: 13px;"
        )
        info_banner.setWordWrap(True)
        layout.addWidget(info_banner)
        
        # Main Form Frame
        form_frame = QFrame()
        form_frame.setStyleSheet(CARD_STYLE)
        form_layout = QVBoxLayout(form_frame)
        
        form_title = QLabel("Nouvelle Demande de Réservation")
        form_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_dark']}; margin-bottom: 10px;")
        form_layout.addWidget(form_title)
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Date
        grid.addWidget(QLabel("Date:"), 0, 0)
        self.new_res_date = QDateEdit(QDate.currentDate().addDays(1))
        self.new_res_date.setCalendarPopup(True)
        self.new_res_date.setMinimumDate(QDate.currentDate())
        self.new_res_date.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_date, 0, 1)
        
        # Heure Début
        grid.addWidget(QLabel("Heure Début:"), 0, 2)
        self.new_res_time = QTimeEdit(QTime(8, 30))
        self.new_res_time.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_time, 0, 3)
        
        # Heure Fin
        grid.addWidget(QLabel("Heure Fin:"), 0, 4)
        self.new_res_time_end = QTimeEdit(QTime(10, 0))
        self.new_res_time_end.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_time_end, 0, 5)
        
        # Groupe
        grid.addWidget(QLabel("Groupe:"), 1, 0)
        self.new_res_groupe = QComboBox()
        self.new_res_groupe.setStyleSheet(INPUT_STYLE)
        self.load_groupes_combobox()
        grid.addWidget(self.new_res_groupe, 1, 1)
        
        # Salle
        grid.addWidget(QLabel("Salle Souhaitée:"), 1, 2)
        self.new_res_salle = QComboBox()
        self.new_res_salle.setStyleSheet(INPUT_STYLE)
        self.load_salles_combobox()
        grid.addWidget(self.new_res_salle, 1, 3, 1, 2)
        
        # Type de demande
        grid.addWidget(QLabel("Type:"), 2, 0)
        self.new_res_type = QComboBox()
        self.new_res_type.addItems(["Rattrapage", "Reprogrammation", "Examen", "Autre"])
        self.new_res_type.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.new_res_type, 2, 1)
        
        # Motif
        grid.addWidget(QLabel("Motif / Détails:"), 2, 2)
        self.new_res_motif = QTextEdit()
        self.new_res_motif.setStyleSheet(INPUT_STYLE)
        self.new_res_motif.setMaximumHeight(60)
        self.new_res_motif.setPlaceholderText("Décrivez le motif de votre demande...")
        grid.addWidget(self.new_res_motif, 2, 3, 1, 3)
        
        form_layout.addLayout(grid)
        layout.addWidget(form_frame)
        
        # Bouton Soumettre
        btn_layout = QHBoxLayout()
        btn_reserve = QPushButton("Soumettre la Demande")
        btn_reserve.setStyleSheet(PRIMARY_BUTTON_STYLE)
        btn_reserve.clicked.connect(self.submit_reservation_request)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_reserve)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return page
    
    def load_groupes_combobox(self):
        """Load groups into combobox"""
        try:
            groupes = self.db.get_tous_groupes()
            self.new_res_groupe.clear()
            for g in groupes:
                # g: id, nom, effectif, filiere_id
                self.new_res_groupe.addItem(g[1], g[0])  # Display nom, store id
        except Exception as e:
            print(f"Error loading groups: {e}")
            self.new_res_groupe.addItem("Aucun groupe", 0)
    
    def load_salles_combobox(self):
        """Load rooms into combobox"""
        try:
            salles = self.db.get_toutes_salles()
            self.new_res_salle.clear()
            for s in salles:
                # s: id, nom, capacite, type_salle, equipements
                self.new_res_salle.addItem(f"{s[1]} ({s[3]}, {s[2]} places)", s[0])
        except Exception as e:
            print(f"Error loading rooms: {e}")
            self.new_res_salle.addItem("Aucune salle", 0)
    
    def submit_reservation_request(self):
        """
        Submit a reservation request with 'pending' status.
        The request requires Admin approval before confirmation.
        """
        date = self.new_res_date.date().toString("yyyy-MM-dd")
        h_debut = self.new_res_time.time().toString("HH:mm")
        h_fin = self.new_res_time_end.time().toString("HH:mm")
        groupe_id = self.new_res_groupe.currentData()
        salle_id = self.new_res_salle.currentData()
        type_demande = self.new_res_type.currentText()
        motif = self.new_res_motif.toPlainText().strip()
        
        # Validation
        if self.new_res_time.time() >= self.new_res_time_end.time():
            QMessageBox.warning(self, "Erreur", "L'heure de fin doit être après l'heure de début.")
            return
        
        if not groupe_id or groupe_id == 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un groupe.")
            return
        
        if not salle_id or salle_id == 0:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une salle.")
            return
        
        if not motif:
            motif = type_demande
        else:
            motif = f"{type_demande}: {motif}"
        
        try:
            # Create request with 'pending' status
            demande_id = self.db.creer_demande_reservation(
                enseignant_id=self.user.id,
                salle_id=salle_id,
                groupe_id=groupe_id,
                date=date,
                heure_debut=h_debut,
                heure_fin=h_fin,
                type_demande=type_demande,
                motif=motif
            )
            
            if demande_id:
                QMessageBox.information(
                    self, 
                    "Demande Soumise",
                    f"Votre demande de réservation a été soumise avec succès.\n\n"
                    f"📋 Référence: #{demande_id}\n"
                    f"📅 Date: {date}\n"
                    f"⏰ Horaire: {h_debut} - {h_fin}\n"
                    f"📍 Salle: {self.new_res_salle.currentText()}\n\n"
                    f"⏳ Statut: En attente d'approbation\n\n"
                    f"Vous recevrez une notification lorsque l'administrateur "
                    f"aura traité votre demande."
                )
                # Clear form
                self.new_res_motif.clear()
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de la soumission de la demande.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")

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
        """
        Save teacher unavailability (absence).
        This requires NO APPROVAL - just immediate reporting and notifications.
        
        Actions:
        1. Save the absence in database
        2. Immediately notify Admin (for records)
        3. Immediately notify Students (class is off)
        """
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
            
            # 1. Save absence in database
            try:
                cursor.execute('''
                   INSERT INTO disponibilites (enseignant_id, date_debut, date_fin, motif) 
                   VALUES (?, ?, ?, ?)
                ''', (self.user.id, d_start, d_end, final_motif))
            except Exception:
                cursor.execute('''
                   INSERT INTO disponibilites (enseignant_id, date, motif) 
                   VALUES (?, ?, ?)
                ''', (self.user.id, d_start, final_motif))
                 
            conn.commit()
            conn.close()
            
            # ═══════════════════════════════════════════════════════════
            # 2. IMMEDIATE NOTIFICATIONS (No approval required)
            # ═══════════════════════════════════════════════════════════
            
            from src.services_notification import NotificationService
            notif_service = NotificationService(self.db)
            
            enseignant_nom = f"{self.user.prenom} {self.user.nom}"
            
            # 2a. Notify all Admins (for records)
            nb_admins = notif_service.notifier_admins(
                type_notification='info',
                titre='Absence Enseignant Signalée',
                message=f"L'enseignant {enseignant_nom} a signalé une absence.\n"
                        f"Période: {d_start} - {d_end}\n"
                        f"Motif: {reason or 'Non spécifié'}"
            )
            
            # 2b. Notify Students of affected courses
            # Find sessions in this period and notify their groups
            seances_affectees = self.db.get_seances_enseignant_periode(
                self.user.id, d_start, d_end
            )
            
            groupes_notifies = set()
            nb_etudiants_notifies = 0
            
            for seance in seances_affectees:
                groupe_id = seance[8] if len(seance) > 8 else None
                
                if groupe_id and groupe_id not in groupes_notifies:
                    nb_etudiants, _ = notif_service.notifier_groupe(
                        groupe_id=groupe_id,
                        type_notification='annulation',
                        titre='Cours Annulé',
                        message=f"Le cours de {seance[1]} avec {enseignant_nom} est annulé.\n"
                                f"Date: {seance[3]}\n"
                                f"Motif: {reason or 'Absence enseignant'}"
                    )
                    nb_etudiants_notifies += nb_etudiants
                    groupes_notifies.add(groupe_id)
            
            # Success message with notification summary
            success_msg = "Votre indisponibilité a été enregistrée avec succès.\n\n"
            success_msg += "Notifications envoyées:\n"
            success_msg += f"• {nb_admins} administrateur(s) notifié(s)\n"
            success_msg += f"• {nb_etudiants_notifies} étudiant(s) notifié(s) "
            success_msg += f"({len(groupes_notifies)} groupe(s) affecté(s))"
            
            QMessageBox.information(self, "Succès", success_msg)
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
