# init_data.py
"""
═══════════════════════════════════════════════════════════════
SCRIPT D'INITIALISATION DE LA BASE DE DONNÉES FST TANGER
Version complète avec données réelles depuis config.py et CSV
═══════════════════════════════════════════════════════════════
"""

import csv
import sys
from pathlib import Path
from src.database import Database
from config import (
    FILIERES_LST,
    SALLES_FSTT,
    CSV_TEMPLATES,
    APP_CONFIG,
    MESSAGES,
    MATIERES_COMPLETES,
    CYCLES,
    TRONCS_COMMUNS_LST,
    FILIERES_MST,
    FILIERES_INGENIEUR,
    SPECIALITE_KEYWORDS
)

class InitDataFSTT:
    """Classe pour initialiser la base de données avec les données FSTT"""
    
    def __init__(self):
        self.db = Database()
        self.stats = {
            'admin': 0,
            'cycles': 0,
            'filieres': 0,
            'matieres': 0,
            'groupes': 0,
            'salles': 0,
            'enseignants': 0,
            'etudiants': 0,
            'associations': 0
        }
    
    def afficher_banniere(self):
        """Affiche la bannière de démarrage"""
        print("\n" + "═" * 70)
        print(f"  📊 INITIALISATION BASE DE DONNÉES - {APP_CONFIG['etablissement']}")
        print(f"  📅 Année universitaire : {APP_CONFIG['annee_universitaire']}")
        print("═" * 70 + "\n")
    
    def afficher_rapport(self):
        """Affiche le rapport final"""
        print("\n" + "═" * 70)
        print("  ✅ INITIALISATION TERMINÉE AVEC SUCCÈS !")
        print("═" * 70)
        print(f"\n📊 STATISTIQUES :")
        print(f"  • Administrateurs : {self.stats['admin']}")
        print(f"  • Filières LST    : {self.stats['filieres']}")
        print(f"  • Groupes         : {self.stats['groupes']}")
        print(f"  • Salles          : {self.stats['salles']}")
        print(f"  • Enseignants     : {self.stats['enseignants']}")
        print(f"  • Étudiants       : {self.stats['etudiants']}")
        
        print("\n🔐 CONNEXION ADMINISTRATEUR :")
        print("  📧 Email      : admin@fstt.ac.ma")
        print("  🔑 Mot de passe : admin123")
        
        print("\n🚀 PROCHAINES ÉTAPES :")
        print("  1. Lancez l'application : python main.py")
        print("  2. Connectez-vous avec les identifiants admin ci-dessus")
        print("  3. Explorez les données importées")
        print("\n" + "═" * 70 + "\n")
    
    def creer_admin(self):
        """Crée le compte administrateur par défaut"""
        print("👤 Création de l'administrateur...")
        
        # Vérifier si l'admin existe déjà
        admin_existant = self.db.get_utilisateur_by_email("admin@fstt.ac.ma")
        if admin_existant:
            print("  ⚠️  Administrateur déjà existant - ignoré")
            return
        
        admin_id = self.db.ajouter_utilisateur(
            nom="Admin",
            prenom="FST Tanger",
            email="admin@fstt.ac.ma",
            mot_de_passe="admin123",
            type_user="admin"
        )
        
        if admin_id:
            self.stats['admin'] = 1
            print(f"  ✅ Administrateur créé (ID: {admin_id})")
            print(f"     📧 Email : admin@fstt.ac.ma")
            print(f"     🔑 Mot de passe : admin123\n")
        else:
            print("  ❌ Erreur lors de la création de l'administrateur\n")
    

        def initialiser_cycles_et_filieres(self):
            """Initialise les cycles, troncs communs et filières"""
            print("🎓 Initialisation des cycles et filières...\n")
        
            # Étape 1: Créer les cycles
            print("  📚 Création des cycles...")
            for cycle in CYCLES:
                cycle_id = self.db.ajouter_cycle(
                    code=cycle['code'],
                    nom=cycle['nom'],
                    niveau=cycle['niveau'],
                    duree=cycle['duree'],
                    description=cycle.get('description', '')
                )
                if cycle_id:
                    self.stats['cycles'] += 1
                    print(f"    ✅ {cycle['code']:8s} - {cycle['nom']}")
        
            # Étape 2: Créer les troncs communs
            print("\n  🔗 Création des troncs communs LST...")
            for tc_code, tc_nom, accred in TRONCS_COMMUNS_LST:
                tc_id = self.db.ajouter_tronc_commun(
                    code=tc_code,
                    nom=tc_nom,
                    cycle_code='LST',
                    accreditation=accred
                )
                if tc_id:
                    print(f"    ✅ {tc_code:10s} - {tc_nom}")
        
            # Étape 3: Créer les filières LST
            print("\n  📖 Création des filières LST...")
            filieres_ids = {}
            for filiere_info in FILIERES_LST:
                if len(filiere_info) == 2:
                    code, nom = filiere_info
                    desc = ""
                else:
                    code, nom, desc = filiere_info
            
                filiere_id = self.db.ajouter_filiere(
                    code=code,
                    nom=nom,
                    cycle_code='LST',
                    description=desc
                )
                if filiere_id:
                    self.stats['filieres'] += 1
                    filieres_ids[code] = filiere_id
                    print(f"    ✅ {code:10s} - {nom}")
        
            # Étape 4: Créer les filières MST
            print("\n  🎓 Création des filières MST...")
            for code, nom in FILIERES_MST:
                filiere_id = self.db.ajouter_filiere(
                    code=code,
                    nom=nom,
                    cycle_code='MST'
                )
                if filiere_id:
                    self.stats['filieres'] += 1
                    filieres_ids[code] = filiere_id
                    print(f"    ✅ {code:10s} - {nom}")
        
            # Étape 5: Créer les filières Ingénieur
            print("\n  👷 Création des filières Ingénieur...")
            for filiere_info in FILIERES_INGENIEUR:
                code, nom, statut = filiere_info
                filiere_id = self.db.ajouter_filiere(
                    code=code,
                    nom=nom,
                    cycle_code='ING',
                    description=f"Statut: {statut}"
                )
                if filiere_id:
                    self.stats['filieres'] += 1
                    filieres_ids[code] = filiere_id
                    print(f"    ✅ {code:10s} - {nom}")
        
            print()
            return filieres_ids
    
        def initialiser_matieres(self):
            """Initialise toutes les matières pour toutes les filières"""
            print("📚 Initialisation des matières...\n")
        
            nb_matieres = 0
            stats_par_cycle = {}
        
            for cle, matieres in MATIERES_COMPLETES.items():
                # Parser la clé: DEUST_TC-GI_S1 ou LST_AD_S5 ou ING_LSI_S1
                parts = cle.split('_')
                cycle_code = parts[0]
                semestre = parts[-1]
            
                # Le code de filière est tout ce qui est entre le cycle et le semestre
                filiere_code = '_'.join(parts[1:-1])
            
                for matiere_info in matieres:
                    code, nom, type_mat, h_cours, h_td, h_tp = matiere_info
                
                    matiere_id = self.db.ajouter_matiere(
                        code=code,
                        nom=nom,
                        filiere_code=filiere_code,
                        cycle_code=cycle_code,
                        semestre=semestre,
                        type_matiere=type_mat,
                        heures_cours=h_cours,
                        heures_td=h_td,
                        heures_tp=h_tp
                    )
                
                    if matiere_id:
                        nb_matieres += 1
                    
                        # Stats par cycle
                        if cycle_code not in stats_par_cycle:
                            stats_par_cycle[cycle_code] = 0
                        stats_par_cycle[cycle_code] += 1
        
            print(f"  ✅ {nb_matieres} matières initialisées")
            for cycle, nb in stats_par_cycle.items():
                print(f"     • {cycle:6s}: {nb:3d} matières")
            print()
        
            self.stats['matieres'] = nb_matieres
            return nb_matieres

        def associer_enseignants_matieres(self):
            """
            Associe automatiquement chaque enseignant aux matières de sa spécialité
            en respectant la durée maximale de travail
            """
            print("🔗 Association enseignants ↔ matières...")
        
            # Récupérer tous les enseignants
            enseignants = self.db.get_tous_utilisateurs(type_user='enseignant')
        
            if not enseignants:
                print("  ⚠️ Aucun enseignant trouvé - associations ignorées\\n")
                return 0
        
            # Récupérer toutes les matières
            toutes_matieres = self.db.get_toutes_matieres()
        
            if not toutes_matieres:
                print("  ⚠️ Aucune matière trouvée - associations ignorées\\n")
                return 0
        
            nb_associations = 0
            stats_par_specialite = {}
        
            # Pour chaque enseignant
            for enseignant in enseignants:
                ens_id = enseignant[0]
                nom = enseignant[1]
                prenom = enseignant[2]
                specialite = enseignant[6]  # Index de la spécialité
                duree_max_jour = enseignant[8]  # Durée max par jour
            
                if not specialite:
                    continue
            
                # Récupérer les mots-clés de la spécialité
                keywords = SPECIALITE_KEYWORDS.get(specialite, [])
            
                if not keywords:
                    print(f"  ⚠️ Spécialité '{specialite}' non répertoriée - {prenom} {nom} ignoré")
                    continue
            
                # Durée max hebdomadaire (5 jours de travail)
                duree_max_semaine = duree_max_jour * 5
                duree_totale = 0
                nb_matieres_assignees = 0
            
                # Trouver les matières compatibles avec cette spécialité
                for matiere in toutes_matieres:
                    mat_id = matiere[0]
                    mat_nom = matiere[1]
                    mat_code = matiere[2]
                    filiere_code = matiere[3]
                    cycle_code = matiere[4]
                    semestre = matiere[5]
                    nb_heures = matiere[10]  # nb_heures_total
                
                    # Vérifier si la matière correspond à la spécialité
                    nom_lower = mat_nom.lower()
                    match = False
                
                    for keyword in keywords:
                        if keyword.lower() in nom_lower:
                            match = True
                            break
                
                    if not match:
                        continue
                
                    # Vérifier si on ne dépasse pas la durée max hebdomadaire
                    # On suppose qu'une matière de 45h se répartit sur ~15 semaines
                    # Donc ~3h par semaine, soit ~36 min par jour (3h/5j)
                    heures_par_semaine = nb_heures / 15  # Répartition sur 15 semaines
                    minutes_par_jour = (heures_par_semaine * 60) / 5  # Répartition sur 5 jours
                
                    if duree_totale + minutes_par_jour <= duree_max_jour:
                        # Créer l'association
                        try:
                            ens_id_result = self.db.ajouter_enseignement(
                                enseignant_id=ens_id,
                                matiere_id=mat_id,
                                filiere_id=None,  # À récupérer si nécessaire
                                semestre=semestre,
                                groupe_id=None,
                                type_seance='Cours',
                                volume_horaire=nb_heures,
                                annee_universitaire='2025/2026'
                            )
                        
                            if ens_id_result:
                                nb_associations += 1
                                nb_matieres_assignees += 1
                                duree_totale += minutes_par_jour
                        except Exception as e:
                            # Ignorer les doublons (contrainte UNIQUE)
                            pass
            
                # Stats
                if specialite not in stats_par_specialite:
                    stats_par_specialite[specialite] = {'profs': 0, 'matieres': 0}
            
                stats_par_specialite[specialite]['profs'] += 1
                stats_par_specialite[specialite]['matieres'] += nb_matieres_assignees
            
                if nb_matieres_assignees > 0:
                    print(f"  ✅ {prenom} {nom} ({specialite}): {nb_matieres_assignees} matières")
        
            print(f"\\n  📊 Total associations : {nb_associations}")
            print(f"\\n  📈 Statistiques par spécialité:")
            for spec, data in stats_par_specialite.items():
                print(f"     • {spec:30s}: {data['profs']} profs, {data['matieres']} matières")
        
            print()
        
            self.stats['associations'] = nb_associations
            return nb_associations


    def creer_filieres(self):
        """Crée les filières LST depuis config.py"""
        print(f"🎓 Création des {len(FILIERES_LST)} filières LST...")
        
        filieres_ids = {}
        
        for filiere_info in FILIERES_LST:
            # Gérer les tuples avec ou sans description
            if len(filiere_info) == 2:
                code, nom = filiere_info
            else:
                code, nom, _ = filiere_info
            
            filiere_id = self.db.ajouter_filiere(nom, "L3")
            
            if filiere_id:
                filieres_ids[nom] = filiere_id
                self.stats['filieres'] += 1
                print(f"  ✅ {code:10s} - {nom}")
            else:
                print(f"  ⚠️  {code:10s} - {nom} (déjà existante)")
                # Récupérer l'ID si elle existe déjà
                filiere_existante = self.db.get_filiere_by_nom(nom)
                if filiere_existante:
                    filieres_ids[nom] = filiere_existante[0]
        
        print()
        return filieres_ids
    
    def importer_groupes(self, filieres_ids):
        """Importe les groupes depuis groupes.csv"""
        fichier_csv = CSV_TEMPLATES['groupes']
        
        if not fichier_csv.exists():
            print(f"  ⚠️  Fichier {fichier_csv} introuvable - groupes non importés\n")
            return
        
        print(f"👨‍🎓 Importation des groupes depuis {fichier_csv.name}...")
        
        try:
            with open(fichier_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    nom_groupe = row['nom'].strip()
                    effectif = int(row['effectif'])
                    nom_filiere = row['filiere'].strip()
                    
                    # Récupérer l'ID de la filière
                    filiere_id = filieres_ids.get(nom_filiere)
                    
                    if not filiere_id:
                        print(f"  ⚠️  Filière '{nom_filiere}' introuvable pour groupe '{nom_groupe}'")
                        continue
                    
                    # Créer le groupe
                    groupe_id = self.db.ajouter_groupe(nom_groupe, effectif, filiere_id)
                    
                    if groupe_id:
                        self.stats['groupes'] += 1
                        print(f"  ✅ {nom_groupe:20s} ({effectif:2d} étudiants) - {nom_filiere}")
            
            print(f"  📊 Total groupes importés : {self.stats['groupes']}\n")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'import des groupes : {e}\n")
    
    def creer_salles(self):
        """Crée les salles depuis config.py ou salles.csv"""
        fichier_csv = CSV_TEMPLATES['salles']
        
        # Option 1 : Importer depuis CSV si le fichier existe
        if fichier_csv.exists():
            print(f"🏢 Importation des salles depuis {fichier_csv.name}...")
            self._importer_salles_csv(fichier_csv)
        # Option 2 : Créer depuis config.py
        else:
            print(f"🏢 Création des {len(SALLES_FSTT)} salles depuis config.py...")
            self._creer_salles_config()
    
    def _importer_salles_csv(self, fichier_csv):
        """Importe les salles depuis le fichier CSV"""
        try:
            with open(fichier_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    nom = row['nom'].strip()
                    capacite = int(row['capacite'])
                    type_salle = row['type_salle'].strip()
                    equipements = row.get('equipements', '').strip()
                    
                    salle_id = self.db.ajouter_salle(nom, capacite, type_salle, equipements)
                    
                    if salle_id:
                        self.stats['salles'] += 1
                        print(f"  ✅ {nom:20s} ({type_salle:15s}, {capacite:3d} places)")
            
            print(f"  📊 Total salles importées : {self.stats['salles']}\n")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'import des salles : {e}\n")
    
    def _creer_salles_config(self):
        """Crée les salles depuis config.py"""
        for salle_info in SALLES_FSTT:
            if len(salle_info) == 3:
                nom, capacite, type_salle = salle_info
                equipements = ""
            else:
                nom, capacite, type_salle, equipements = salle_info
            
            salle_id = self.db.ajouter_salle(nom, capacite, type_salle, equipements)
            
            if salle_id:
                self.stats['salles'] += 1
                if self.stats['salles'] % 10 == 0:
                    print(f"  ✅ {self.stats['salles']} salles créées...")
        
        print(f"  📊 Total salles créées : {self.stats['salles']}\n")
    
    def importer_enseignants(self):
        """Importe les enseignants depuis enseignants.csv"""
        fichier_csv = CSV_TEMPLATES['enseignants']
        
        if not fichier_csv.exists():
            print(f"  ℹ️  Fichier {fichier_csv} introuvable - enseignants non importés\n")
            return
        
        print(f"👨‍🏫 Importation des enseignants depuis {fichier_csv.name}...")
        
        try:
            with open(fichier_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    nom = row['nom'].strip()
                    prenom = row['prenom'].strip()
                    email = row['email'].strip()
                    specialite = row['specialite'].strip()
                    duree_max_jour = int(row.get('duree_max_jour', 480))
                    
                    # Créer un mot de passe par défaut : prenom.nom
                    mot_de_passe = f"{prenom.lower()}.{nom.lower()}"
                    
                    enseignant_id = self.db.ajouter_utilisateur(
                        nom=nom,
                        prenom=prenom,
                        email=email,
                        mot_de_passe=mot_de_passe,
                        type_user="enseignant",
                        specialite=specialite,
                        duree_max_jour=duree_max_jour
                    )
                    
                    if enseignant_id:
                        self.stats['enseignants'] += 1
                        print(f"  ✅ Prof. {prenom:12s} {nom:15s} ({specialite})")
            
            print(f"  📊 Total enseignants importés : {self.stats['enseignants']}")
            print(f"  🔑 Mot de passe par défaut : prenom.nom (ex: mohammed.alami)\n")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'import des enseignants : {e}\n")
    
    def importer_etudiants(self):
        """Importe les étudiants depuis etudiants.csv"""
        fichier_csv = CSV_TEMPLATES['etudiants']
        
        if not fichier_csv.exists():
            print(f"  ℹ️  Fichier {fichier_csv} introuvable - étudiants non importés\n")
            return
        
        print(f"🎓 Importation des étudiants depuis {fichier_csv.name}...")
        
        try:
            # Récupérer tous les groupes pour mapping
            tous_groupes = self.db.get_tous_groupes()
            groupes_map = {g[1]: g[0] for g in tous_groupes}  # nom -> id
            
            with open(fichier_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    nom = row['nom'].strip()
                    prenom = row['prenom'].strip()
                    email = row['email'].strip()
                    nom_groupe = row['groupe'].strip()
                    
                    # Récupérer l'ID du groupe
                    groupe_id = groupes_map.get(nom_groupe)
                    
                    if not groupe_id:
                        print(f"  ⚠️  Groupe '{nom_groupe}' introuvable pour {prenom} {nom}")
                        continue
                    
                    # Créer un mot de passe par défaut : prenom.nom
                    mot_de_passe = f"{prenom.lower()}.{nom.lower()}"
                    
                    etudiant_id = self.db.ajouter_utilisateur(
                        nom=nom,
                        prenom=prenom,
                        email=email,
                        mot_de_passe=mot_de_passe,
                        type_user="etudiant",
                        groupe_id=groupe_id
                    )
                    
                    if etudiant_id:
                        self.stats['etudiants'] += 1
                        if self.stats['etudiants'] % 10 == 0:
                            print(f"  ✅ {self.stats['etudiants']} étudiants importés...")
            
            print(f"  📊 Total étudiants importés : {self.stats['etudiants']}")
            print(f"  🔑 Mot de passe par défaut : prenom.nom (ex: yassine.hafidi)\n")
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'import des étudiants : {e}\n")
    
    def executer(self):
        """Exécute toute la procédure d'initialisation"""
        self.afficher_banniere()
        
        # Étape 1 : Admin
        self.creer_admin()
        
        # Étape 2 : Filières
        filieres_ids = self.creer_filieres()
        
        # Étape 3 : Groupes
        self.importer_groupes(filieres_ids)
        
        # Étape 4 : Salles
        self.creer_salles()
        
        # Étape 5 : Enseignants (optionnel)
        self.importer_enseignants()
        
        # Étape 6 : Étudiants (optionnel)
        self.importer_etudiants()
        
        # Rapport final
        self.afficher_rapport()


# ═══════════════════════════════════════════════════════════════
# FONCTION UTILITAIRE
# ═══════════════════════════════════════════════════════════════

def verifier_csv_existants():
    """Vérifie quels fichiers CSV sont disponibles"""
    print("\n📋 VÉRIFICATION DES FICHIERS CSV :")
    print("─" * 70)
    
    fichiers_disponibles = []
    fichiers_manquants = []
    
    for nom, chemin in CSV_TEMPLATES.items():
        if chemin.exists():
            # Compter les lignes
            try:
                with open(chemin, 'r', encoding='utf-8') as f:
                    nb_lignes = sum(1 for _ in f) - 1  # -1 pour l'en-tête
                fichiers_disponibles.append((nom, nb_lignes))
                print(f"  ✅ {nom:15s} : {nb_lignes:3d} lignes - {chemin}")
            except:
                fichiers_disponibles.append((nom, "?"))
                print(f"  ⚠️  {nom:15s} : Erreur lecture - {chemin}")
        else:
            fichiers_manquants.append(nom)
            print(f"  ❌ {nom:15s} : MANQUANT - {chemin}")
    
    print("─" * 70)
    
    if fichiers_manquants:
        print(f"\n⚠️  Fichiers manquants : {', '.join(fichiers_manquants)}")
        print("   Les données correspondantes ne seront pas importées.")
    
    print()
    return fichiers_disponibles, fichiers_manquants


# ═══════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        # Vérifier les CSV disponibles
        verifier_csv_existants()
        
        # Demander confirmation
        print("❓ Voulez-vous initialiser/réinitialiser la base de données ?")
        print("   ⚠️  ATTENTION : Cela supprimera toutes les données existantes !")
        reponse = input("\n   Tapez 'oui' pour continuer : ").strip().lower()
        
        if reponse == 'oui':
            # Exécuter l'initialisation
            init = InitDataFSTT()
            init.executer()
        else:
            print("\n❌ Initialisation annulée.\n")
    
    except KeyboardInterrupt:
        print("\n\n❌ Initialisation interrompue par l'utilisateur.\n")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)