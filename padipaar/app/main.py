"""PadiPaar - Flask application (API + static web app)."""
import collections
import hmac
import os
import re
import threading
import time

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

from . import db
from .classifier import analyse_clauses, model_info
from .explainer import band_summary, disclaimer, explain_finding, explain_ui
from .extractor import (MAX_CHARS, InputError, fetch_url_text, pdf_to_text, split_clauses)
from .rules import CATEGORIES
from .samples import SAMPLES
from .scoring import UI_WEIGHTS, compute_score

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB uploads
app.json.ensure_ascii = False

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")
RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MIN", "40"))

# ------------------------------------------------------------------ rate limiting
_hits = collections.defaultdict(collections.deque)
_hits_lock = threading.Lock()


def _client_ip():
    fwd = request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0].strip() if fwd else request.remote_addr) or "unknown"


def _rate_limited():
    now = time.time()
    ip = _client_ip()
    with _hits_lock:
        q = _hits[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return True
        q.append(now)
        if len(_hits) > 5000:  # keep memory bounded
            for k in [k for k, v in _hits.items() if not v or now - v[-1] > 60]:
                _hits.pop(k, None)
    return False


# ------------------------------------------------------------------ core pipeline
def run_pipeline(text, ui_findings=None):
    text = (text or "").strip()
    if not text:
        raise InputError("Please provide some text, a web address or a PDF.")
    if len(text) > MAX_CHARS:
        raise InputError("The document is too long (maximum %d characters)." % MAX_CHARS)
    clauses = split_clauses(text)
    if not clauses:
        raise InputError("No readable clauses were found. Please paste more of the terms text.")

    per_clause = analyse_clauses(clauses)
    explained, flat = [], []
    flagged = 0
    for clause, findings in zip(clauses, per_clause):
        if findings:
            flagged += 1
        for f in findings:
            flat.append(f)
            explained.append(explain_finding(f, clause))

    clean_ui = []
    for u in (ui_findings or [])[:10]:
        if isinstance(u, dict) and u.get("type") in UI_WEIGHTS:
            ex = explain_ui(u)
            if ex:
                clean_ui.append(ex)

    result = compute_score(flat, clean_ui)
    explained.sort(key=lambda x: -x["confidence"])
    by_cat = [{"category": c, "confidence": conf,
               "title_en": explain_finding({"category": c, "confidence": conf, "source": "x"}, "")["title_en"],
               "title_ta": explain_finding({"category": c, "confidence": conf, "source": "x"}, "")["title_ta"]}
              for c, conf in result["by_category"].items()]
    return {
        "score": result["score"], "band": result["band"],
        "doc_score": result["doc_score"], "ui_bonus": result["ui_bonus"],
        "summary": band_summary(result["band"]),
        "clause_count": len(clauses), "flagged_clauses": flagged,
        "categories": by_cat,
        "findings": explained[:25],
        "ui_findings": clean_ui,
        "disclaimer": disclaimer(),
    }


def _json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise InputError("Send a JSON body with either 'text' or 'url'.")
    return data


# ------------------------------------------------------------------ routes
@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/health")
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "padipaar"})


@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return ("", 204)
    if _rate_limited():
        return jsonify({"error": "Too many requests. Please wait a minute and try again."}), 429
    data = _json_body()
    url, text = (data.get("url") or "").strip(), data.get("text")
    if url:
        text = fetch_url_text(url)
    elif not isinstance(text, str) or not text.strip():
        raise InputError("Send either 'text' or 'url'.")
    ui = data.get("ui_findings")
    return jsonify(run_pipeline(text, ui if isinstance(ui, list) else []))


@app.route("/api/analyze/pdf", methods=["POST", "OPTIONS"])
def analyze_pdf():
    if request.method == "OPTIONS":
        return ("", 204)
    if _rate_limited():
        return jsonify({"error": "Too many requests. Please wait a minute and try again."}), 429
    f = request.files.get("file")
    if f is None or not f.filename:
        raise InputError("Please choose a PDF file to upload.")
    data = f.read()
    if not data.startswith(b"%PDF"):
        raise InputError("That file is not a PDF.")
    return jsonify(run_pipeline(pdf_to_text(data), []))


@app.route("/api/samples")
def samples():
    return jsonify([{"slug": s["slug"], "name": s["app_name"], "text": s["text"]} for s in SAMPLES])


@app.route("/api/scores")
def scores():
    return jsonify({"scores": db.list_scores(request.args.get("category") or None),
                    "note": "Automated analysis on the date shown; not legal advice."})


@app.route("/api/scores/<slug>")
def score_one(slug):
    row = db.get_score(slug)
    if not row:
        return jsonify({"error": "Not found."}), 404
    return jsonify(row)


@app.route("/api/model-info")
def info():
    return jsonify({"categories": CATEGORIES, "model": model_info()})


@app.route("/api/admin/scores", methods=["POST"])
def admin_add_score():
    """Add/update an app score. Disabled unless the ADMIN_KEY environment variable is set."""
    if not ADMIN_KEY:
        return jsonify({"error": "Admin endpoint is disabled."}), 403
    if not hmac.compare_digest(request.headers.get("X-Admin-Key", ""), ADMIN_KEY):
        return jsonify({"error": "Forbidden."}), 403
    data = _json_body()
    slug = str(data.get("slug", "")).strip().lower()
    name = str(data.get("app_name", "")).strip()[:80]
    cat = str(data.get("category", "other")).strip().lower()[:30] or "other"
    if not re.fullmatch(r"[a-z0-9-]{2,60}", slug) or not name:
        raise InputError("Provide a valid 'slug' (a-z, 0-9, -) and an 'app_name'.")
    terms_url = (data.get("terms_url") or data.get("url") or "").strip()[:300]
    text = data.get("text") or (fetch_url_text(terms_url) if terms_url else "")
    result = run_pipeline(text, [])
    db.upsert_score(slug, name, cat, terms_url, result)
    return jsonify({"saved": slug, "score": result["score"], "band": result["band"]})


# ------------------------------------------------------------------ hooks / errors
@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Frame-Options"] = "DENY"
    if request.path.startswith("/api/") or request.path == "/health":
        resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGINS
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Admin-Key"
        resp.headers["Cache-Control"] = "no-store"
    else:
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
            "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
    return resp


@app.errorhandler(InputError)
def handle_input_error(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(413)
def too_large(_e):
    return jsonify({"error": "File too large (maximum 8 MB)."}), 413


@app.errorhandler(HTTPException)
def handle_http(e):
    return jsonify({"error": e.description or e.name}), e.code


@app.errorhandler(Exception)
def handle_unexpected(e):
    app.logger.exception("Unexpected error: %s", e)
    return jsonify({"error": "Something went wrong on our side. Please try again."}), 500


# ------------------------------------------------------------------ startup
def _startup():
    db.init_db()
    from .classifier import analyse_clauses as _warm  # loads / trains the model once
    _warm(["warm up"])
    if db.count_scores() == 0:
        for s in SAMPLES:
            res = run_pipeline(s["text"], [])
            db.upsert_score(s["slug"], s["app_name"], s["category"], "", res, is_sample=True)


_startup()
