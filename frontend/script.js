/* ================================================================
   Brain Checker — AI Feedback System
   Frontend JavaScript
   - Only Name + Service in form
   - Animated SVG face expression per star rating
   ================================================================ */

const API_BASE = window.location.origin;
const GOOGLE_REVIEWS_URL =
  "https://search.google.com/local/writereview?placeid=ChIJI_RUrxPr3TsRmbt6xgs5c-0";

// ── State ─────────────────────────────────────────────────────────
const state = {
  name: "", service: "", rating: 0,
  complaintText: "", reviewText: "",
};

const $ = (id) => document.getElementById(id);

// ── Step Navigation ───────────────────────────────────────────────
const allSteps = ["step-1","step-2-complaint","step-2-review","step-3"];

function showStep(id) {
  allSteps.forEach((s) => $(s).classList.remove("active"));
  $(id).classList.add("active");
}

function updateProgress(stepNum) {
  const dots  = [$("step-1-dot"), $("step-2-dot"), $("step-3-dot")];
  const lines = [$("step-line-1"), $("step-line-2")];
  dots.forEach((d, i) => {
    d.classList.remove("active","done");
    if (i + 1 === stepNum) d.classList.add("active");
    if (i + 1 < stepNum)   d.classList.add("done");
  });
  lines.forEach((l, i) => {
    l.classList.remove("active","done");
    if (i + 1 < stepNum)   l.classList.add("done");
    if (i + 1 === stepNum) l.classList.add("active");
  });
}

/* ================================================================
   ANIMATED FACE — expressions per star rating
   ================================================================ */

/*
  Face config per rating:
  - faceColor:   circle fill
  - strokeColor: circle stroke + body parts
  - animation:   CSS class to add (bounce / shake / tada)
  - label:       text under face
  - show/hide:   which mouth, eyes, extras to toggle
*/
const faceConfig = {
  0: {  // default/reset
    faceColor:   "#f0f0f0",
    strokeColor: "#e0e0e0",
    labelColor:  "var(--text-light)",
    labelText:   "How was it?",
    animation:   null,
    mouth:       "neutral",
    eyeStyle:    "normal",
    tears:       false,
    blush:       false,
    sparkles:    false,
    brows:       false,
  },
  1: {
    faceColor:   "#ffcdd2",     // light red
    strokeColor: "#e57373",
    labelColor:  "#c62828",
    labelText:   "Very Poor 😢",
    animation:   "shake",
    mouth:       "sad",
    eyeStyle:    "x",           // X eyes
    tears:       true,
    blush:       false,
    sparkles:    false,
    brows:       true,
  },
  2: {
    faceColor:   "#ffe0b2",     // light orange
    strokeColor: "#ff8a65",
    labelColor:  "#bf360c",
    labelText:   "Poor 😕",
    animation:   "bounce",
    mouth:       "sad",
    eyeStyle:    "normal",
    tears:       false,
    blush:       false,
    sparkles:    false,
    brows:       true,
  },
  3: {
    faceColor:   "#fff9c4",     // light yellow
    strokeColor: "#f9a825",
    labelColor:  "#f57f17",
    labelText:   "Average 😐",
    animation:   "bounce",
    mouth:       "neutral",
    eyeStyle:    "normal",
    tears:       false,
    blush:       false,
    sparkles:    false,
    brows:       false,
  },
  4: {
    faceColor:   "#c8e6c9",     // light green
    strokeColor: "#66bb6a",
    labelColor:  "#2e7d32",
    labelText:   "Good 😊",
    animation:   "bounce",
    mouth:       "smile-sm",
    eyeStyle:    "normal",
    tears:       false,
    blush:       true,
    sparkles:    false,
    brows:       false,
  },
  5: {
    faceColor:   "#b3e5fc",     // light blue
    strokeColor: "#29b6f6",
    labelColor:  "#01579b",
    labelText:   "Excellent! 🤩",
    animation:   "tada",
    mouth:       "laugh",
    eyeStyle:    "star",        // star eyes
    tears:       false,
    blush:       true,
    sparkles:    true,
    brows:       false,
  },
};

function applyFace(rating) {
  const cfg   = faceConfig[rating] || faceConfig[0];
  const svg   = $("face-svg");
  const label = $("face-label");

  // ── Face circle colour ────────────────────────────────────────
  const circle = $("face-circle");
  circle.setAttribute("fill",   cfg.faceColor);
  circle.setAttribute("stroke", cfg.strokeColor);

  // ── Mouth: show the right one ─────────────────────────────────
  const mouths = {
    "neutral":  $("mouth-neutral"),
    "sad":      $("mouth-sad"),
    "smile-sm": $("mouth-smile-sm"),
    "smile-lg": $("mouth-smile-lg"),
    "laugh":    $("mouth-laugh"),
  };
  Object.entries(mouths).forEach(([key, el]) => {
    el.setAttribute("opacity", key === cfg.mouth ? "1" : "0");
    el.setAttribute("stroke", cfg.strokeColor);
  });
  // The laugh mouth has a fill
  if (cfg.mouth === "laugh") {
    $("mouth-laugh").setAttribute("fill", "#ff8a80");
    $("mouth-laugh").setAttribute("stroke", cfg.strokeColor);
  }

  // ── Eyes ──────────────────────────────────────────────────────
  // Normal dots
  $("eye-l-dot").setAttribute("opacity", cfg.eyeStyle === "normal" ? "1" : "0");
  $("eye-r-dot").setAttribute("opacity", cfg.eyeStyle === "normal" ? "1" : "0");
  $("eye-l-dot").setAttribute("fill", cfg.strokeColor);
  $("eye-r-dot").setAttribute("fill", cfg.strokeColor);

  // Star eyes (5-star)
  $("eye-l-star").setAttribute("opacity", cfg.eyeStyle === "star" ? "1" : "0");
  $("eye-r-star").setAttribute("opacity", cfg.eyeStyle === "star" ? "1" : "0");

  // X eyes (1-star)
  $("eye-l-x").setAttribute("opacity", cfg.eyeStyle === "x" ? "1" : "0");
  $("eye-r-x").setAttribute("opacity", cfg.eyeStyle === "x" ? "1" : "0");
  $("eye-l-x").setAttribute("stroke", cfg.strokeColor);
  $("eye-r-x").setAttribute("stroke", cfg.strokeColor);

  // ── Sad brows ─────────────────────────────────────────────────
  const browOpacity = cfg.brows ? "1" : "0";
  $("eye-l-brow").setAttribute("opacity", browOpacity);
  $("eye-r-brow").setAttribute("opacity", browOpacity);
  $("eye-l-brow").setAttribute("stroke", cfg.strokeColor);
  $("eye-r-brow").setAttribute("stroke", cfg.strokeColor);

  // ── Extras ────────────────────────────────────────────────────
  $("tears").setAttribute("opacity",    cfg.tears    ? "1" : "0");
  $("blush").setAttribute("opacity",    cfg.blush    ? "1" : "0");
  $("sparkles").setAttribute("opacity", cfg.sparkles ? "1" : "0");

  // ── Label ─────────────────────────────────────────────────────
  label.textContent  = cfg.labelText;
  label.style.color  = cfg.labelColor;

  // ── Trigger animation ─────────────────────────────────────────
  if (cfg.animation) {
    svg.classList.remove("bounce","shake","tada");
    // Force reflow so CSS animation restarts
    void svg.offsetWidth;
    svg.classList.add(cfg.animation);
  }
}

/* ================================================================
   STAR RATING
   ================================================================ */
const ratingLabels = [
  "", "1 star — Very Poor", "2 stars — Poor",
  "3 stars — Average", "4 stars — Good", "5 stars — Excellent"
];
const starBtns = document.querySelectorAll(".star");

function paintStars(upTo) {
  starBtns.forEach((s) =>
    s.classList.toggle("hovered", parseInt(s.dataset.value) <= upTo)
  );
}

function selectStar(value) {
  state.rating = value;
  starBtns.forEach((s) => {
    const v = parseInt(s.dataset.value);
    s.classList.toggle("selected", v <= value);
    s.classList.remove("hovered");
  });
  $("rating-label").textContent = ratingLabels[value];
  applyFace(value);
}

starBtns.forEach((s) => {
  s.addEventListener("mouseenter", () => paintStars(parseInt(s.dataset.value)));
  s.addEventListener("mouseleave", () => paintStars(0));
  s.addEventListener("click",      () => selectStar(parseInt(s.dataset.value)));
  s.addEventListener("keydown",    (e) => {
    if (e.key === "Enter" || e.key === " ") selectStar(parseInt(s.dataset.value));
  });
});

/* ================================================================
   VALIDATION
   ================================================================ */
function setErr(id, msg) { const el=$(id); if(el) el.textContent = msg; }

function clearErrors() {
  ["err-name","err-service","err-rating"].forEach((id) => setErr(id, ""));
  ["inp-name","inp-service"].forEach((id) => $(id).classList.remove("error"));
}

function validateStep1() {
  clearErrors();
  let valid = true;

  if (!$("inp-name").value.trim()) {
    setErr("err-name", "Please enter your full name.");
    $("inp-name").classList.add("error"); valid = false;
  }
  if (!$("inp-service").value.trim()) {
    setErr("err-service", "Please enter the service or test taken.");
    $("inp-service").classList.add("error"); valid = false;
  }
  if (!state.rating) {
    setErr("err-rating", "Please select a star rating.");
    valid = false;
  }
  return valid;
}

// Live clear — name uses input event, service (now a select) uses change event
$("inp-name").addEventListener("input", () => {
  $("inp-name").classList.remove("error");
  setErr("err-name", "");
});
$("inp-service").addEventListener("change", () => {
  $("inp-service").classList.remove("error");
  setErr("err-service", "");
});

/* ================================================================
   CHAR COUNTER
   ================================================================ */
$("inp-complaint").addEventListener("input", function() {
  $("char-count").textContent = this.value.length;
});

/* ================================================================
   STEP 1 → STEP 2
   ================================================================ */
$("btn-step1-next").addEventListener("click", () => {
  if (!validateStep1()) return;

  state.name    = $("inp-name").value.trim();
  state.service = $("inp-service").value.trim();

  if (state.rating <= 3) {
    // Complaint path
    updateProgress(2);
    showStep("step-2-complaint");
  } else {
    // Review path
    updateProgress(2);
    showStep("step-2-review");
    $("review-box").classList.add("hidden");
    $("ai-error").classList.add("hidden");
    $("ai-loading").classList.remove("hidden");
    generateAIReview();
  }
});

/* ================================================================
   AI REVIEW GENERATION
   ================================================================ */
async function generateAIReview() {
  try {
    const res = await fetch(`${API_BASE}/generate-review`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name:    state.name,
        service: state.service,
        rating:  state.rating,
      }),
    });

    if (!res.ok) {
      const d = await res.json().catch(() => ({}));
      throw new Error(d.detail || `Error ${res.status}`);
    }

    const data = await res.json();
    state.reviewText = data.review;

    $("ai-loading").classList.add("hidden");
    $("ai-error").classList.add("hidden");
    $("inp-review").value = state.reviewText;
    $("review-box").classList.remove("hidden");

  } catch (err) {
    console.error("[AI]", err);
    $("ai-loading").classList.add("hidden");
    $("review-box").classList.add("hidden");
    $("ai-error").classList.remove("hidden");
  }
}

$("btn-ai-retry").addEventListener("click", () => {
  $("ai-error").classList.add("hidden");
  $("ai-loading").classList.remove("hidden");
  generateAIReview();
});

/* ================================================================
   COMPLAINT FLOW
   ================================================================ */
$("btn-complaint-back").addEventListener("click", () => {
  updateProgress(1); showStep("step-1");
});

$("btn-complaint-submit").addEventListener("click", async () => {
  const msg = $("inp-complaint").value.trim();
  if (!msg) {
    setErr("err-complaint", "Please describe your complaint.");
    $("inp-complaint").classList.add("error"); return;
  }
  state.complaintText = msg;
  toggleBtn("btn-complaint-submit", "spinner-complaint", true);

  try {
    const res = await fetch(`${API_BASE}/submit-feedback`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name:          state.name,
        service:       state.service,
        rating:        state.rating,
        message:       state.complaintText,
        feedback_type: "complaint",
      }),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);

    // ✅ "Review Submitted" as requested
    $("success-title").textContent   = "Review Submitted!";
    $("success-message").textContent =
      "Thank you for your feedback. Our team will review it and get back to you shortly.";
    $("copy-section").classList.add("hidden");
    updateProgress(3);
    showStep("step-3");

  } catch (err) {
    console.error(err);
    showToast("⚠ Submission failed. Please try again.");
  } finally {
    toggleBtn("btn-complaint-submit", "spinner-complaint", false);
  }
});

/* ================================================================
   REVIEW FLOW
   ================================================================ */
$("btn-review-back").addEventListener("click", () => {
  updateProgress(1); showStep("step-1");
});

$("btn-review-submit").addEventListener("click", async () => {
  const txt = $("inp-review").value.trim();
  if (!txt) { showToast("Review text cannot be empty."); return; }

  state.reviewText = txt;
  toggleBtn("btn-review-submit", "spinner-review", true);

  try {
    const res = await fetch(`${API_BASE}/submit-feedback`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name:          state.name,
        service:       state.service,
        rating:        state.rating,
        message:       state.reviewText,
        feedback_type: "review",
      }),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);

    // ✅ "Review Submitted" for reviews too
    $("success-title").textContent   = "Review Submitted! 🎉";
    $("success-message").textContent =
      "Thank you! Copy your review below and paste it on Google Reviews to help others.";
    $("copy-preview").textContent = state.reviewText;
    $("copy-section").classList.remove("hidden");
    updateProgress(3);
    showStep("step-3");
    startCountdown();

  } catch (err) {
    console.error(err);
    showToast("⚠ Submission failed. Please try again.");
  } finally {
    toggleBtn("btn-review-submit", "spinner-review", false);
  }
});

/* ================================================================
   COPY & COUNTDOWN
   ================================================================ */
$("btn-copy").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(state.reviewText); }
  catch {
    const ta = document.createElement("textarea");
    ta.value = state.reviewText;
    document.body.appendChild(ta); ta.select();
    document.execCommand("copy"); document.body.removeChild(ta);
  }
  $("btn-copy").classList.add("copied");
  $("copy-btn-text").textContent = "✓ Copied!";
  showToast("✓ Review copied to clipboard!");
  setTimeout(() => {
    $("btn-copy").classList.remove("copied");
    $("copy-btn-text").textContent = "Copy Review";
  }, 3000);
});

let countdownTimer = null;
function startCountdown() {
  let s = 5; $("countdown").textContent = s;
  clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    s--; $("countdown").textContent = s;
    if (s <= 0) { clearInterval(countdownTimer); window.open(GOOGLE_REVIEWS_URL, "_blank"); }
  }, 1000);
}

/* ================================================================
   RESTART
   ================================================================ */
$("btn-restart").addEventListener("click", () => {
  Object.keys(state).forEach((k) => (state[k] = k === "rating" ? 0 : ""));
  $("inp-name").value      = "";
  $("inp-service").value   = "";   // resets the select to "— Select a service —"
  $("inp-complaint").value = "";
  $("inp-review").value    = "";
  $("char-count").textContent = "0";
  clearErrors();
  starBtns.forEach((s) => s.classList.remove("selected","hovered"));
  $("rating-label").textContent = "Tap a star to rate";
  applyFace(0);   // reset face
  clearInterval(countdownTimer);
  updateProgress(1);
  showStep("step-1");
});

/* ================================================================
   HELPERS
   ================================================================ */
function toggleBtn(btnId, spinId, loading) {
  $(btnId).disabled = loading;
  $(spinId).classList.toggle("hidden", !loading);
}

let toastTimer = null;
function showToast(msg) {
  let t = document.querySelector(".toast");
  if (!t) { t = document.createElement("div"); t.className = "toast"; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 3000);
}

/* ── Init ────────────────────────────────────────────────────────*/
updateProgress(1);
showStep("step-1");
applyFace(0);
console.log("[Brain Checker] ✅ Ready.");
