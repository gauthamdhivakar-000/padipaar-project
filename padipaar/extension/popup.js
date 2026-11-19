(function () {
  "use strict";
  var DEFAULT_API = "http://127.0.0.1:5000";
  var state = { lang: "ta", api: DEFAULT_API, data: null };

  var T = {
    ta: { scan: "இந்தப் பக்கத்தைச் சோதி", scanning: "பக்கத்தைப் படிக்கிறோம்...", score: "ஆபத்து மதிப்பெண்",
          tip: "என்ன செய்யலாம்", ui: "பக்க வடிவமைப்பு எச்சரிக்கைகள்", find: "கவனிக்க வேண்டிய விதிகள்",
          none: "குறிப்பிடத்தக்க எச்சரிக்கை எதுவும் இல்லை.", full: "முழு அறிக்கையைத் திற",
          band: { Low: "குறைவு", Medium: "நடுத்தரம்", High: "அதிகம்" },
          errRestricted: "இந்தப் பக்கத்தைச் சோதிக்க முடியாது (உலாவியின் சிறப்புப் பக்கம்). வேறொரு பக்கத்தில் முயற்சிக்கவும்.",
          errNet: "சேவையுடன் இணைக்க முடியவில்லை. Settings-ல் முகவரியைச் சரிபார்க்கவும்.",
          errShort: "இந்தப் பக்கத்தில் படிக்கக்கூடிய உரை மிகக் குறைவு.", saved: "சேமிக்கப்பட்டது",
          foot: "தானியங்கிப் பகுப்பாய்வு; சட்ட ஆலோசனை அல்ல. பக்க உரை சேமிக்கப்படாது." },
    en: { scan: "Scan this page", scanning: "Reading the page...", score: "Risk score",
          tip: "What you can do", ui: "Page design warnings", find: "Clauses to watch",
          none: "No notable warning signs.", full: "Open full report",
          band: { Low: "Low", Medium: "Medium", High: "High" },
          errRestricted: "This page cannot be scanned (browser internal page). Try another page.",
          errNet: "Could not reach the service. Check the address in Settings.",
          errShort: "This page has too little readable text.", saved: "Saved",
          foot: "Automated analysis, not legal advice. Page text is not stored." }
  };
  function tr(k) { return T[state.lang][k]; }
  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; }
  function pick(o, base) { return o[base + "_" + state.lang]; }
  function setStatus(msg, isErr) { var s = $("status"); s.textContent = msg || ""; s.className = isErr ? "error" : ""; }

  // Runs INSIDE the web page being scanned (must be self-contained).
  function scanPage() {
    var out = [];
    try {
      var boxes = document.querySelectorAll("input[type=checkbox]");
      for (var i = 0; i < boxes.length; i++) {
        var cb = boxes[i];
        var holder = cb.closest("label") || cb.parentElement || cb;
        var label = (holder.innerText || "").toLowerCase();
        if (cb.defaultChecked && /(newsletter|offers?|marketing|partners?|share|promotional|promotions)/.test(label) && !/remember me/.test(label)) {
          out.push({ type: "pre_ticked_consent", text: label.trim().slice(0, 120) });
          break;
        }
      }
      var body = (document.body && document.body.innerText) || "";
      var urgent = body.match(/(only \d+ (items? |rooms? |seats? )?left|hurry[^.\n]{0,30}|offer (ends|expires)[^.\n]{0,30}|expires in [^.\n]{0,20}|\d+ (people|others|persons) (are )?(viewing|watching|looking))/i);
      if (urgent) out.push({ type: "urgency_pressure", text: urgent[0].trim().slice(0, 120) });
      var fs = function (e) { return parseFloat(getComputedStyle(e).fontSize) || 14; };
      var els = document.querySelectorAll("button, a, input[type=submit]");
      var accept = null, decline = null;
      for (var j = 0; j < els.length; j++) {
        var txt = ((els[j].innerText || els[j].value || "") + "").trim();
        if (!accept && /^(accept|agree|continue|sign up|get started|subscribe|start free trial)/i.test(txt)) accept = els[j];
        if (!decline && /^(no,? thanks|no thank you|skip|decline|not now|maybe later|cancel)/i.test(txt)) decline = els[j];
      }
      if (accept && decline && fs(decline) < fs(accept) * 0.75)
        out.push({ type: "hidden_decline", text: ((decline.innerText || decline.value) + "").trim().slice(0, 60) });
    } catch (e) { /* ignore */ }
    return { text: ((document.body && document.body.innerText) || "").slice(0, 150000), ui: out, title: document.title || "" };
  }

  function storageGet(key) {
    return new Promise(function (resolve) {
      try { chrome.storage.local.get([key], function (r) { resolve(r ? r[key] : undefined); }); } catch (e) { resolve(undefined); }
    });
  }
  function storageSet(key, val) {
    return new Promise(function (resolve) {
      try { var o = {}; o[key] = val; chrome.storage.local.set(o, resolve); } catch (e) { resolve(); }
    });
  }

  function render() {
    var d = state.data, box = $("result");
    $("scan").textContent = tr("scan");
    $("foot").textContent = tr("foot");
    $("lang-ta").className = state.lang === "ta" ? "active" : "";
    $("lang-en").className = state.lang === "en" ? "active" : "";
    if (!d) { box.hidden = true; return; }
    box.hidden = false; box.textContent = "";
    var row = el("div", "score-row");
    var ring = el("div", "ring " + d.band); ring.style.setProperty("--p", String(d.score)); ring.appendChild(el("span", null, String(d.score)));
    row.appendChild(ring);
    var side = el("div");
    side.appendChild(el("span", "pill " + d.band, tr("band")[d.band]));
    side.appendChild(el("div", null, pick(d.summary, "summary")));
    row.appendChild(side); box.appendChild(row);

    if (d.ui_findings && d.ui_findings.length) {
      box.appendChild(el("div", "sec", tr("ui")));
      d.ui_findings.forEach(function (u) {
        var c = el("div", "card ui"); c.appendChild(el("b", null, pick(u, "title"))); c.appendChild(el("div", null, pick(u, "meaning")));
        c.appendChild(el("div", "tip", tr("tip") + ": " + pick(u, "tip"))); box.appendChild(c);
      });
    }
    box.appendChild(el("div", "sec", tr("find")));
    if (!d.findings.length) { box.appendChild(el("div", "hint", tr("none"))); }
    d.findings.slice(0, 5).forEach(function (f) {
      var c = el("div", "card"); c.appendChild(el("b", null, pick(f, "title"))); c.appendChild(el("div", null, pick(f, "meaning")));
      c.appendChild(el("div", "tip", tr("tip") + ": " + pick(f, "tip"))); c.appendChild(el("div", "clause", f.clause)); box.appendChild(c);
    });
    var a = el("a", "more", tr("full")); a.href = state.api; a.target = "_blank"; a.rel = "noopener"; box.appendChild(a);
  }

  function scan() {
    var btn = $("scan"); btn.disabled = true; setStatus(tr("scanning"), false);
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      var tab = tabs && tabs[0];
      if (!tab || tab.id === undefined) { btn.disabled = false; return setStatus(tr("errRestricted"), true); }
      chrome.scripting.executeScript({ target: { tabId: tab.id }, func: scanPage }, function (results) {
        if (chrome.runtime.lastError || !results || !results[0] || !results[0].result) {
          btn.disabled = false; return setStatus(tr("errRestricted"), true);
        }
        var page = results[0].result;
        if (!page.text || page.text.trim().length < 200) { btn.disabled = false; return setStatus(tr("errShort"), true); }
        fetch(state.api.replace(/\/+$/, "") + "/api/analyze", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: page.text, ui_findings: page.ui })
        }).then(function (res) {
          return res.json().catch(function () { return {}; }).then(function (data) {
            if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
            return data;
          });
        }).then(function (data) {
          state.data = data; setStatus("", false); render();
          try {
            chrome.action.setBadgeText({ text: String(data.score), tabId: tab.id });
            chrome.action.setBadgeBackgroundColor({ color: data.band === "High" ? "#d23b3b" : data.band === "Medium" ? "#e19a0b" : "#1f9d55", tabId: tab.id });
          } catch (e) { /* badge is optional */ }
        }).catch(function (err) {
          var m = err && err.message;
          setStatus(!m || m === "Failed to fetch" ? tr("errNet") : m, true);
        }).then(function () { btn.disabled = false; });
      });
    });
  }

  function init() {
    storageGet("api").then(function (v) {
      if (typeof v === "string" && v) state.api = v;
      $("api-url").value = state.api;
    });
    storageGet("lang").then(function (v) { if (v === "ta" || v === "en") { state.lang = v; } render(); });
    $("scan").addEventListener("click", scan);
    $("lang-ta").addEventListener("click", function () { state.lang = "ta"; storageSet("lang", "ta"); render(); });
    $("lang-en").addEventListener("click", function () { state.lang = "en"; storageSet("lang", "en"); render(); });
    $("save-api").addEventListener("click", function () {
      var v = $("api-url").value.trim();
      if (!/^https?:\/\//i.test(v)) return setStatus(tr("errNet"), true);
      state.api = v; storageSet("api", v).then(function () { setStatus(tr("saved"), false); });
    });
    render();
  }
  init();
})();
