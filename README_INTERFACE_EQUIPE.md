# 📘 Documentation Technique - Interface Graphique (UI)

Ce document résume le travail réalisé sur la partie **Interface Utilisateur** du projet *"Système de Gestion d'Emploi du Temps FSTT"*. Il est destiné à l'équipe de développement pour faciliter l'intégration de la logique métier (Back-end / Algorithmes).

## 🛠️ Technologies Utilisées

*   **Langage** : Python 3.x
*   **Framework GUI** : **PyQt6** (Choisi pour sa robustesse, son look professionnel et sa fluidité).
*   **Style** : CSS (QT Style Sheets) pour un design moderne, épuré et "Flat".
*   **Structure** : Architecture modulaire (séparation Vue / Logique).

---

## 🚀 Ce qui a été réalisé (Livrables)

J'ai conçu et implémenté l'intégralité des interfaces graphiques demandées dans le cahier des charges, réparties en trois profils distincts.

### 1. 🏢 Espace Administrateur (`src/ui/admin_window.py`)
*   **Dashboard Moderne** : Visualisation claire sans emojis, avec des graphiques statistiques (Taux d'occupation, Volume horaire) créés sur mesure avec `QPainter`.
*   **Gestion des Réservations** : Tableau de bord pour valider ou refuser les demandes des enseignants (Boutons Vert/Rouge fonctionnels visuellement).
*   **Préparation Génération** : Interface prête pour lancer l'algorithme d'affectation automatique.
*   **Ergonomie** : Fenêtre plein écran, menu latéral fixe, navigation fluide.

### 2. 👨‍🏫 Espace Enseignant (`src/ui/enseignant_window.py`)
*   **Consultation** : Vue emploi du temps personnel (Grille hebdomadaire).
*   **Actions** :
    *   Formulaire de **Demande de réservation** (Date, Heure, Motif).
    *   Outil de **Recherche de salle** (Filtres par capacité/équipement).
    *   Formulaire de **Déclaration d'absence**.

### 3. 👨‍🎓 Espace Étudiant (`src/ui/etudiant_window.py`)
*   **Consultation Groupe** : Vue emploi du temps de la filière.
*   **Temps Réel** : Fil d'actualité pour les notifications (Annulations, Changements de salle) avec code couleur.
*   **Salles Libres** : Recherche rapide pour travaux de groupe.

---

## 📝 Guide étape par étape (Comment j'ai procédé)

Si vous devez expliquer la démarche au prof ou aux collègues :

1.  **Initialisation de l'environnement** :
    *   Création d'un environnement virtuel (`venv`) pour isoler les dépendances.
    *   Installation de `PyQt6` (`pip install PyQt6`).

2.  **Création du Design System (`src/ui/styles.py`)** :
    *   J'ai d'abord défini toutes les couleurs (Bleu FSTT), les polices et les styles des boutons dans un fichier centralisé. Cela garantit que toute l'application est cohérente et belle.

3.  **Développement Modulaire** :
    *   J'ai créé une classe Python par fenêtre (`AdminWindow`, `EnseignantWindow`, `EtudiantWindow`).
    *   Chaque fenêtre utilise un `QStackedWidget` pour changer de page sans fermer la fenêtre (comme des onglets).

4.  **Intégration (`main.py`)** :
    *   Le fichier principal gère la connexion. Selon si c'est un admin, un prof ou un étudiant qui se connecte, il lance la bonne fenêtre.

---

## 🔌 Points d'Intégration pour l'équipe (À faire)

Maintenant que l'interface (le corps) est prête, voici ce que les collègues (le cerveau) doivent connecter :

*   **Base de Données** :
    *   Remplacer les données fictives (Mock Data) dans les `QTableWidget` par des requêtes SQL réelles (ex: récupérer la liste réelle des enseignants).
*   **Algorithme** :
    *   Dans `AdminWindow`, connecter le bouton "Lancer Génération" à votre script Python d'algorithme génétique/CSP.
*   **Logique Métier** :
    *   Enregistrer les demandes de réservation dans la BD quand on clique sur "Soumettre" (Enseignant).
    *   Mettre à jour le statut dans la BD quand l'admin clique sur "Accepter".

---

## ▶️ Comment tester le projet

1.  Activer l'environnement : `.\venv\Scripts\activate`
2.  Lancer l'app : `python main.py`
3.  Comptes de test (Simulation) :
    *   Admin : `admin@fstt.ac.ma`
    *   Prof : `prof@fstt.ac.ma`
    *   Étudiant : `etudiant@fstt.ac.ma`
