from src.database import Database
from src.logic.conflict_detector import ConflictDetector
import config

def test_pause_logic():
    print("--- 🕵️ TEST DE LA PAUSE (Config 09:00) ---")
    
    DATE_TEST = "2024-02-05" # Lundi
    
    # 1. Connexion DB
    db = Database()
    salles = db.get_toutes_salles()
    if not salles:
        print("❌ Erreur : Pas de salles. Lance 'python init_data.py'")
        return
        
    salle_id = salles[0]['id']
    print(f"📍 Salle : {salles[0]['nom']} (ID: {salle_id})")

    groupes = db.get_tous_groupes()
    if not groupes: return
    groupe_id = groupes[0]['id']
    
    users = db.get_tous_utilisateurs()
    prof_id = users[0]['id'] if users else 1

    # 2. SCÉNARIO COMPATIBLE AVEC TES HORAIRES [09:00 - 10:30]
    print("\n1️⃣ Insertion de la Séance 1 (09:00 - 10:30)...")
    try:
        # On insère le premier créneau officiel
        db.ajouter_seance("Cours Test", "Cours", DATE_TEST, "09:00", "10:30", salle_id, prof_id, groupe_id)
        print("✅ Séance 1 enregistrée.")
    except Exception as e:
        print(f"⚠️ Erreur insertion : {e}")

    # 3. Initialisation Détecteur
    print("⚙️ Chargement du ConflictDetector...")
    raw_seances = db.get_seances_by_salle(salle_id, DATE_TEST)
    existing_seances = [dict(row) for row in raw_seances]
    detector = ConflictDetector(existing_seances)

    # 4. TEST A : Tentative PENDANT LA PAUSE (10:30 -> 10:45)
    # On essaye d'ajouter un cours à 10:35 (5min après la fin du cours)
    # Normalement, ConflictDetector impose 10min de pause min.
    # Donc 10:30 + 10min = 10:40.
    # 10:35 est < 10:40 -> DOIT BLOQUER.
    
    print(f"\n👉 Test A : Tentative à 10:35 (Dans la pause)...")
    conflits = detector.detect_all_conflicts(DATE_TEST, "10:35", "12:00", salle_id=salle_id)
    
    if conflits:
        print(f"✅ SUCCÈS : Le système a bloqué ! -> {conflits[0]}")
    else:
        print("❌ ÉCHEC : Le système a laissé passer (Pause ignorée) !")

    # 5. TEST B : Tentative APRÈS LA PAUSE (10:45)
    # Le prochain créneau officiel est 10:45. Ça doit passer.
    print("\n👉 Test B : Tentative à 10:45 (Créneau suivant)...")
    conflits_ok = detector.detect_all_conflicts(DATE_TEST, "10:45", "12:15", salle_id=salle_id)
    
    if not conflits_ok:
        print("✅ SUCCÈS : Créneau validé.")
    else:
        print(f"❌ ÉCHEC : Faux conflit détecté -> {conflits_ok}")
    
    print("\nFin du test.")

if __name__ == "__main__":
    test_pause_logic()