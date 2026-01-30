# src/services_audio.py
"""
Service Audio - Synthèse vocale (Text-to-Speech)
Permet de convertir l'emploi du temps en audio pour une lecture vocale.
"""

import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path


class AudioService:
    """
    Service de synthèse vocale pour la lecture de l'emploi du temps.
    Utilise pyttsx3 (offline) ou gTTS (Google Text-to-Speech).
    """
    
    # Répertoire de sortie pour les fichiers audio
    AUDIO_OUTPUT_DIR = os.path.join("exports", "audio")
    
    # Langues supportées
    LANG_FR = "fr"
    LANG_EN = "en"
    
    def __init__(self, db, lang: str = "fr"):
        """
        Initialise le service audio
        
        Args:
            db: Instance de Database
            lang: Langue pour la synthèse ("fr" ou "en")
        """
        self.db = db
        self.lang = lang
        self.tts_engine = None
        self._init_output_dir()
        self._init_tts_engine()
    
    def _init_output_dir(self):
        """Crée le répertoire de sortie si nécessaire"""
        os.makedirs(self.AUDIO_OUTPUT_DIR, exist_ok=True)
    
    def _init_tts_engine(self):
        """Initialise le moteur TTS (pyttsx3 en priorité)"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)  # Vitesse de parole
            
            # Essayer de configurer la voix française
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_type = "pyttsx3"
            print("✅ Moteur TTS pyttsx3 initialisé")
        except ImportError:
            print("⚠️ pyttsx3 non disponible, utilisation de gTTS si disponible")
            self.tts_type = "gtts"
        except Exception as e:
            print(f"⚠️ Erreur TTS: {e}")
            self.tts_type = "none"
    
    # ═══════════════════════════════════════════════════════════
    # CONVERSION EMPLOI DU TEMPS -> TEXTE LISIBLE
    # ═══════════════════════════════════════════════════════════
    
    def seances_to_text(self, seances: List, date_specifique: str = None) -> str:
        """
        Convertit une liste de séances en texte lisible pour TTS
        
        Args:
            seances: Liste de séances (tuples ou dicts)
            date_specifique: Filtrer sur une date spécifique
        
        Returns:
            Texte formaté pour lecture vocale
        """
        if not seances:
            return "Vous n'avez aucune séance programmée."
        
        # Convertir en dicts si nécessaire
        seances_list = []
        for s in seances:
            if isinstance(s, tuple):
                seances_list.append({
                    'titre': s[1],
                    'type_seance': s[2],
                    'date': s[3],
                    'heure_debut': s[4],
                    'heure_fin': s[5],
                    'salle_id': s[6]
                })
            else:
                seances_list.append(s)
        
        # Filtrer par date si spécifiée
        if date_specifique:
            seances_list = [s for s in seances_list if s['date'] == date_specifique]
            if not seances_list:
                return f"Vous n'avez aucune séance le {self._format_date_vocale(date_specifique)}."
        
        # Trier par date et heure
        seances_list.sort(key=lambda x: (x['date'], x['heure_debut']))
        
        # Grouper par date
        dates_dict = {}
        for s in seances_list:
            d = s['date']
            if d not in dates_dict:
                dates_dict[d] = []
            dates_dict[d].append(s)
        
        # Construire le texte
        texte_parts = []
        
        for date_key in sorted(dates_dict.keys()):
            seances_jour = dates_dict[date_key]
            date_vocale = self._format_date_vocale(date_key)
            
            texte_parts.append(f"{date_vocale}.")
            
            for idx, seance in enumerate(seances_jour, 1):
                heure_debut = self._format_heure_vocale(seance['heure_debut'])
                heure_fin = self._format_heure_vocale(seance['heure_fin'])
                
                # Récupérer le nom de la salle
                salle_nom = "salle inconnue"
                if seance.get('salle_id'):
                    salle = self.db.get_salle_by_id(seance['salle_id'])
                    if salle:
                        salle_nom = f"salle {salle[1]}"
                
                texte_parts.append(
                    f"Séance {idx}: {seance['titre']}, "
                    f"de {heure_debut} à {heure_fin}, "
                    f"en {salle_nom}. "
                    f"Type: {seance['type_seance']}."
                )
        
        return " ".join(texte_parts)
    
    def _format_date_vocale(self, date_str: str) -> str:
        """Formate une date pour lecture vocale"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            mois = ["janvier", "février", "mars", "avril", "mai", "juin", 
                   "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
            
            jour_nom = jours[date_obj.weekday()]
            jour_num = date_obj.day
            mois_nom = mois[date_obj.month - 1]
            
            return f"{jour_nom} {jour_num} {mois_nom}"
        except ValueError:
            return date_str
    
    def _format_heure_vocale(self, heure_str: str) -> str:
        """Formate une heure pour lecture vocale"""
        try:
            parties = heure_str.split(":")
            heures = int(parties[0])
            minutes = int(parties[1]) if len(parties) > 1 else 0
            
            if minutes == 0:
                return f"{heures} heures"
            elif minutes == 30:
                return f"{heures} heures trente"
            else:
                return f"{heures} heures {minutes}"
        except (ValueError, IndexError):
            return heure_str
    
    # ═══════════════════════════════════════════════════════════
    # SYNTHÈSE VOCALE - LECTURE DIRECTE
    # ═══════════════════════════════════════════════════════════
    
    def lire_texte(self, texte: str) -> Tuple[bool, str]:
        """
        Lit un texte à voix haute (pyttsx3)
        
        Args:
            texte: Texte à lire
        
        Returns:
            Tuple (success, message)
        """
        if self.tts_type == "pyttsx3" and self.tts_engine:
            try:
                self.tts_engine.say(texte)
                self.tts_engine.runAndWait()
                return True, "Lecture terminée"
            except Exception as e:
                return False, f"Erreur de lecture: {str(e)}"
        else:
            return False, (
                "Moteur TTS non disponible. Pour activer la lecture vocale, installez l'un des modules suivants:\n"
                "  • pip install pyttsx3  (lecture directe, hors-ligne)\n"
                "  • pip install gTTS     (export fichier audio, nécessite internet)"
            )
    
    def lire_emploi_du_temps_etudiant(self, etudiant_id: int, date: str = None) -> Tuple[bool, str]:
        """
        Lit l'emploi du temps d'un étudiant à voix haute
        
        Args:
            etudiant_id: ID de l'étudiant
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message)
        """
        # Récupérer le groupe de l'étudiant
        etudiant = self.db.get_utilisateur_by_id(etudiant_id)
        if not etudiant:
            return False, "Étudiant non trouvé"
        
        groupe_id = etudiant[7]  # groupe_id est à l'index 7
        if not groupe_id:
            return False, "L'étudiant n'est associé à aucun groupe"
        
        # Récupérer les séances du groupe
        seances = self.db.get_seances_by_groupe(groupe_id)
        
        # Convertir en texte
        texte = self._creer_intro_etudiant(etudiant)
        texte += self.seances_to_text(seances, date)
        
        # Lire le texte
        return self.lire_texte(texte)
    
    def lire_emploi_du_temps_enseignant(self, enseignant_id: int, date: str = None) -> Tuple[bool, str]:
        """
        Lit l'emploi du temps d'un enseignant à voix haute
        
        Args:
            enseignant_id: ID de l'enseignant
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message)
        """
        # Récupérer l'enseignant
        enseignant = self.db.get_utilisateur_by_id(enseignant_id)
        if not enseignant:
            return False, "Enseignant non trouvé"
        
        # Récupérer les séances de l'enseignant
        seances = self.db.get_seances_by_enseignant(enseignant_id)
        
        # Convertir en texte
        texte = self._creer_intro_enseignant(enseignant)
        texte += self.seances_to_text(seances, date)
        
        # Lire le texte
        return self.lire_texte(texte)
    
    def _creer_intro_etudiant(self, etudiant) -> str:
        """Crée une introduction vocale pour un étudiant"""
        prenom = etudiant[2] if isinstance(etudiant, tuple) else etudiant.get('prenom')
        return f"Bonjour {prenom}. Voici votre emploi du temps. "
    
    def _creer_intro_enseignant(self, enseignant) -> str:
        """Crée une introduction vocale pour un enseignant"""
        prenom = enseignant[2] if isinstance(enseignant, tuple) else enseignant.get('prenom')
        return f"Bonjour Professeur {prenom}. Voici vos séances programmées. "
    
    # ═══════════════════════════════════════════════════════════
    # SYNTHÈSE VOCALE - EXPORT FICHIER AUDIO
    # ═══════════════════════════════════════════════════════════
    
    def exporter_audio(self, texte: str, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Exporte un texte vers un fichier audio MP3
        
        Args:
            texte: Texte à convertir
            filename: Nom du fichier (sans extension)
        
        Returns:
            Tuple (success, message, filepath ou None)
        """
        filepath = os.path.join(self.AUDIO_OUTPUT_DIR, f"{filename}.mp3")
        
        # Essayer gTTS d'abord pour l'export
        try:
            from gtts import gTTS
            tts = gTTS(text=texte, lang=self.lang, slow=False)
            tts.save(filepath)
            return True, "Fichier audio créé avec succès", filepath
        except ImportError:
            # Fallback: créer un fichier texte à la place
            txt_path = os.path.join(self.AUDIO_OUTPUT_DIR, f"{filename}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(texte)
            return True, "gTTS non disponible. Fichier texte créé à la place.", txt_path
        except Exception as e:
            return False, f"Erreur d'export: {str(e)}", None
    
    def exporter_emploi_du_temps_etudiant(self, etudiant_id: int, 
                                          date: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Exporte l'emploi du temps d'un étudiant en fichier audio
        
        Args:
            etudiant_id: ID de l'étudiant
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message, filepath)
        """
        # Récupérer l'étudiant
        etudiant = self.db.get_utilisateur_by_id(etudiant_id)
        if not etudiant:
            return False, "Étudiant non trouvé", None
        
        groupe_id = etudiant[7]
        if not groupe_id:
            return False, "L'étudiant n'est associé à aucun groupe", None
        
        # Récupérer les séances
        seances = self.db.get_seances_by_groupe(groupe_id)
        
        # Convertir en texte
        texte = self._creer_intro_etudiant(etudiant)
        texte += self.seances_to_text(seances, date)
        
        # Générer le nom de fichier
        prenom = etudiant[2]
        nom = etudiant[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emploi_du_temps_{prenom}_{nom}_{timestamp}"
        
        return self.exporter_audio(texte, filename)
    
    def exporter_emploi_du_temps_enseignant(self, enseignant_id: int,
                                             date: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Exporte l'emploi du temps d'un enseignant en fichier audio
        
        Args:
            enseignant_id: ID de l'enseignant
            date: Date spécifique (optionnel)
        
        Returns:
            Tuple (success, message, filepath)
        """
        # Récupérer l'enseignant
        enseignant = self.db.get_utilisateur_by_id(enseignant_id)
        if not enseignant:
            return False, "Enseignant non trouvé", None
        
        # Récupérer les séances
        seances = self.db.get_seances_by_enseignant(enseignant_id)
        
        # Convertir en texte
        texte = self._creer_intro_enseignant(enseignant)
        texte += self.seances_to_text(seances, date)
        
        # Générer le nom de fichier
        prenom = enseignant[2]
        nom = enseignant[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"emploi_du_temps_prof_{prenom}_{nom}_{timestamp}"
        
        return self.exporter_audio(texte, filename)
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════
    
    def is_tts_available(self) -> Tuple[bool, str]:
        """Vérifie si le TTS est disponible"""
        if self.tts_type == "pyttsx3":
            return True, "pyttsx3 disponible (lecture directe)"
        elif self.tts_type == "gtts":
            return True, "gTTS disponible (export fichier uniquement)"
        else:
            return False, "Aucun moteur TTS disponible"
    
    def get_emploi_du_temps_texte(self, user_id: int, user_type: str, date: str = None) -> str:
        """
        Récupère l'emploi du temps d'un utilisateur sous forme de texte
        
        Args:
            user_id: ID de l'utilisateur
            user_type: Type ('etudiant' ou 'enseignant')
            date: Date spécifique (optionnel)
        
        Returns:
            Texte formaté de l'emploi du temps
        """
        if user_type == 'etudiant':
            etudiant = self.db.get_utilisateur_by_id(user_id)
            if etudiant and etudiant[7]:  # groupe_id
                seances = self.db.get_seances_by_groupe(etudiant[7])
                return self.seances_to_text(seances, date)
        elif user_type == 'enseignant':
            seances = self.db.get_seances_by_enseignant(user_id)
            return self.seances_to_text(seances, date)
        
        return "Impossible de récupérer l'emploi du temps."
