(function () {
  "use strict";

  // ------------------------------------------------------------ translations
  var I18N = {
    ta: {
      brandSub: "படி · பார் · பிறகு கையெழுத்திடு",
      navAnalyse: "பகுப்பாய்வு", navCompare: "ஒப்பீடு", navAbout: "பற்றி",
      heroTitle: "படித்துப் பார்; பிறகு கையெழுத்திடு",
      heroSub: "விதிமுறைகள், கடன் ஒப்பந்தங்கள், ஆப் அனுமதிகள் - ஆபத்தான பகுதிகளைத் தமிழில் எளிமையாக விளக்குகிறோம்.",
      tabText: "உரையை ஒட்டவும்", tabUrl: "இணைய முகவரி", tabPdf: "PDF பதிவேற்றம்",
      phText: "இங்கே விதிமுறைகள் (Terms & Conditions) அல்லது ஒப்பந்த உரையை ஒட்டவும்...",
      hintUrl: "பொது விதிமுறைப் பக்கத்தின் முகவரியை மட்டும் கொடுக்கவும். வேலை செய்யவில்லை என்றால் உரையை ஒட்டவும்.",
      phPdf: "PDF கோப்பைத் தேர்வு செய்ய இங்கே தொடவும்",
      btnAnalyse: "பகுப்பாய்வு செய்", btnClear: "அழி", trySample: "மாதிரி முயற்சி:",
      loading: "ஆவணத்தைப் படித்துக்கொண்டிருக்கிறோம்...",
      errEmpty: "முதலில் உரை, இணைய முகவரி அல்லது PDF கொடுக்கவும்.",
      errNet: "சேவையுடன் இணைக்க முடியவில்லை. சற்று நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.",
      scoreLabel: "ஆபத்து மதிப்பெண்",
      statClauses: "படித்த விதிகள்", statFlagged: "எச்சரிக்கை உள்ளவை",
      band: { Low: "குறைவு", Medium: "நடுத்தரம்", High: "அதிகம்" },
      uiTitle: "பக்க வடிவமைப்பு எச்சரிக்கைகள்", findTitle: "கவனிக்க வேண்டிய விதிகள்",
      original: "மூல விதி", tip: "என்ன செய்யலாம்", noFindings: "குறிப்பிடத்தக்க எச்சரிக்கை எதுவும் கண்டறியப்படவில்லை.",
      srcRule: "விதி", srcMl: "AI", srcBoth: "விதி + AI", conf: "நம்பிக்கை",
      compareTitle: "ஆப் ஆபத்து ஒப்பீடு",
      compareNote: "கீழுள்ள மாதிரிப் பதிவுகள் செயல்விளக்கத்துக்கானவை; அவை உண்மையான நிறுவனங்கள் அல்ல.",
      filterLabel: "வகை:", allCats: "அனைத்தும்",
      thApp: "ஆப்", thCategory: "வகை", thScore: "மதிப்பெண்", thTop: "முக்கிய ஆபத்துகள்", thDate: "தேதி",
      sampleTag: "மாதிரி", emptyScores: "பதிவுகள் எதுவும் இல்லை.",
      aboutTitle: "இது எப்படி வேலை செய்கிறது?",
      steps: [
        "நீங்கள் உரையை ஒட்டலாம், இணைய முகவரி தரலாம் அல்லது PDF பதிவேற்றலாம்.",
        "ஆவணம் தனித்தனி விதிகளாகப் பிரிக்கப்படுகிறது.",
        "ஒவ்வொரு விதியையும் விதி-அடிப்படை (rules) மற்றும் இயந்திரக் கற்றல் (AI) மாதிரி இரண்டும் சோதிக்கின்றன.",
        "மொத்த ஆபத்து மதிப்பெண் (0-100) கணக்கிடப்பட்டு, ஒவ்வொரு எச்சரிக்கையும் தமிழில் விளக்கப்படுகிறது; மூல விதியும் உடனே காட்டப்படுகிறது."
      ],
      privacyTitle: "தனியுரிமை",
      privacyText: "நீங்கள் கொடுக்கும் ஆவணங்கள் சேமிக்கப்படுவதில்லை. அவை உடனே பகுப்பாய்வு செய்யப்பட்டு முடிவு மட்டும் உங்களுக்குக் காட்டப்படும்.",
      modelTitle: "மாடல் தகவல்", extTitle: "உலாவி நீட்சி (Extension)",
      extText: "இத்திட்டத்தில் உள்ள extension கோப்புறையை Chrome / Brave-இல் 'Load unpacked' மூலம் சேர்த்தால், பதிவுப் பக்கத்திலேயே மதிப்பெண்ணைப் பார்க்கலாம்.",
      f1: "மேக்ரோ F1 (சிறு seed தரவு, cross-validation)", footer: "PadiPaar - ஆபத்துகளைச் சுட்டிக்காட்டும் கருவி; இது சட்ட ஆலோசனை அல்ல."
    },
    en: {
      brandSub: "Read. See. Then sign.",
      navAnalyse: "Analyse", navCompare: "Compare", navAbout: "About",
      heroTitle: "Read what you sign",
      heroSub: "Terms, loan agreements and app permissions - the risky parts, explained in simple Tamil.",
      tabText: "Paste text", tabUrl: "Web address", tabPdf: "Upload PDF",
      phText: "Paste the terms and conditions or agreement text here...",
      hintUrl: "Enter the address of a public terms page. If it does not work, paste the text instead.",
      phPdf: "Tap here to choose a PDF file",
      btnAnalyse: "Analyse", btnClear: "Clear", trySample: "Try a sample:",
      loading: "Reading the document...",
      errEmpty: "Please provide text, a web address or a PDF first.",
      errNet: "Could not reach the service. Please try again in a moment.",
      scoreLabel: "Risk score",
      statClauses: "Clauses read", statFlagged: "Clauses flagged",
      band: { Low: "Low", Medium: "Medium", High: "High" },
      uiTitle: "Page design warnings", findTitle: "Clauses to watch",
      original: "Original clause", tip: "What you can do", noFindings: "No notable warning signs were found.",
      srcRule: "Rule", srcMl: "AI", srcBoth: "Rule + AI", conf: "confidence",
      compareTitle: "App risk comparison",
      compareNote: "The entries below are demo samples for illustration; they are not real companies.",
      filterLabel: "Category:", allCats: "All",
      thApp: "App", thCategory: "Category", thScore: "Score", thTop: "Top risks", thDate: "Date",
      sampleTag: "sample", emptyScores: "No entries yet.",
      aboutTitle: "How it works",
      steps: [
        "Paste text, enter a web address, or upload a PDF.",
        "The document is split into individual clauses.",
        "Each clause is checked by both a rule engine and a machine-learning (AI) model.",
        "A 0-100 risk score is computed and every warning is explained in Tamil, with the original clause shown right beside it."
      ],
      privacyTitle: "Privacy",
      privacyText: "Your documents are not stored. They are analysed immediately and only the result is shown to you.",
      modelTitle: "Model information", extTitle: "Browser extension",
      extText: "Load the extension folder from this project in Chrome or Brave using 'Load unpacked' to see the score right on a sign-up page.",
      f1: "Macro F1 (small seed set, cross-validation)", footer: "PadiPaar highlights possible risks. It is not legal advice."
    }
  };

  var CATEGORY_LABEL = {
    loan: { ta: "கடன்", en: "Loan" }, streaming: { ta: "ஸ்ட்ரீமிங்", en: "Streaming" },
    productivity: { ta: "உற்பத்தித்திறன்", en: "Productivity" }
  };

  var state = { cats: [], lang: "ta", mode: "text", view: "analyse", result: null, scores: [], pdfFile: null, samples: [], lastDisclaimer: null };

  function t(key) { return I18N[state.lang][key]; }
  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }
  function pick(obj, base) { return obj[base + "_" + state.lang]; }
  function catLabel(c) { var m = CATEGORY_LABEL[c]; return m ? m[state.lang] : c; }

  // ------------------------------------------------------------ static text
  function applyStaticText() {
    document.documentElement.lang = state.lang === "ta" ? "ta" : "en";
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n]"), function (n) {
      var v = t(n.getAttribute("data-i18n"));
      if (typeof v === "string") n.textContent = v;
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-i18n-ph]"), function (n) {
      n.setAttribute("placeholder", t(n.getAttribute("data-i18n-ph")));
    });
    var steps = $("about-steps");
    steps.textContent = "";
    t("steps").forEach(function (s) { steps.appendChild(el("li", null, s)); });
    $("lang-ta").classList.toggle("active", state.lang === "ta");
    $("lang-en").classList.toggle("active", state.lang === "en");
    if (state.pdfFile) $("pdf-name").textContent = state.pdfFile.name;
    var d = state.lastDisclaimer;
    $("disclaimer-line").textContent = d ? d[state.lang] : "";
  }

  // ------------------------------------------------------------ highlight
  function appendHighlighted(container, text, phrases) {
    var ranges = [];
    var lower = text.toLowerCase();
    (phrases || []).forEach(function (p) {
      if (!p) return;
      var needle = p.toLowerCase().trim();
      if (!needle) return;
      var idx = lower.indexOf(needle);
      if (idx >= 0) ranges.push([idx, idx + needle.length]);
    });
    ranges.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [];
    ranges.forEach(function (r) {
      var last = merged[merged.length - 1];
      if (last && r[0] <= last[1]) { last[1] = Math.max(last[1], r[1]); } else { merged.push([r[0], r[1]]); }
    });
    var pos = 0;
    merged.forEach(function (r) {
      if (r[0] > pos) container.appendChild(document.createTextNode(text.slice(pos, r[0])));
      container.appendChild(el("mark", null, text.slice(r[0], r[1])));
      pos = r[1];
    });
    if (pos < text.length) container.appendChild(document.createTextNode(text.slice(pos)));
  }

  // ------------------------------------------------------------ result rendering
  function severityClass(conf) { return conf >= 0.85 ? "sev-high" : conf >= 0.6 ? "" : "sev-low"; }

  function renderResult() {
    var box = $("result");
    var r = state.result;
    box.textContent = "";
    if (!r) { box.classList.add("hidden"); return; }
    box.classList.remove("hidden");
    state.lastDisclaimer = r.disclaimer;

    // summary card
    var card = el("div", "card");
    var sum = el("div", "summary");
    var ring = el("div", "ring band-" + r.band);
    ring.style.setProperty("--p", String(r.score));
    var inner = el("div", "ring-inner");
    inner.appendChild(el("div", "ring-score", String(r.score)));
    inner.appendChild(el("div", "ring-label", t("scoreLabel")));
    ring.appendChild(inner);
    sum.appendChild(ring);

    var txt = el("div", "summary-text");
    txt.appendChild(el("span", "band-pill band-" + r.band, t("band")[r.band]));
    txt.appendChild(el("div", null, pick(r.summary, "summary")));
    var stats = el("div", "stats");
    var s1 = el("span"); s1.appendChild(document.createTextNode(t("statClauses") + ": ")); s1.appendChild(el("b", null, String(r.clause_count)));
    var s2 = el("span"); s2.appendChild(document.createTextNode(t("statFlagged") + ": ")); s2.appendChild(el("b", null, String(r.flagged_clauses)));
    stats.appendChild(s1); stats.appendChild(s2);
    txt.appendChild(stats);
    if (r.categories.length) {
      var chips = el("div", "cat-chips");
      r.categories.forEach(function (c) { chips.appendChild(el("span", "cat-chip", pick(c, "title"))); });
      txt.appendChild(chips);
    }
    sum.appendChild(txt);
    card.appendChild(sum);
    box.appendChild(card);

    // UI (dark pattern) warnings
    if (r.ui_findings && r.ui_findings.length) {
      box.appendChild(el("h3", "section-title", t("uiTitle")));
      r.ui_findings.forEach(function (u) {
        var c = el("div", "card finding sev-high");
        c.appendChild(el("div", "finding-title", pick(u, "title")));
        c.appendChild(el("p", "meaning", pick(u, "meaning")));
        var tip = el("div", "tip"); tip.appendChild(el("b", null, t("tip") + ": ")); tip.appendChild(document.createTextNode(pick(u, "tip")));
        c.appendChild(tip);
        if (u.text) { var cb = el("div", "clause-box"); cb.appendChild(document.createTextNode(u.text)); c.appendChild(cb); }
        box.appendChild(c);
      });
    }

    // clause findings
    box.appendChild(el("h3", "section-title", t("findTitle")));
    if (!r.findings.length) {
      box.appendChild(el("div", "ok-box", t("noFindings")));
    }
    r.findings.forEach(function (f) {
      var c = el("div", "card finding " + severityClass(f.confidence));
      var head = el("div", "finding-head");
      head.appendChild(el("span", "finding-title", pick(f, "title")));
      var srcKey = f.source === "both" ? "srcBoth" : f.source === "rule" ? "srcRule" : "srcMl";
      head.appendChild(el("span", "badge", t(srcKey)));
      head.appendChild(el("span", "badge", t("conf") + " " + Math.round(f.confidence * 100) + "%"));
      c.appendChild(head);
      c.appendChild(el("p", "meaning", pick(f, "meaning")));
      if (f.details && f.details.length) {
        var d = el("div");
        f.details.forEach(function (x) { d.appendChild(el("span", "detail-tag", x)); });
        c.appendChild(d);
      }
      var tip = el("div", "tip"); tip.appendChild(el("b", null, t("tip") + ": ")); tip.appendChild(document.createTextNode(pick(f, "tip")));
      c.appendChild(tip);
      var cb = el("div", "clause-box");
      cb.appendChild(el("span", "clause-label", t("original")));
      appendHighlighted(cb, f.clause, f.highlights);
      c.appendChild(cb);
      box.appendChild(c);
    });

    box.appendChild(el("p", "disclaimer", r.disclaimer[state.lang]));
    $("disclaimer-line").textContent = r.disclaimer[state.lang];
  }

  // ------------------------------------------------------------ status helpers
  function setStatus(kind, msg) {
    var s = $("status");
    s.textContent = "";
    s.className = "status" + (kind ? " " + kind : "");
    if (kind === "loading") { s.appendChild(el("span", "spinner")); }
    if (msg) s.appendChild(document.createTextNode(msg));
  }

  function fetchJson(url, opts) {
    return fetch(url, opts).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (data) {
        if (!res.ok) { throw new Error(data.error || ("HTTP " + res.status)); }
        return data;
      });
    });
  }

  // ------------------------------------------------------------ analyse
  var busy = false;
  function analyse(overrideText) {
    if (busy) return;
    var req;
    if (typeof overrideText === "string") {
      req = { url: "/api/analyze", opts: { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: overrideText }) } };
    } else if (state.mode === "text") {
      var v = $("text-input").value.trim();
      if (!v) return setStatus("error", t("errEmpty"));
      req = { url: "/api/analyze", opts: { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: v }) } };
    } else if (state.mode === "url") {
      var u = $("url-input").value.trim();
      if (!u) return setStatus("error", t("errEmpty"));
      req = { url: "/api/analyze", opts: { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ url: u }) } };
    } else {
      if (!state.pdfFile) return setStatus("error", t("errEmpty"));
      var fd = new FormData(); fd.append("file", state.pdfFile);
      req = { url: "/api/analyze/pdf", opts: { method: "POST", body: fd } };
    }
    busy = true;
    $("analyse-btn").disabled = true;
    setStatus("loading", t("loading"));
    fetchJson(req.url, req.opts).then(function (data) {
      state.result = data;
      setStatus("", "");
      renderResult();
      $("result").scrollIntoView({ behavior: "smooth", block: "start" });
    }).catch(function (err) {
      var m = err && err.message ? err.message : t("errNet");
      if (m === "Failed to fetch" || m === "NetworkError when attempting to fetch resource.") m = t("errNet");
      setStatus("error", m);
    }).then(function () { busy = false; $("analyse-btn").disabled = false; });
  }

  // ------------------------------------------------------------ views, tabs
  function showView(name) {
    state.view = name;
    ["analyse", "compare", "about"].forEach(function (v) { $("view-" + v).classList.toggle("hidden", v !== name); });
    Array.prototype.forEach.call(document.querySelectorAll(".nav-btn"), function (b) { b.classList.toggle("active", b.getAttribute("data-view") === name); });
    if (name === "compare") loadScores();
    if (name === "about") loadModelInfo();
  }
  function showMode(mode) {
    state.mode = mode;
    ["text", "url", "pdf"].forEach(function (m) { $("mode-" + m).classList.toggle("hidden", m !== mode); });
    Array.prototype.forEach.call(document.querySelectorAll(".tab"), function (b) { b.classList.toggle("active", b.getAttribute("data-mode") === mode); });
  }

  // ------------------------------------------------------------ compare table
  function loadScores() {
    var cat = $("cat-filter").value;
    fetchJson("/api/scores" + (cat ? "?category=" + encodeURIComponent(cat) : "")).then(function (d) {
      state.scores = d.scores || [];
      if (!cat) {
        var seen = {};
        state.scores.forEach(function (s) { seen[s.category] = true; });
        state.cats = Object.keys(seen).sort();
        rebuildCategoryFilter();
      }
      renderScores();
    }).catch(function () { state.scores = []; renderScores(); });
  }
  function rebuildCategoryFilter() {
    var sel = $("cat-filter"); var cur = sel.value;
    sel.textContent = "";
    var all = el("option", null, t("allCats")); all.value = ""; sel.appendChild(all);
    state.cats.forEach(function (c) { var o = el("option", null, catLabel(c)); o.value = c; sel.appendChild(o); });
    sel.value = cur;
  }
  function renderScores() {
    var body = $("scores-body"); body.textContent = "";
    if (!state.scores.length) {
      var tr = el("tr"); var td = el("td", "muted", t("emptyScores")); td.colSpan = 5; tr.appendChild(td); body.appendChild(tr); return;
    }
    state.scores.forEach(function (s) {
      var tr = el("tr");
      var name = el("td", null, s.app_name);
      if (s.is_sample) name.appendChild(el("span", "sample-tag", t("sampleTag")));
      tr.appendChild(name);
      tr.appendChild(el("td", null, catLabel(s.category)));
      var sc = el("td"); var bar = el("span", "bar"); var fill = el("span", "band-" + s.band); fill.style.width = s.score + "%"; bar.appendChild(fill);
      sc.appendChild(bar); sc.appendChild(document.createTextNode(s.score + " (" + t("band")[s.band] + ")")); tr.appendChild(sc);
      tr.appendChild(el("td", null, s.top_categories.map(function (c) { return c.replace(/_/g, " "); }).join(", ")));
      tr.appendChild(el("td", null, s.analysed_on));
      body.appendChild(tr);
    });
  }

  // ------------------------------------------------------------ about / model info
  function loadModelInfo() {
    fetchJson("/api/model-info").then(function (d) {
      var box = $("model-info"); box.textContent = "";
      var m = d.model || {};
      if (m.macro_f1 !== undefined) {
        box.appendChild(el("p", null, t("f1") + ": " + m.macro_f1));
        if (m.caveat) box.appendChild(el("p", "muted", m.caveat));
      }
    }).catch(function () { /* ignore */ });
  }

  // ------------------------------------------------------------ samples
  function loadSamples() {
    fetchJson("/api/samples").then(function (list) {
      state.samples = list;
      var wrap = $("sample-buttons"); wrap.textContent = "";
      list.forEach(function (s, i) {
        var b = el("button", "chip-btn", (i + 1) + ". " + s.name.replace(" (demo text)", ""));
        b.type = "button";
        b.addEventListener("click", function () { showMode("text"); $("text-input").value = s.text; analyse(s.text); });
        wrap.appendChild(b);
      });
    }).catch(function () { /* samples are optional */ });
  }

  // ------------------------------------------------------------ wire up
  function init() {
    Array.prototype.forEach.call(document.querySelectorAll(".nav-btn"), function (b) { b.addEventListener("click", function () { showView(b.getAttribute("data-view")); }); });
    Array.prototype.forEach.call(document.querySelectorAll(".tab"), function (b) { b.addEventListener("click", function () { showMode(b.getAttribute("data-mode")); }); });
    $("lang-ta").addEventListener("click", function () { state.lang = "ta"; applyStaticText(); renderResult(); renderScores(); rebuildCategoryFilter(); loadModelInfo(); });
    $("lang-en").addEventListener("click", function () { state.lang = "en"; applyStaticText(); renderResult(); renderScores(); rebuildCategoryFilter(); loadModelInfo(); });
    $("analyse-btn").addEventListener("click", function () { analyse(); });
    $("clear-btn").addEventListener("click", function () {
      $("text-input").value = ""; $("url-input").value = ""; $("pdf-input").value = ""; state.pdfFile = null;
      $("pdf-name").textContent = t("phPdf"); state.result = null; renderResult(); setStatus("", "");
    });
    $("pdf-input").addEventListener("change", function (e) {
      var f = e.target.files && e.target.files[0];
      state.pdfFile = f || null;
      $("pdf-name").textContent = f ? f.name : t("phPdf");
    });
    $("cat-filter").addEventListener("change", loadScores);
    applyStaticText();
    loadSamples();
  }

  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", init); } else { init(); }
})();
