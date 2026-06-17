/* ==========================================================================
   main.js
   Portalul de Petiții și Sesizări - Primăria Bălănești
   Interacțiuni front-end: previzualizare fotografie, validare client-side
   ușoară, confirmare la schimbarea statusului, dismiss automat alerte.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {

  // ---- Previzualizare fotografie la încărcare (formular petiție) ----
  const inputFoto = document.getElementById("fotografie");
  const previewFoto = document.getElementById("previewFotografie");

  if (inputFoto && previewFoto) {
    inputFoto.addEventListener("change", function () {
      const fisier = inputFoto.files && inputFoto.files[0];
      if (!fisier) {
        previewFoto.style.display = "none";
        return;
      }
      const tipuriPermise = ["image/png", "image/jpeg", "image/gif"];
      if (!tipuriPermise.includes(fisier.type)) {
        previewFoto.style.display = "none";
        return;
      }
      const cititor = new FileReader();
      cititor.onload = function (e) {
        previewFoto.src = e.target.result;
        previewFoto.style.display = "block";
      };
      cititor.readAsDataURL(fisier);
    });
  }

  // ---- Activare validare Bootstrap pe formulare cu clasa "needs-validation" ----
  const formulare = document.querySelectorAll(".needs-validation");
  Array.prototype.slice.call(formulare).forEach(function (form) {
    form.addEventListener("submit", function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    }, false);
  });

  // ---- Auto-închidere alerte de tip "flash" după câteva secunde ----
  document.querySelectorAll(".alert.alert-dismissible.pb-autohide").forEach(function (alertEl) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      bsAlert.close();
    }, 6000);
  });

  // ---- Confirmare înainte de a trimite un răspuns oficial / schimba statusul ----
  const formActualizare = document.getElementById("formActualizarePetitie");
  if (formActualizare) {
    formActualizare.addEventListener("submit", function (e) {
      const raspuns = document.getElementById("raspuns");
      if (raspuns && raspuns.value.trim().length > 0) {
        const confirmat = window.confirm(
          "Confirmați trimiterea acestui răspuns către cetățean? Răspunsul va deveni vizibil imediat."
        );
        if (!confirmat) {
          e.preventDefault();
        }
      }
    });
  }

  // ---- Copiere rapidă a numărului de înregistrare în clipboard ----
  const butoaneCopiere = document.querySelectorAll(".pb-copy-reg");
  butoaneCopiere.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const text = btn.getAttribute("data-reg");
      if (navigator.clipboard && text) {
        navigator.clipboard.writeText(text).then(function () {
          const originalText = btn.innerHTML;
          btn.innerHTML = '<i class="bi bi-check2"></i> Copiat!';
          setTimeout(function () { btn.innerHTML = originalText; }, 1800);
        });
      }
    });
  });

});
