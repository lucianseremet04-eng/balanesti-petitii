# -*- coding: utf-8 -*-
"""
models.py
---------
Modelele bazei de date pentru Portalul de Petiții și Sesizări - Primăria Bălănești.

Folosim Flask-SQLAlchemy ca ORM peste o bază de date SQLite.
Două tabele principale:
    - users     : conturile funcționarilor/administratorilor primăriei
    - petitions : petițiile / sesizările depuse de cetățeni
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Instanța SQLAlchemy este creată aici și inițializată ulterior în app.py
# cu db.init_app(app), pentru a evita importurile circulare.
db = SQLAlchemy()


class User(db.Model):
    """
    Cont de utilizator pentru funcționarii primăriei.

    Parola NU este stocată în clar, ci ca hash (Werkzeug / PBKDF2-SHA256),
    conform cerinței de securitate din specificație.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="functionar")

    def set_password(self, password: str) -> None:
        """Generează și salvează hash-ul parolei (nu parola în clar)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifică o parolă în clar față de hash-ul salvat."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


class Petition(db.Model):
    """
    O petiție / sesizare depusă de un cetățean al satului Bălănești.

    `registration_number` este generat automat la creare, în formatul
    BAL-<an>-<secvență de 4 cifre>, ex: BAL-2026-0007.
    """
    __tablename__ = "petitions"

    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # Date de contact ale cetățeanului
    nume = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    telefon = db.Column(db.String(30), nullable=False)
    adresa = db.Column(db.String(255), nullable=False)

    # Detalii despre sesizare
    categorie = db.Column(db.String(50), nullable=False)
    prioritate = db.Column(db.String(20), nullable=False)
    descriere = db.Column(db.Text, nullable=False)
    fotografie = db.Column(db.String(255), nullable=True)  # numele fișierului încărcat

    # Gestionare de către primărie
    status = db.Column(db.String(30), nullable=False, default="Înregistrată")
    raspuns = db.Column(db.Text, nullable=True)
    data_raspuns = db.Column(db.DateTime, nullable=True)

    # Metadate
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Petition {self.registration_number} - {self.status}>"
