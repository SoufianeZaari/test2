# 📚 Système de Gestion d'Emploi du Temps - FST Tanger

**Projet académique - Année 2025/2026**

## 🚀 GUIDE DE DÉMARRAGE RAPIDE

### Prérequis
- **Python 3.10+** installé
- **pip** (gestionnaire de packages Python)

### Installation en 3 étapes

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Initialiser la base de données avec les données de test
python init_data.py

# 3. Lancer l'application
python main.py
```

---

## 🔐 IDENTIFIANTS DE CONNEXION

### Administrateur
| Email | Mot de passe |
|-------|--------------|
| `admin@fstt.ac.ma` | `admin123` |

### Enseignants (60 professeurs)
| Email | Mot de passe |
|-------|--------------|
| `mohammed.alami1@uae.ac.ma` | `prof123` |
| `fatima.bennani1@uae.ac.ma` | `prof123` |
| `ahmed.tazi1@uae.ac.ma` | `prof123` |
| *(tous les autres profs)* | `prof123` |

### Étudiants (1300 étudiants)
| Email | Mot de passe |
|-------|--------------|
| `mohammed.bennani1@etu.uae.ac.ma` | `etudiant123` |
| `fatima.alami2@etu.uae.ac.ma` | `etudiant123` |
| *(tous les autres étudiants)* | `etudiant123` |

---

## 📖 UTILISATION DE L'APPLICATION

### 1️⃣ En tant qu'ADMINISTRATEUR

1. **Se connecter** avec `admin@fstt.ac.ma` / `admin123`
2. **Importer les données** (si pas déjà fait):
   - Aller dans "Générer Emploi" 
   - Cliquer sur "Importer les Salles" → sélectionner `templates_csv/salles.csv`
   - Cliquer sur "Importer Groupes" → sélectionner `templates_csv/groupes.csv`
   - Cliquer sur "Importer Enseignants" → sélectionner `templates_csv/enseignants.csv`
   - Cliquer sur "Importer Étudiants" → sélectionner `templates_csv/etudiants.csv`
3. **Générer l'emploi du temps**:
   - Cliquer sur "Lancer la Génération de l'Emploi du Temps"
   - Attendre la fin de la génération
4. **Gérer les réservations** dans l'onglet "Réservations"
5. **Voir les notifications** dans l'onglet "Notifications"

### 2️⃣ En tant qu'ENSEIGNANT

1. **Se connecter** avec un email prof (ex: `mohammed.alami1@uae.ac.ma` / `prof123`)
2. **Consulter son emploi du temps** dans "Emploi du Temps"
3. **Télécharger** en PDF, Excel ou PNG avec les boutons
4. **Réserver une salle** dans "Réserver une séance"
5. **Signaler une indisponibilité** dans "Indisponibilités"

### 3️⃣ En tant qu'ÉTUDIANT

1. **Se connecter** avec un email étudiant (ex: `mohammed.bennani1@etu.uae.ac.ma` / `etudiant123`)
2. **Consulter l'emploi du temps** de son groupe
3. **Télécharger** en PDF, Excel ou PNG
4. **Chercher des salles libres** dans "Salles Libres"
5. **Voir les mises à jour** (cours annulés, rattrapages) dans "Mises à jour"

---

## 📂 STRUCTURE DU PROJET

```
PROJET_EMPLOI_DU_TEMPS/
├── main.py                    # Point d'entrée de l'application
├── config.py                  # Configuration globale
├── configUI.py                # Configuration interface
├── requirements.txt           # Dépendances Python
│
├── src/
│   ├── database.py            # Gestion base de données SQLite
│   ├── import_manager.py      # Import CSV
│   ├── models.py              # Classes POO (Utilisateur, Enseignant, Etudiant, Salle...)
│   ├── gestionnaire.py        # Logique métier (Rattrapage, Absences)
│   ├── services_notification.py # Service de notifications
│   ├── services_audio.py      # Service Text-to-Speech
│   │
│   ├── ui/                    # Interfaces utilisateur
│   │   ├── login_window.py    # Fenêtre de connexion
│   │   ├── admin_window.py    # Interface administrateur
│   │   ├── enseignant_window.py # Interface enseignant
│   │   └── etudiant_window.py # Interface étudiant
│   │
│   └── logic/                 # Logique de génération
│       ├── schedule_generator.py    # Générateur d'emploi du temps
│       ├── conflict_detector.py     # Détection de conflits
│       ├── constraint_validator.py  # Validation des contraintes
│       ├── room_availability_service.py # Disponibilité des salles
│       └── timetable_export_service.py  # Export PDF/Excel/PNG
│
├── data/
│   └── emploi_du_temps.db     # Base de données SQLite
│
├── templates_csv/             # Fichiers CSV de données
│   ├── salles.csv             # 77 salles FSTT
│   ├── groupes.csv            # 39 groupes
│   ├── enseignants.csv        # 60 enseignants
│   └── etudiants.csv          # 1300 étudiants
│
└── exports/                   # Fichiers exportés (PDF, Excel, PNG)
```

---

## 🔧 DÉPANNAGE

### L'application ne démarre pas
```bash
# Vérifier que PyQt6 est installé
pip install PyQt6

# Réinstaller toutes les dépendances
pip install -r requirements.txt --force-reinstall
```

### Base de données vide
```bash
# Réinitialiser la base de données
rm -f data/emploi_du_temps.db
python init_data.py
```

### Pas d'emploi du temps visible
1. Connectez-vous en tant qu'admin
2. Allez dans "Générer Emploi"
3. Cliquez sur "Lancer la Génération"

### Erreur "Module not found"
```bash
# S'assurer d'être dans le bon répertoire
cd /chemin/vers/le/projet
python main.py
```

---

## 📊 DONNÉES DE TEST

| Entité | Nombre | Description |
|--------|--------|-------------|
| Filières | 13 | Génie Civil, Informatique, etc. |
| Groupes | 39 | GP_GCI, Gr_GCI_1, etc. |
| Salles | 77 | Amphithéâtres, Salles, Labos |
| Enseignants | 60 | Professeurs variés |
| Étudiants | 1300 | Répartis dans les groupes |

---

## ✅ FONCTIONNALITÉS IMPLÉMENTÉES

- [x] Interface de connexion (Admin, Prof, Étudiant)
- [x] Import CSV massif (salles, groupes, enseignants, étudiants)
- [x] Génération automatique d'emploi du temps
- [x] Détection des conflits (salles, profs, groupes)
- [x] Chaque étudiant voit l'emploi du temps de son groupe
- [x] Chaque prof voit ses propres cours
- [x] Export PDF / Excel / PNG
- [x] Système de notifications
- [x] Gestion des rattrapages avec verrouillage de salle
- [x] Gestion des absences avec libération automatique des salles
- [x] Service audio (Text-to-Speech)

---

## 👥 Équipe de Développement

Projet académique - FST Tanger - 2025/2026

---

**Pour toute question, consultez le fichier `Mini projet (1).pdf` qui contient le cahier des charges complet.**