# 📚 Système de Gestion d'Emploi du Temps - FST Tanger

**Projet académique - Année 2025/2026**

## 👥 Équipe

- **[TON NOM]** : Base de données + Import CSV ✅
- **Membre 2** : Interface utilisateur 🔄
- **Membre 3** : Génération emploi du temps 🔄
- **Membre 4** : Réservations + Exports 🔄

## 📦 Installation
```bash
# 1. Cloner le projet
git clone https://github.com/[TON-USERNAME]/fstt-emploi-temps.git
cd fstt-emploi-temps

# 2. Initialiser la base de données
python generate_templates.py
python init_data.py
```

## 🗂️ Structure du projet
```
PROJET_EMPLOI_DU_TEMPS/
├── src/
│   ├── database.py           ✅ Gestion BDD
│   └── import_manager.py     ✅ Import CSV
├── data/                     
├── templates_csv/            
├── config.py                 ✅ Configuration
├── models.py                 ✅ Classes métier
└── init_data.py             ✅ Initialisation
```

## 🎯 Fonctionnalités complétées

✅ Base de données SQLite (8 tables)
✅ Import CSV massif (salles, enseignants, groupes, étudiants)
✅ Classes POO avec héritage
✅ Système de backup automatique

## 🔐 Compte admin par défaut

- Email : `admin@fstt.ac.ma`
- Mot de passe : `admin123`

## 📝 TODO

- [ ] Interface utilisateur (Membre 2)
- [ ] Génération emploi du temps (Membre 3)
- [ ] Système de réservations (Membre 4)
- [ ] Exports PDF/Excel (Membre 4)

---

**Status** : Phase 1 complétée - En attente des autres modules