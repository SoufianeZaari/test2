# 📚 Documentation Interface - Système FSTT

## 🎯 TON TRAVAIL (Phase 1 - LOGIN)

Tu as maintenant une **interface de connexion professionnelle** complète!

---

## 📁 FICHIERS CRÉÉS

```
ton_projet/
├── main.py                    ✅ Point d'entrée
├── config.py                  ✅ Configuration
├── src/
│   └── ui/
│       ├── __init__.py        ✅ Package
│       ├── styles.py          ✅ Tous les styles CSS
│       └── login_window.py    ✅ Page de connexion
├── assets/
│   └── images/
│       ├── fst_background.png ⚠️ À AJOUTER
│       └── fst_logo.png       ⚠️ À AJOUTER
```

---

## 🚀 INSTALLATION DANS TON PROJET

### 1️⃣ Copier les fichiers dans ton projet GitHub

```bash
# Dans ton terminal (dossier de ton projet)
# Les fichiers sont déjà créés dans /home/claude/

# Copie ces fichiers dans ton projet:
cp /chemin/vers/main.py .
cp /chemin/vers/config.py .
cp -r /chemin/vers/src/ui/ src/
cp -r /chemin/vers/assets/ .
```

### 2️⃣ Ajouter tes images FST

**IMPORTANT**: Place tes 2 images dans le dossier `assets/images/`:

1. **`fst_background.png`**: Photo du campus FST (celle que tu m'as envoyée)
2. **`fst_logo.png`**: Logo FST (celui bleu/jaune)

```bash
# Crée le dossier si nécessaire
mkdir -p assets/images

# Copie tes images
cp /chemin/vers/ta/photo_fst.png assets/images/fst_background.png
cp /chemin/vers/ton/logo_fst.png assets/images/fst_logo.png
```

### 3️⃣ Lancer l'application

```bash
# Active ton environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Lance l'application
python main.py
```

---

## 🎨 CE QUE TU AS

### ✅ Page LOGIN Complète:

1. **Background avec image FST**
   - Ton image du campus en fond d'écran
   - Si l'image n'existe pas, dégradé bleu FSTT

2. **Bouton LOGIN principal**
   - Grand bouton "LOGIN" au centre
   - Animation au survol

3. **Formulaire de connexion** (apparaît au clic):
   - Overlay sombre sur le background
   - Logo FST semi-transparent en arrière-plan du formulaire
   - Titre "GESTION D'EMPLOI DU TEMPS" en dégradé bleu/jaune
   - Champ Email
   - Champ Mot de passe
   - Bouton "SE CONNECTER"
   - Bouton "QUITTER"

4. **Animations professionnelles**:
   - Fade in/out du formulaire
   - Shake sur les erreurs
   - Transitions fluides

5. **Validation**:
   - Messages d'erreur animés sous les inputs
   - Vérification dans la base de données
   - Redirection automatique selon le type d'utilisateur

---

## 🔍 COMMENT ÇA MARCHE

### Architecture du code:

```python
# main.py - Point d'entrée
FSSTApplication()
    ├── show_login()          # Affiche LoginWindow
    ├── on_login_success()    # Reçoit le signal de connexion
    └── show_admin_window()   # Redirige selon le type
        show_enseignant_window()
        show_etudiant_window()

# src/ui/login_window.py
LoginWindow()
    ├── init_ui()                  # Crée l'interface
    ├── create_login_form()        # Formulaire
    ├── show_login_form()          # Animation d'ouverture
    ├── hide_login_form()          # Animation de fermeture
    ├── handle_login()             # Gestion de la connexion
    └── login_success.emit()       # Signal PyQt6
```

### Flux de connexion:

```
1. Utilisateur clique sur "LOGIN"
   ↓
2. Formulaire apparaît avec animation
   ↓
3. Utilisateur entre email/password
   ↓
4. Validation des champs
   ↓
5. Vérification dans database.py
   ↓
6. Si OK: Signal login_success.emit(user, type)
   ↓
7. main.py reçoit le signal
   ↓
8. Redirection vers interface appropriée
```

---

## 🧪 TEST DE L'INTERFACE

### Test avec base de données:

```bash
python main.py
```

- Utilise le compte admin par défaut:
  - Email: `admin@fstt.ac.ma`
  - Password: `admin123`

### Test sans base de données (Mode démo):

L'interface fonctionne même sans BDD:
- Email avec "admin" → Interface admin
- Email avec "prof" ou "enseignant" → Interface enseignant
- Autre email → Interface étudiant

---

## 🎨 PERSONNALISATION

### Changer les couleurs:

Édite `config.py`:

```python
COLORS = {
    'primary_blue': '#0066CC',      # Ton bleu
    'primary_yellow': '#FFC107',    # Ton jaune
    ...
}
```

### Changer la taille de la fenêtre:

Édite `config.py`:

```python
WINDOW_CONFIG = {
    'login': {
        'width': 1000,    # Change ici
        'height': 700,    # Et ici
        ...
    }
}
```

### Modifier les messages:

Édite `config.py`:

```python
MESSAGES = {
    'login': {
        'empty_email': 'Ton message personnalisé',
        ...
    }
}
```

---

## 📝 EXPLIQUER AU PROF

### Ce que tu as fait:

1. **Architecture MVC**:
   - `config.py`: Configuration globale
   - `styles.py`: Présentation (Vue)
   - `login_window.py`: Logique + Vue
   - `main.py`: Contrôleur principal

2. **Technologies**:
   - PyQt6 pour l'interface graphique
   - Système de signaux/slots pour la communication
   - Animations avec QPropertyAnimation
   - CSS-like styling avec QSS

3. **Fonctionnalités**:
   - Interface responsive
   - Animations fluides et professionnelles
   - Validation des entrées
   - Connexion à la base de données
   - Gestion des erreurs avec feedback visuel
   - Architecture extensible

4. **Design Pattern**:
   - Signal/Slot (Observer pattern)
   - Séparation des responsabilités
   - Code réutilisable et maintenable

---

## 🐛 DÉPANNAGE

### Erreur: "No module named PyQt6"

```bash
pip install PyQt6 PyQt6-tools
```

### Erreur: "No module named config"

Tu n'es pas dans le bon dossier:

```bash
cd /chemin/vers/ton/projet
python main.py
```

### L'image ne s'affiche pas

Vérifie que le fichier existe:

```bash
ls -la assets/images/fst_background.png
```

Si non, place ton image là.

### La base de données ne fonctionne pas

Mode démo activé automatiquement. Pour utiliser la vraie BDD:

1. Vérifie que `src/database.py` existe
2. Vérifie que `models.py` existe
3. Lance `python init_data.py` pour créer la BDD

---

## 📊 PROCHAINES ÉTAPES

### Phase 2: Interface Admin (à faire après)

Tu devras créer `src/ui/admin_window.py` avec:
- Dashboard avec stats
- Gestion emplois du temps
- Gestion utilisateurs
- Gestion salles
- Validation réservations

### Phase 3: Interface Enseignant

Tu devras créer `src/ui/enseignant_window.py` avec:
- Emploi du temps personnel
- Demandes de réservation
- Déclaration d'indisponibilités

### Phase 4: Interface Étudiant

Tu devras créer `src/ui/etudiant_window.py` avec:
- Emploi du temps du groupe
- Recherche de salles libres

---

## 💡 CONSEILS

### Pour présenter au prof:

1. **Montre le code propre**:
   - Commentaires en français
   - Structure claire
   - Séparation des responsabilités

2. **Démo en direct**:
   - Lance `python main.py`
   - Montre les animations
   - Montre la validation des erreurs
   - Connecte-toi avec différents types d'utilisateurs

3. **Explique l'architecture**:
   - Pourquoi PyQt6
   - Comment les signaux/slots fonctionnent
   - Comment ajouter de nouvelles fenêtres

### Pour travailler avec tes collègues:

1. **Git workflow**:
   ```bash
   git add src/ui/
   git commit -m "feat: Interface de connexion professionnelle"
   git push origin interface-login
   ```

2. **Documentation**:
   - Ce README explique tout
   - Les commentaires dans le code sont détaillés
   - Facile pour eux de comprendre et étendre

---

## ✅ CHECKLIST AVANT DE PUSH

- [ ] Les 2 images sont dans `assets/images/`
- [ ] Teste avec `python main.py`
- [ ] La connexion admin fonctionne
- [ ] Les animations sont fluides
- [ ] Les erreurs s'affichent correctement
- [ ] Le code est commenté
- [ ] README à jour

---

## 🎓 RESSOURCES

### PyQt6:
- Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Tutoriels: https://www.pythonguis.com/pyqt6-tutorial/

### Animations Qt:
- QPropertyAnimation
- QEasingCurve
- QGraphicsOpacityEffect

---

**Créé par: [TON NOM]**
**Date: Janvier 2026**
**Projet: Système de Gestion d'Emploi du Temps FSTT**