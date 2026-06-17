# Portalul de Petiții și Sesizări - Primăria Bălănești

Aplicație web completă pentru depunerea și gestionarea petițiilor/sesizărilor
cetățenilor din satul Bălănești, raionul Nisporeni, Republica Moldova.

* **Backend:** Python 3 + Flask
* **ORM / Bază de date:** SQLAlchemy (prin Flask-SQLAlchemy) + SQLite
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons, Chart.js

---

## 1. Structura proiectului

```
balanesti-petitii/
├── app.py                     # Aplicația Flask: rute, logică, autentificare
├── models.py                  # Modelele SQLAlchemy (User, Petition)
├── requirements.txt           # Dependențe Python
├── database.db                # Generat automat la prima rulare (SQLite)
├── templates/
│   ├── layouts/
│   │   └── base.html          # Layout comun: navbar, footer, mesaje flash
│   ├── index.html              # Pagina principală
│   ├── login.html              # Autentificare funcționari
│   ├── dashboard.html          # Dashboard administrator + grafice Chart.js
│   ├── petition_form.html      # Formular depunere petiție
│   ├── petition_details.html   # Detalii petiție + răspuns oficial (admin)
│   ├── manage_petitions.html   # Listă/filtrare petiții (admin)
│   ├── status_check.html       # Verificare status (cetățeni)
│   └── confirmation.html       # Confirmare după depunere petiție
└── static/
    ├── css/style.css           # Stiluri proprii (paleta Bălănești)
    ├── js/main.js               # Previzualizare foto, validări, mici interacțiuni
    ├── images/logo.svg          # Emblemă generică Primăria Bălănești
    └── uploads/                 # Fotografiile încărcate de cetățeni (generat automat)
```

## 2. Instalare

Necesită Python 3.10 sau mai recent.

```bash
# 1. Creează un mediu virtual (recomandat)
python -m venv venv

# 2. Activează mediul virtual
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalează dependențele
pip install -r requirements.txt
```

## 3. Pornire

```bash
python app.py
```

La prima rulare, aplicația:
* creează automat fișierul `database.db` cu tabelele `users` și `petitions`;
* creează automat contul implicit de administrator.

Aplicația va fi disponibilă la adresa: **http://127.0.0.1:5000**

### Cont implicit de administrator

| Utilizator | Parolă     |
|------------|------------|
| `lucianadmin`    | `lucian123` |

Parola este stocată în baza de date exclusiv sub formă de hash
(`werkzeug.security.generate_password_hash`), niciodată în clar.

> Recomandare: schimbați parola implicită și valoarea `SECRET_KEY` din
> `app.py` înainte de orice utilizare în afara mediului de prezentare/testare.

## 4. Funcționalități

### Pentru cetățeni
* Pagina principală cu prezentarea platformei și acces rapid la formular.
* Formular de depunere petiție cu: nume, email, telefon, adresă, categorie,
  prioritate, descriere și fotografie opțională (PNG/JPG/GIF, max. 5 MB).
* Generare automată a unui număr unic de înregistrare (format `BAL-AAAA-NNNN`).
* Verificare status după numărul de înregistrare: status curent, răspunsul
  primăriei (dacă există) și data ultimei actualizări.

### Pentru funcționarii primăriei
* Autentificare securizată (sesiune Flask + parolă hash-uită).
* Dashboard cu carduri de statistici (total, noi, în lucru, rezolvate) și
  trei grafice Chart.js (pe categorii, priorități și statusuri).
* Listă completă a petițiilor, cu filtrare după categorie, status sau
  cetățean (nume/email/telefon/număr de înregistrare).
* Pagină de detalii petiție: vizualizare completă, schimbare status
  (Înregistrată / În analiză / În lucru / Rezolvată / Respinsă) și redactare
  răspuns oficial, vizibil imediat cetățeanului.

## 5. Note tehnice

* Numărul de înregistrare se generează automat în formatul `BAL-<an>-<NNNN>`,
  cu secvența reluată de la `0001` în fiecare an calendaristic.
* Fotografiile încărcate sunt salvate cu un nume unic (UUID) în
  `static/uploads/`, pentru a evita coliziunile de nume.
* Pentru reinițializarea completă a bazei de date (ex. pentru o nouă
  prezentare), ștergeți fișierul `database.db` și porniți din nou `app.py`.
