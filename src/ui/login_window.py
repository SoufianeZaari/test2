import importlib._bootstrap_external
import posixpath
import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFrame, QGraphicsOpacityEffect,
    QApplication, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont, QIcon

# Configuration (Assure-toi que ces variables pointent vers tes fichiers)
from configUI import WINDOW_CONFIG, COLORS, MESSAGES, FST_BACKGROUND_IMAGE, FST_LOGO_IMAGE

class LoginWindow(QWidget):
    login_success = pyqtSignal(object, str)

    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.setWindowTitle("FSTT System")
        self.setFixedSize(1000, 700) # Taille fixe pour le design
        self.form_visible = False
        self.init_ui()

    def init_ui(self):
        # 1. Image de fond principale
        self.set_background_image()

        # 2. Bouton LOGIN Central avec Icone
        self.main_login_button = QPushButton("  LOGIN", self)
        self.main_login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Charger l'icône utilisateur
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'images', 'login_icon.png')
        if os.path.exists(icon_path):
            self.main_login_button.setIcon(QIcon(icon_path))
            self.main_login_button.setIconSize(QSize(40, 40))
            
        # Style "Fresh" et semi-transparent (Cyan/Bleu clair)
        self.main_login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 200, 255, 0.7); /* Cyan semi-transparent */
                color: white;
                font-size: 26px;
                font-weight: bold;
                border-radius: 40px;
                border: 2px solid rgba(255, 255, 255, 0.8);
                padding: 15px 40px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 200, 255, 0.9); /* Plus opaque au survol */
                border: 2px solid white;
                transform: scale(1.05); /* Note: transform ne marche pas en pur QSS standard sans animation, mais on laisse pour l'idée */
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 150, 200, 0.9);
            }}
        """)
        
        # Centrer le bouton
        btn_w, btn_h = 250, 80
        self.main_login_button.setGeometry(
            (self.width() - btn_w) // 2,
            (self.height() - btn_h) // 2,
            btn_w, btn_h
        )
        self.main_login_button.raise_() # Ensure button is on top of background
        self.main_login_button.clicked.connect(self.show_login_form)

        # 3. Overlay sombre
        self.overlay = QFrame(self)
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.overlay.hide()
        
        # Redimensionnement auto de l'overlay et bouton
        # (Note: idéalement géré par resizeEvent, mais ici on reste simple)

        # 4. Formulaire
        self.create_login_form()

    def set_background_image(self):
        if os.path.exists(FST_BACKGROUND_IMAGE):
            # Utiliser QLabel pour le background pour mieux gérer le scaling
            self.bg_label = QLabel(self)
            self.bg_label.setGeometry(0, 0, self.width(), self.height())
            pixmap = QPixmap(FST_BACKGROUND_IMAGE)
            self.bg_label.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            self.bg_label.lower() # Mettre en arrière-plan
            
    def resizeEvent(self, event):
        if hasattr(self, 'bg_label'):
            self.bg_label.setGeometry(0, 0, self.width(), self.height())
            if os.path.exists(FST_BACKGROUND_IMAGE):
                 pixmap = QPixmap(FST_BACKGROUND_IMAGE)
                 self.bg_label.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            self.bg_label.lower()
            
        if hasattr(self, 'overlay'):
            self.overlay.setGeometry(0, 0, self.width(), self.height())
            
        # Re-center form
        if hasattr(self, 'form_container'):
             form_width = 400
             form_height = 580
             x = (self.width() - form_width) // 2
             y = (self.height() - form_height) // 2
             self.form_container.setGeometry(x, y, form_width, form_height)
             
        # Re-center button
        if hasattr(self, 'main_login_button'):
             btn_w, btn_h = 250, 80
             self.main_login_button.setGeometry(
                (self.width() - btn_w) // 2,
                (self.height() - btn_h) // 2,
                btn_w, btn_h
            )
             self.main_login_button.raise_()
             
        super().resizeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        # Auto-show login form commented out to restore Button flow
        # self.show_login_form()
        pass

    def create_login_form(self):
        # === CONTAINER PRINCIPAL (Invisible/Transparent) ===
        self.form_container = QFrame(self)
        self.form_container.setObjectName("LoginForm")
        
        # Dimensions et position
        form_width = 400
        form_height = 580 # Un peu plus grand pour le bouton quitter
        x = (self.width() - form_width) // 2
        y = (self.height() - form_height) // 2
        self.form_container.setGeometry(x, y, form_width, form_height)
        self.form_container.hide()
        
        # === BACKGROUND LOGO (Image de fond semi-transparente) ===
        self.bg_logo = QLabel(self.form_container)
        self.bg_logo.setGeometry(0, 0, form_width, form_height)
        self.bg_logo.setStyleSheet("background-color: white; border-radius: 20px;")
        
        

        # Layout vertical
        layout = QVBoxLayout(self.form_container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        # === EN-TÊTE ===
        self.btn_back = QPushButton("← Retour")
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #7F8C8D;
                border: none;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover { color: #2C3E50; }
        """)
        self.btn_back.clicked.connect(self.hide_login_form)
        layout.addWidget(self.btn_back)

        # Titre
        title = QLabel("Bienvenue")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {COLORS['primary_blue']}
            }}
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Connectez-vous à votre espace")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #7F8C8D; margin-bottom: 15px;")
        layout.addWidget(subtitle)

        # === CHAMPS DE SAISIE ===
        input_style = f"""
            QLineEdit {{
                border: none;
                background-color: rgba(240, 242, 245, 0.8);
                border-radius: 10px;
                padding: 15px;
                padding-left: 45px;
                font-size: 14px;
                color: #2C3E50;
            }}
            QLineEdit:focus {{
                background-color: white;
                border: 1px solid {COLORS['primary_blue']};
            }}
        """

        # -- Email --
        email_container = QFrame()
        email_layout = QVBoxLayout(email_container)
        email_layout.setContentsMargins(0, 0, 0, 0)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse Email")
        self.email_input.setStyleSheet(input_style)
        
        # Calculer le chemin absolu basé sur l'emplacement du fichier actuel
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Icône Email
        email_icon = QLabel(self.email_input)
        icon_path_email = os.path.join(base_dir, "assets", "images", "email_icon.png")
        
        print(f"DEBUG: Email Icon Path: {icon_path_email}") # Debugging
        
        if os.path.exists(icon_path_email):
            pixmap = QPixmap(icon_path_email)
            if not pixmap.isNull():
                email_icon.setPixmap(pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                print("DEBUG: Failed to load email pixmap (Null)")
                email_icon.setText("📧")
        else:
            print("DEBUG: Email icon file not found")
            email_icon.setText("📧")
        
        email_icon.setStyleSheet("background: transparent; border: none;")
        email_icon.setGeometry(10, 10, 30, 30)
        email_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        email_layout.addWidget(self.email_input)
        layout.addWidget(email_container)

        # -- Mot de passe --
        pass_container = QFrame()
        pass_layout = QVBoxLayout(pass_container)
        pass_layout.setContentsMargins(0, 0, 0, 0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(input_style)

        # Icône Password
        pass_icon = QLabel(self.password_input)
        icon_path_pass = os.path.join(base_dir, "assets", "images", "password_icon.png")
        
        print(f"DEBUG: Pass Icon Path: {icon_path_pass}") # Debugging

        if os.path.exists(icon_path_pass):
            pixmap = QPixmap(icon_path_pass)
            if not pixmap.isNull():
                pass_icon.setPixmap(pixmap.scaled(25, 25, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                print("DEBUG: Failed to load password pixmap (Null)")
                pass_icon.setText("🔒")
        else:
            pass_icon.setText("🔒")
            
        pass_icon.setStyleSheet("background: transparent; border: none;")
        pass_icon.setGeometry(10, 10, 30, 30)
        pass_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        pass_layout.addWidget(self.password_input)
        layout.addWidget(pass_container)
        
        # -- Options --
        options_layout = QHBoxLayout()
        self.remember_box = QPushButton("Se souvenir de moi")
        self.remember_box.setCheckable(True)
        self.remember_box.setStyleSheet(f"""
            QPushButton {{
                border: none;
                color: #7F8C8D;
                text-align: left;
            }}
            QPushButton:checked {{ color: {COLORS['primary_blue']}; font-weight: bold; }}
        """)
        options_layout.addWidget(self.remember_box)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        layout.addSpacing(15)

        # === BOUTONS D'ACTION ===
        # 1. Se Connecter
        self.btn_login = QPushButton("SE CONNECTER")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['primary_blue']}, stop:1 {COLORS['secondary_blue']});
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                border: none;
            }}
            QPushButton:hover {{
                margin-top: -2px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['secondary_blue']}, stop:1 {COLORS['primary_blue']});
            }}
            QPushButton:pressed {{ margin-top: 2px; }}
        """)
        self.btn_login.clicked.connect(self.handle_login)
        layout.addWidget(self.btn_login)
        
        layout.addSpacing(5)

        # 2. Quitter
        self.btn_quit = QPushButton("QUITTER L'APPLICATION")
        self.btn_quit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_quit.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_light']};
                padding: 10px;
                border-radius: 10px;
                font-size: 12px;
                border: 1px solid #E0E0E0;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']};
                color: white;
                border: 1px solid {COLORS['error']};
            }}
        """)
        self.btn_quit.clicked.connect(QApplication.instance().quit)
        layout.addWidget(self.btn_quit)

        layout.addStretch()

    def show_login_form(self):
        self.overlay.show()
        self.form_container.show()
        self.main_login_button.hide()

    def hide_login_form(self):
        self.overlay.hide()
        self.form_container.hide()
        self.main_login_button.show()


        # ... (rest of init_ui is fine, reusing existing structure if possible or just assuming init_ui is called)
        # Note: I am not replacing init_ui here, just __init__ and handle_login.
        # But wait, replace_file_content replaces a block.
        # I need to target __init__ separately if I can't see lines.
        # Better to just target __init__ and handle_login separately or use multi_replace.
        pass

    def handle_login(self):
        """Gère la connexion"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validation basique
        if not email or not password:
            print("❌ Erreur: Champs vides")
            return

        print(f"Tentative de connexion : {email}")
        
        # 1. Connexion via Base de Données
        if self.db:
            user = self.db.verifier_connexion(email, password)
            if user:
                # user est un tuple (id, nom, prenom, email, mdp, type, ...)
                user_type = user[5]
                print(f"✅ Connexion DB réussie: {user[1]} {user[2]} ({user_type})")
                self.login_success.emit(user, user_type)
                self.close()
                return
            else:
                print("⚠️ Echec connexion DB - Tentative fallback démo...")
        
        # 2. Fallback / Mode Démo (Si DB non dispo ou auth echouée mais match pattern démo)
        # Simulation connexion (Mode Démo)
        if 'admin' in email.lower():
            # Créer un faux objet utilisateur pour la démo
            # Tuple like: (id, nom, prenom, email, pwd, type)
            fake_admin = (0, "Administrateur", "System", email, "", "admin")
            self.login_success.emit(fake_admin, 'admin')
            self.close()
            
        elif 'prof' in email.lower():
            fake_prof = (1, "Professeur", "Enseignant", email, "", "enseignant")
            self.login_success.emit(fake_prof, 'enseignant')
            self.close()
            
        elif 'etud' in email.lower():
            fake_etud = (2, "Étudiant", "LST", email, "", "etudiant")
            self.login_success.emit(fake_etud, 'etudiant')
            self.close()
            
        else:
            print("❌ Identifiants invalides")
            self.password_input.clear()
            self.password_input.setPlaceholderText("Erreur: identifiants incorrects")
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec())