/* ==========================================================================
   Lendvue — Site JS
   Mobile nav, modal system, multi-step forms, AJAX submission to
   /api/submit-form (Cloudflare Pages Function -> email via Resend).
   No jQuery, no UIkit, no build step.
   ========================================================================== */
(function () {
  "use strict";

  /* ---------------- Mobile nav ---------------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");
  var scrim = document.querySelector(".nav-scrim");

  function closeNav() {
    if (!nav) return;
    nav.classList.remove("is-open");
    if (scrim) scrim.classList.remove("is-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }
  function openNav() {
    if (!nav) return;
    nav.classList.add("is-open");
    if (scrim) scrim.classList.add("is-open");
    if (toggle) toggle.setAttribute("aria-expanded", "true");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      nav.classList.contains("is-open") ? closeNav() : openNav();
    });
  }
  if (scrim) scrim.addEventListener("click", closeNav);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeNav();
  });

  /* ---------------- Modal system ----------------
     Trigger:  <button data-modal-open="equipment-quote">...</button>
     Modal:    <div class="modal-overlay" id="modal-equipment-quote" data-modal>
  ------------------------------------------------- */
  var openModalEl = null;

  function openModal(id) {
    var modal = document.getElementById("modal-" + id);
    if (!modal) return;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    openModalEl = modal;
    var firstField = modal.querySelector(".form-step.is-active input:not(.honeypot), form input:not(.honeypot), select, textarea, button");
    if (firstField) firstField.focus();
  }
  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    openModalEl = null;
  }
  document.addEventListener("click", function (e) {
    var opener = e.target.closest("[data-modal-open]");
    if (opener) {
      e.preventDefault();
      openModal(opener.getAttribute("data-modal-open"));
      return;
    }
    var closer = e.target.closest("[data-modal-close]");
    if (closer) {
      e.preventDefault();
      closeModal(closer.closest(".modal-overlay"));
      return;
    }
    if (e.target.classList && e.target.classList.contains("modal-overlay")) {
      closeModal(e.target);
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && openModalEl) closeModal(openModalEl);
  });

  var HASH_MODALS = { "#equipmentfinancing": "equipment-quote", "#equipment-quote": "equipment-quote",
                      "#workingcapital": "working-capital", "#working-capital": "working-capital" };
  if (HASH_MODALS[window.location.hash]) openModal(HASH_MODALS[window.location.hash]);

  /* ---------------- Multi-step forms ----------------
     Wrap steps in <div class="form-step" data-step="1">, use
     [data-step-next] / [data-step-prev] buttons to move between them.
  ------------------------------------------------- */
  document.querySelectorAll("form[data-multistep]").forEach(function (form) {
    var steps = Array.prototype.slice.call(form.querySelectorAll(".form-step"));
    var indicatorDots = Array.prototype.slice.call(form.querySelectorAll(".step-indicator span"));
    var current = 0;

    function show(index) {
      steps.forEach(function (s, i) { s.classList.toggle("is-active", i === index); });
      indicatorDots.forEach(function (d, i) { d.classList.toggle("is-active", i <= index); });
      current = index;
    }
    function stepValid(step) {
      var bad = [];
      step.querySelectorAll("input, select, textarea").forEach(function (f) {
        if (f.classList.contains("honeypot") || f.type === "hidden") return;
        var invalid = !f.checkValidity();
        f.classList.toggle("is-invalid", invalid);
        f.setAttribute("aria-invalid", invalid ? "true" : "false");
        if (invalid) bad.push(f);
      });
      if (bad.length) {
        var status = form.querySelector(".form-status");
        if (status) {
          status.textContent = bad[0].validity.rangeUnderflow
            ? "Please enter a value of at least " + Number(bad[0].min).toLocaleString() + "."
            : "Please fill out all required fields.";
          status.className = "form-status is-visible error";
        }
        bad[0].focus();
        return false;
      }
      var st = form.querySelector(".form-status");
      if (st) st.className = "form-status";
      return true;
    }
    // Like Gravity Forms "partial entries": email the step-1 contact details as soon as
    // they're entered, so an abandoned step 2 still leaves a lead in the inbox.
    function sendPartial() {
      if (!form.hasAttribute("data-partial-step1") || form.dataset.partialSent) return;
      var hp = form.querySelector('input[name="website"]');
      if (hp && hp.value) return;
      var payload = { formName: (form.getAttribute("data-ajax-form") || "Form") + " (step 1 of 2 - partial)", pageUrl: window.location.href };
      steps[0].querySelectorAll("input, select, textarea").forEach(function (f) {
        if (!f.name || f.name === "website") return;
        if (f.type === "checkbox") { if (f.checked) payload[f.name] = f.value; return; }
        payload[f.name] = f.value;
      });
      form.dataset.partialSent = "1";
      fetch("/api/submit-form", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), keepalive: true })
        .catch(function () { delete form.dataset.partialSent; });
    }
    form.addEventListener("click", function (e) {
      var next = e.target.closest("[data-step-next]");
      var prev = e.target.closest("[data-step-prev]");
      if (next) {
        e.preventDefault();
        if (!stepValid(steps[current])) return;
        if (current === 0) sendPartial();
        if (current < steps.length - 1) show(current + 1);
        var box = form.closest(".modal-box"); if (box) box.scrollTop = 0;
      }
      if (prev) {
        e.preventDefault();
        if (current > 0) show(current - 1);
      }
    });
    show(0);
  });

  /* ---------------- AJAX form submission ---------------- */
  function setStatus(form, type, message) {
    var status = form.querySelector(".form-status");
    if (!status) return;
    status.textContent = message;
    status.className = "form-status is-visible " + type;
  }

  document.querySelectorAll("form[data-ajax-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      // Honeypot spam check
      var honeypot = form.querySelector('input[name="website"]');
      if (honeypot && honeypot.value) return;

      // Validate required fields / min values (forms use novalidate for custom styling)
      var invalid = [];
      form.querySelectorAll("input, select, textarea").forEach(function (f) {
        if (f.classList.contains("honeypot") || f.type === "hidden") return;
        var bad = !f.checkValidity();
        f.classList.toggle("is-invalid", bad);
        f.setAttribute("aria-invalid", bad ? "true" : "false");
        if (bad) invalid.push(f);
      });
      if (invalid.length) {
        var first = invalid[0];
        var msg = first.validity.rangeUnderflow
          ? "Please enter a value of at least " + Number(first.min).toLocaleString() + "."
          : "Please fill out all required fields.";
        setStatus(form, "error", msg);
        first.focus();
        return;
      }

      var submitBtns = form.querySelectorAll('button[type="submit"]');
      submitBtns.forEach(function (b) { b.disabled = true; b.dataset.originalText = b.textContent; b.textContent = "Sending..."; });

      var formData = new FormData(form);
      var payload = {};
      formData.forEach(function (value, key) { payload[key] = value; });
      payload.formName = form.getAttribute("data-ajax-form") || "General Inquiry";
      payload.pageUrl = window.location.href;

      fetch("/api/submit-form", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          if (!res.ok) throw new Error("Request failed");
          return res.json();
        })
        .then(function () {
          var redirect = form.getAttribute("data-redirect");
          if (redirect) {
            window.location.href = redirect;
          } else {
            setStatus(form, "success", "Thanks! Your information has been received — we'll be in touch shortly.");
            form.reset();
          }
        })
        .catch(function () {
          setStatus(form, "error", "Something went wrong sending your info. Please call us at 800-866-7231 or try again.");
        })
        .finally(function () {
          submitBtns.forEach(function (b) { b.disabled = false; b.textContent = b.dataset.originalText; });
        });
    });
  });

  /* ---------------- Current year in footer ---------------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
