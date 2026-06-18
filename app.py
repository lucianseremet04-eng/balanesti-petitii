# -*- coding: utf-8 -*-


import os
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify
)
from sqlalchemy import func, or_

from models import db, User, Petition

# --------------------------------------------------------------------------
# Configurare aplicație
# --------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)

# IMPORTANT: într-un mediu de producție reală, SECRET_KEY trebuie citit
# dintr-o variabilă de mediu, nu scris direct în cod.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "cheie-secreta-balanesti-schimba-in-productie-2026"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # limită de 5 MB per fișier încărcat

db.init_app(app)

# Liste de referință folosite în formulare, filtre și șabloane
CATEGORII = [
    "Gropi în drum",
    "Iluminat stradal",
    "Salubrizare",
    "Câini vagabonzi",
    "Spații verzi",
    "Alte probleme",
]
PRIORITATI = ["Scăzută", "Medie", "Ridicată", "Urgentă"]
STATUSURI = ["Înregistrată", "În analiză", "În lucru", "Rezolvată", "Respinsă"]

# Statusuri considerate "în lucru" pentru cardul de pe dashboard
STATUSURI_IN_LUCRU = ["În analiză", "În lucru"]


# --------------------------------------------------------------------------
# Funcții ajutătoare
# --------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    """Verifică dacă extensia fișierului încărcat este permisă."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(view):
    """Decorator simplu bazat pe sesiune Flask pentru rutele de administrare."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Trebuie să vă autentificați pentru a accesa această pagină.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def generate_registration_number() -> str:
    """
    Generează un număr unic de înregistrare în formatul BAL-<an>-<NNNN>.
    Secvența se reia de la 1 în fiecare an calendaristic.
    """
    year = datetime.now().year
    prefix = f"BAL-{year}-"
    count_this_year = Petition.query.filter(
        Petition.registration_number.like(f"{prefix}%")
    ).count()
    return f"{prefix}{count_this_year + 1:04d}"


@app.context_processor
def inject_globals():
    """Variabile disponibile în toate șabloanele (an curent, utilizator logat)."""
    return dict(
        current_year=datetime.now().year,
        logged_in_user=session.get("username"),
    )


# --------------------------------------------------------------------------
# Rute publice - pagina principală
# --------------------------------------------------------------------------

@app.route("/")
def index():
    total_petitii = Petition.query.count()
    rezolvate = Petition.query.filter_by(status="Rezolvată").count()
    return render_template("index.html", total_petitii=total_petitii, rezolvate=rezolvate)


# --------------------------------------------------------------------------
# Rute publice - depunere petiție
# --------------------------------------------------------------------------

@app.route("/petitie/noua", methods=["GET", "POST"])
def petition_new():
    if request.method == "POST":
        nume = request.form.get("nume", "").strip()
        email = request.form.get("email", "").strip()
        telefon = request.form.get("telefon", "").strip()
        adresa = request.form.get("adresa", "").strip()
        categorie = request.form.get("categorie", "")
        prioritate = request.form.get("prioritate", "")
        descriere = request.form.get("descriere", "").strip()

        # Validare minimală pe server (în plus față de cea din browser)
        erori = []
        if not nume:
            erori.append("Numele și prenumele sunt obligatorii.")
        if not email:
            erori.append("Adresa de email este obligatorie.")
        if not telefon:
            erori.append("Numărul de telefon este obligatoriu.")
        if not adresa:
            erori.append("Adresa este obligatorie.")
        if categorie not in CATEGORII:
            erori.append("Selectați o categorie validă.")
        if prioritate not in PRIORITATI:
            erori.append("Selectați o prioritate validă.")
        if not descriere:
            erori.append("Descrierea problemei este obligatorie.")

        if erori:
            for e in erori:
                flash(e, "danger")
            return render_template(
                "petition_form.html",
                categorii=CATEGORII, prioritati=PRIORITATI, form_data=request.form,
            )

        # Procesare fotografie (opțională)
        nume_fisier = None
        foto = request.files.get("fotografie")
        if foto and foto.filename:
            if allowed_file(foto.filename):
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                extensie = foto.filename.rsplit(".", 1)[1].lower()
                nume_fisier = f"{uuid.uuid4().hex}.{extensie}"
                foto.save(os.path.join(app.config["UPLOAD_FOLDER"], nume_fisier))
            else:
                flash(
                    "Formatul fotografiei nu este acceptat (folosiți PNG, JPG sau GIF). "
                    "Petiția a fost trimisă fără fotografie.", "warning",
                )

        petitie = Petition(
            registration_number=generate_registration_number(),
            nume=nume, email=email, telefon=telefon, adresa=adresa,
            categorie=categorie, prioritate=prioritate, descriere=descriere,
            fotografie=nume_fisier, status="Înregistrată",
        )
        db.session.add(petitie)
        db.session.commit()

        return redirect(url_for("petition_confirmation", reg_number=petitie.registration_number))

    return render_template("petition_form.html", categorii=CATEGORII, prioritati=PRIORITATI, form_data={})


@app.route("/petitie/confirmare/<reg_number>")
def petition_confirmation(reg_number):
    petitie = Petition.query.filter_by(registration_number=reg_number).first_or_404()
    return render_template("confirmation.html", petitie=petitie)


# --------------------------------------------------------------------------
# Rute publice - verificare status
# --------------------------------------------------------------------------

@app.route("/status", methods=["GET", "POST"])
def status_check():
    petitie = None
    cautare_efectuata = False

    if request.method == "POST":
        reg_number = request.form.get("registration_number", "").strip().upper()
        cautare_efectuata = True
        petitie = Petition.query.filter_by(registration_number=reg_number).first()
        if not petitie:
            flash("Nu a fost găsită nicio petiție cu acest număr de înregistrare.", "warning")

    return render_template("status_check.html", petitie=petitie, cautare_efectuata=cautare_efectuata)


# --------------------------------------------------------------------------
# Autentificare funcționari
# --------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            flash(f"Bine ați venit, {user.username}!", "success")
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)

        flash("Utilizator sau parolă incorectă.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("V-ați deconectat cu succes.", "info")
    return redirect(url_for("index"))


# --------------------------------------------------------------------------
# Zona de administrare (necesită autentificare)
# --------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    total = Petition.query.count()
    noi = Petition.query.filter_by(status="Înregistrată").count()
    in_lucru = Petition.query.filter(Petition.status.in_(STATUSURI_IN_LUCRU)).count()
    rezolvate = Petition.query.filter_by(status="Rezolvată").count()

    # Agregări pentru grafice (Chart.js)
    cat_query = dict(
        db.session.query(Petition.categorie, func.count(Petition.id))
        .group_by(Petition.categorie).all()
    )
    prio_query = dict(
        db.session.query(Petition.prioritate, func.count(Petition.id))
        .group_by(Petition.prioritate).all()
    )
    status_query = dict(
        db.session.query(Petition.status, func.count(Petition.id))
        .group_by(Petition.status).all()
    )

    # Ne asigurăm că toate categoriile/statusurile apar în grafic, chiar și cu 0
    cat_counts = [cat_query.get(c, 0) for c in CATEGORII]
    prio_counts = [prio_query.get(p, 0) for p in PRIORITATI]
    status_counts = [status_query.get(s, 0) for s in STATUSURI]

    recente = Petition.query.order_by(Petition.created_at.desc()).limit(6).all()

    return render_template(
        "dashboard.html",
        total=total, noi=noi, in_lucru=in_lucru, rezolvate=rezolvate,
        categorii=CATEGORII, cat_counts=cat_counts,
        prioritati=PRIORITATI, prio_counts=prio_counts,
        statusuri=STATUSURI, status_counts=status_counts,
        recente=recente,
    )


@app.route("/admin/petitii")
@login_required
def manage_petitions():
    query = Petition.query

    categorie = request.args.get("categorie", "")
    status = request.args.get("status", "")
    cetatean = request.args.get("cetatean", "").strip()

    if categorie:
        query = query.filter_by(categorie=categorie)
    if status:
        query = query.filter_by(status=status)
    if cetatean:
        termen = f"%{cetatean}%"
        query = query.filter(
            or_(
                Petition.nume.ilike(termen),
                Petition.email.ilike(termen),
                Petition.telefon.ilike(termen),
                Petition.registration_number.ilike(termen),
            )
        )

    petitii = query.order_by(Petition.created_at.desc()).all()

    return render_template(
        "manage_petitions.html",
        petitii=petitii, categorii=CATEGORII, statusuri=STATUSURI,
        filtre={"categorie": categorie, "status": status, "cetatean": cetatean},
    )


@app.route("/admin/petitie/<int:petition_id>", methods=["GET", "POST"])
@login_required
def petition_details(petition_id):
    petitie = Petition.query.get_or_404(petition_id)

    if request.method == "POST":
        status_nou = request.form.get("status")
        raspuns = request.form.get("raspuns", "").strip()

        if status_nou in STATUSURI:
            petitie.status = status_nou
        if raspuns:
            petitie.raspuns = raspuns
            petitie.data_raspuns = datetime.utcnow()

        petitie.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Petiția a fost actualizată cu succes.", "success")
        return redirect(url_for("petition_details", petition_id=petitie.id))

    return render_template("petition_details.html", petitie=petitie, statusuri=STATUSURI)


# --------------------------------------------------------------------------
# Inițializarea bazei de date și a contului implicit de administrator
# --------------------------------------------------------------------------

def init_db():
    """Creează tabelele (dacă nu există) și utilizatorul implicit admin/parola123."""
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="lucianadmin").first():
            admin = User(username="lucianadmin", role="admin")
            admin.set_password("lucian123")
            db.session.add(admin)
            db.session.commit()
            print("[INFO] Utilizator implicit creat -> utilizator: lucianadmin | parolă: lucian123")


if __name__ == "__main__":
    init_db()
    # debug=True este util pentru prezentare/dezvoltare; dezactivați în producție.
    app.run(debug=True, host="0.0.0.0", port=5000)
