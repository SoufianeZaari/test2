# src/logic/timetable_export_service.py
"""
Timetable Export Service - Backend logic for exporting timetables
Supports PDF, Excel, and Image (PNG/JPG) formats
"""

import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from config import EXPORT_FOLDER, ETABLISSEMENT, ANNEE_UNIVERSITAIRE


class TimetableExportService:
    """Service for exporting timetables in various formats"""
    
    def __init__(self, db):
        """
        Initialize the export service
        Args:
            db: Database instance
        """
        self.db = db
        # Ensure export folder exists
        os.makedirs(EXPORT_FOLDER, exist_ok=True)
    
    def export_group_timetable(self, groupe_id: int, format_type: str = "pdf",
                              semaine_debut: str = None, semaine_fin: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Exports group timetable for students
        Args:
            groupe_id: Group ID
            format_type: Export format ("pdf", "excel", "png", "jpg")
            semaine_debut: Start week date (optional)
            semaine_fin: End week date (optional)
        Returns:
            (success, file_path, error_message)
        """
        try:
            # Get group information
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groupes WHERE id = ?", (groupe_id,))
            groupe = cursor.fetchone()
            
            if not groupe:
                conn.close()
                return False, None, "Groupe introuvable"
            
            # Handle both tuple and dict access
            groupe_nom = groupe[1] if isinstance(groupe, tuple) else groupe.get('nom', f"Groupe_{groupe_id}")
            
            # Get seances for the group
            if semaine_debut and semaine_fin:
                seances = self.db.get_seances_by_groupe(groupe_id, semaine_debut, semaine_fin)
            else:
                seances = self.db.get_seances_by_groupe(groupe_id)
            
            conn.close()
            
            # Convert seances to dict format if needed
            seances_dict = []
            for s in seances:
                if isinstance(s, tuple):
                    seances_dict.append({
                        'id': s[0], 'titre': s[1], 'type_seance': s[2],
                        'date': s[3], 'heure_debut': s[4], 'heure_fin': s[5],
                        'salle_id': s[6], 'enseignant_id': s[7], 'groupe_id': s[8]
                    })
                elif isinstance(s, dict):
                    seances_dict.append(s)
                else:
                    try:
                        seances_dict.append(dict(s))
                    except (TypeError, ValueError):
                        continue
            
            # Prepare data for export
            export_data = self._prepare_timetable_data(seances_dict, groupe_nom, None)
            
            # Export based on format
            if format_type.lower() == "pdf":
                return self._export_pdf(export_data, f"emploi_du_temps_groupe_{groupe_nom}")
            elif format_type.lower() in ["excel", "xlsx"]:
                return self._export_excel(export_data, f"emploi_du_temps_groupe_{groupe_nom}")
            elif format_type.lower() in ["png", "jpg", "jpeg"]:
                return self._export_image(export_data, f"emploi_du_temps_groupe_{groupe_nom}", format_type)
            else:
                return False, None, f"Format non supporté: {format_type}"
                
        except Exception as e:
            return False, None, f"Erreur lors de l'export: {e}"
    
    def export_teacher_timetable(self, enseignant_id: int, format_type: str = "pdf",
                                semaine_debut: str = None, semaine_fin: str = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Exports teacher personal timetable (including manual reservations)
        Args:
            enseignant_id: Teacher ID
            format_type: Export format ("pdf", "excel", "png", "jpg")
            semaine_debut: Start week date (optional)
            semaine_fin: End week date (optional)
        Returns:
            (success, file_path, error_message)
        """
        try:
            # Get teacher information
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM utilisateurs WHERE id = ?", (enseignant_id,))
            enseignant = cursor.fetchone()
            
            if not enseignant:
                conn.close()
                return False, None, "Enseignant introuvable"
            
            # Handle both tuple and dict access
            if isinstance(enseignant, tuple):
                # Structure: (id, nom, prenom, email, mot_de_passe, type_user, specialite, groupe_id, duree_max_jour, date_creation)
                enseignant_nom = f"{enseignant[2]} {enseignant[1]}"
            else:
                enseignant_nom = f"{enseignant.get('prenom', '')} {enseignant.get('nom', '')}"
            
            # Get seances for the teacher
            if semaine_debut and semaine_fin:
                seances = self.db.get_seances_by_enseignant(enseignant_id, semaine_debut, semaine_fin)
            else:
                seances = self.db.get_seances_by_enseignant(enseignant_id)
            
            # Convert seances to dict format
            seances_dict = []
            for s in seances:
                if isinstance(s, tuple):
                    seances_dict.append({
                        'id': s[0], 'titre': s[1], 'type_seance': s[2],
                        'date': s[3], 'heure_debut': s[4], 'heure_fin': s[5],
                        'salle_id': s[6], 'enseignant_id': s[7], 'groupe_id': s[8]
                    })
                elif isinstance(s, dict):
                    seances_dict.append(s)
                else:
                    try:
                        seances_dict.append(dict(s))
                    except (TypeError, ValueError):
                        continue
            
            # Get approved reservations for the teacher
            cursor.execute('''
                SELECT * FROM reservations
                WHERE enseignant_id = ? AND statut = 'validee'
            ''', (enseignant_id,))
            reservations_tuples = cursor.fetchall()
            
            # Convert reservations to seance format for display
            for res in reservations_tuples:
                if isinstance(res, tuple):
                    # Structure: (id, enseignant_id, salle_id, date, heure_debut, heure_fin, statut, motif, date_demande)
                    seances_dict.append({
                        'id': res[0],
                        'titre': f"Réservation - {res[7] or ''}",
                        'type_seance': 'Réservation',
                        'date': res[3],
                        'heure_debut': res[4],
                        'heure_fin': res[5],
                        'salle_id': res[2],
                        'enseignant_id': res[1],
                        'groupe_id': None
                    })
                else:
                    try:
                        res_dict = dict(res) if not isinstance(res, dict) else res
                        seances_dict.append({
                            'id': res_dict['id'],
                            'titre': f"Réservation - {res_dict.get('motif', '')}",
                            'type_seance': 'Réservation',
                            'date': res_dict['date'],
                            'heure_debut': res_dict['heure_debut'],
                            'heure_fin': res_dict['heure_fin'],
                            'salle_id': res_dict['salle_id'],
                            'enseignant_id': res_dict['enseignant_id'],
                            'groupe_id': None
                        })
                    except (TypeError, KeyError, ValueError):
                        continue
            
            conn.close()
            
            # Prepare data for export
            export_data = self._prepare_timetable_data(seances_dict, None, enseignant_nom)
            
            # Export based on format
            if format_type.lower() == "pdf":
                return self._export_pdf(export_data, f"emploi_du_temps_{enseignant_nom.replace(' ', '_')}")
            elif format_type.lower() in ["excel", "xlsx"]:
                return self._export_excel(export_data, f"emploi_du_temps_{enseignant_nom.replace(' ', '_')}")
            elif format_type.lower() in ["png", "jpg", "jpeg"]:
                return self._export_image(export_data, f"emploi_du_temps_{enseignant_nom.replace(' ', '_')}", format_type)
            else:
                return False, None, f"Format non supporté: {format_type}"
                
        except Exception as e:
            return False, None, f"Erreur lors de l'export: {e}"
    
    def _prepare_timetable_data(self, seances: List, groupe_nom: Optional[str],
                               enseignant_nom: Optional[str]) -> Dict:
        """
        Prepares timetable data for export
        Args:
            seances: List of sessions (as dictionaries)
            groupe_nom: Group name (for student export)
            enseignant_nom: Teacher name (for teacher export)
        Returns:
            Dictionary with formatted data
        """
        # Get room names
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Organize by day and time
        weekly_schedule = {}
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
        
        for day in days:
            weekly_schedule[day] = []
        
        for seance in seances:
            date_str = seance.get('date', '')
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = days[date_obj.weekday()]
            except (ValueError, IndexError):
                continue
            
            # Get room name
            salle_id = seance.get('salle_id')
            salle_nom = "N/A"
            if salle_id:
                cursor.execute("SELECT nom FROM salles WHERE id = ?", (salle_id,))
                salle = cursor.fetchone()
                if salle:
                    salle_nom = salle[0] if isinstance(salle, tuple) else salle.get('nom', 'N/A')
            
            # Get teacher name (for group timetable)
            enseignant_id = seance.get('enseignant_id')
            enseignant_nom_seance = "N/A"
            if enseignant_id:
                cursor.execute("SELECT nom, prenom FROM utilisateurs WHERE id = ?", (enseignant_id,))
                enseignant = cursor.fetchone()
                if enseignant:
                    if isinstance(enseignant, tuple):
                        enseignant_nom_seance = f"{enseignant[1]} {enseignant[0]}"
                    else:
                        enseignant_nom_seance = f"{enseignant.get('prenom', '')} {enseignant.get('nom', '')}"
            
            # Get group name (for teacher timetable)
            groupe_id = seance.get('groupe_id')
            groupe_nom_seance = "N/A"
            if groupe_id:
                cursor.execute("SELECT nom FROM groupes WHERE id = ?", (groupe_id,))
                groupe = cursor.fetchone()
                if groupe:
                    groupe_nom_seance = groupe[0] if isinstance(groupe, tuple) else groupe.get('nom', 'N/A')
            
            weekly_schedule[day_name].append({
                'time': f"{seance.get('heure_debut', '')} - {seance.get('heure_fin', '')}",
                'course': seance.get('titre', ''),
                'type': seance.get('type_seance', ''),
                'room': salle_nom,
                'teacher': enseignant_nom_seance,
                'group': groupe_nom_seance
            })
        
        conn.close()
        
        # Sort by time for each day
        for day in days:
            weekly_schedule[day].sort(key=lambda x: x['time'])
        
        return {
            'title': f"Emploi du Temps - {groupe_nom if groupe_nom else enseignant_nom}",
            'subtitle': f"{ETABLISSEMENT} - {ANNEE_UNIVERSITAIRE}",
            'groupe_nom': groupe_nom,
            'enseignant_nom': enseignant_nom,
            'schedule': weekly_schedule,
            'period': self._get_period_string(seances)
        }
    
    def _get_period_string(self, seances: List) -> str:
        """Gets period string from seances"""
        if not seances:
            return "Période non spécifiée"
        
        dates = [s.get('date') for s in seances if s.get('date')]
        if not dates:
            return "Période non spécifiée"
        
        try:
            date_objs = [datetime.strptime(d, "%Y-%m-%d") for d in dates if d]
            if date_objs:
                min_date = min(date_objs)
                max_date = max(date_objs)
                return f"{min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')}"
        except ValueError:
            pass
        
        return "Période non spécifiée"
    
    def _export_pdf(self, data: Dict, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Exports timetable to PDF
        Note: This is a placeholder - actual PDF generation would require a library like reportlab
        """
        try:
            # Placeholder for PDF export
            # In real implementation, would use reportlab or similar
            filepath = os.path.join(EXPORT_FOLDER, f"{filename}.pdf")
            
            # For now, create a text file as placeholder
            with open(filepath.replace('.pdf', '_placeholder.txt'), 'w', encoding='utf-8') as f:
                f.write(f"{data['title']}\n")
                f.write(f"{data['subtitle']}\n")
                f.write(f"Période: {data['period']}\n\n")
                for day, sessions in data['schedule'].items():
                    if sessions:
                        f.write(f"\n{day}:\n")
                        for session in sessions:
                            f.write(f"  {session['time']} - {session['course']} ({session['type']})\n")
                            f.write(f"    Salle: {session['room']}\n")
            
            return True, filepath, None
        except Exception as e:
            return False, None, f"Erreur export PDF: {e}"
    
    def _export_excel(self, data: Dict, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Exports timetable to Excel
        Note: This is a placeholder - actual Excel generation would require openpyxl or xlsxwriter
        """
        try:
            # Placeholder for Excel export
            # In real implementation, would use openpyxl or xlsxwriter
            filepath = os.path.join(EXPORT_FOLDER, f"{filename}.xlsx")
            
            # For now, create a CSV file as placeholder
            csv_path = filepath.replace('.xlsx', '_placeholder.csv')
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow([data['title']])
                writer.writerow([data['subtitle']])
                writer.writerow([f"Période: {data['period']}"])
                writer.writerow([])
                writer.writerow(['Jour', 'Horaire', 'Cours', 'Type', 'Salle', 'Enseignant/Groupe'])
                
                for day, sessions in data['schedule'].items():
                    if sessions:
                        for session in sessions:
                            teacher_or_group = session.get('teacher') or session.get('group', '')
                            writer.writerow([
                                day,
                                session['time'],
                                session['course'],
                                session['type'],
                                session['room'],
                                teacher_or_group
                            ])
            
            return True, filepath, None
        except Exception as e:
            return False, None, f"Erreur export Excel: {e}"
    
    def _export_image(self, data: Dict, filename: str, format_type: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Exports timetable to Image (PNG/JPG)
        Note: This is a placeholder - actual image generation would require PIL/Pillow
        """
        try:
            # Placeholder for Image export
            # In real implementation, would use PIL/Pillow to create image
            filepath = os.path.join(EXPORT_FOLDER, f"{filename}.{format_type.lower()}")
            
            # For now, create a text file as placeholder
            with open(filepath.replace(f'.{format_type}', '_placeholder.txt'), 'w', encoding='utf-8') as f:
                f.write(f"{data['title']}\n")
                f.write(f"{data['subtitle']}\n")
                f.write(f"Période: {data['period']}\n\n")
                for day, sessions in data['schedule'].items():
                    if sessions:
                        f.write(f"\n{day}:\n")
                        for session in sessions:
                            f.write(f"  {session['time']} - {session['course']} ({session['type']})\n")
                            f.write(f"    Salle: {session['room']}\n")
            
            return True, filepath, None
        except Exception as e:
            return False, None, f"Erreur export Image: {e}"

