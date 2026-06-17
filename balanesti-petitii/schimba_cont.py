# -*- coding: utf-8 -*-
"""
schimba_cont.py
----------------
Script de utilitate pentru schimbarea utilizatorului și parolei contului
de funcționar, FĂRĂ a șterge petițiile deja existente în baza de date.

Cum se folosește:
1. Opriți aplicația Flask dacă rulează (CTRL+C în terminalul unde rula `python app.py`).
2. Editați mai jos valorile NUME_UTILIZATOR_NOU și PAROLA_NOUA.
3. Rulați în terminal, din folderul proiectului:
       python schimba_cont.py
4. Reporniți aplicația cu `python app.py` și autentificați-vă cu noile date.
"""

from app import app
from models import db, User

# ---------------------------------------------------------------------
# MODIFICAȚI AICI noul utilizator și noua parolă (sau lăsați valorile de mai jos):
NUME_UTILIZATOR_NOU = "lucianadmin"
PAROLA_NOUA = "lucian123"
# ---------------------------------------------------------------------

with app.app_context():
    user = User.query.filter_by(username="admin").first()

    if user is None:
        print("Nu am găsit niciun cont cu utilizatorul 'admin'.")
        print("Verificați manual conturile existente din tabela 'users'.")
    else:
        user.username = NUME_UTILIZATOR_NOU
        user.set_password(PAROLA_NOUA)
        db.session.commit()
        print("Contul a fost actualizat cu succes!")
        print(f"  Utilizator nou: {NUME_UTILIZATOR_NOU}")
        print("  Parola a fost setată (stocată securizat, sub formă de hash).")
